"""
SKU 维度投词建议引擎 —— 整合类目路由 + 市场调研 + 投词输出

用法:
    advisor = SKUAdvisor(sales_df, ad_df)
    result = advisor.analyze("90409001")
    print(result.to_json())

输出结构化投词方案，可直接用于 eBay 广告投放。
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Optional
import json

from .category_router import (
    get_category_config,
    build_title,
    generate_keyword_list,
    get_item_specifics,
    get_model_keywords,
    resolve_year_range,
)
from .sku_evaluator import SKUEvaluator
from .keyword_optimizer import KeywordOptimizer


@dataclass
class SKUAdvisorResult:
    """SKU 投词建议的完整输出结构"""
    sku: str
    category: str = ""
    product_name: str = ""
    model: str = ""
    model_keywords: list = field(default_factory=list)
    year_range: str = ""
    year_display: str = ""
    color: str = ""
    material: str = ""

    # 投放评估
    priority: str = "未知"
    priority_score: int = 0
    ad_type: str = "PLP(Advanced)按点击测款"
    daily_budget: str = "$3-5/天"

    # 标题
    title_template: str = ""
    title_templates: list = field(default_factory=list)

    # 关键词
    keywords: dict = field(default_factory=dict)
    negative_keywords: list = field(default_factory=list)

    # 竞品
    competitor_insight: str = ""
    competitor_titles: list = field(default_factory=list)

    # 运营
    zk_notes: list = field(default_factory=list)
    market_price_range: str = ""
    weekly_checklist: list = field(default_factory=list)
    item_specifics: dict = field(default_factory=dict)

    # 元数据
    search_queries: list = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_markdown(self) -> str:
        """生成可读的 Markdown 报告"""
        lines = [
            f"# 📊 SKU {self.sku} 投词建议报告",
            "",
            f"| 字段 | 内容 |",
            f"|------|------|",
            f"| SKU | {self.sku} |",
            f"| 类目 | {self.category} |",
            f"| 适配车型 | {self.model} |",
            f"| 年份 | {self.year_display} |",
            f"| 颜色 | {self.color} |",
            f"| 投放优先级 | **{self.priority}** ({self.priority_score}分) |",
            f"| 推荐广告类型 | {self.ad_type} |",
            f"| 建议日预算 | {self.daily_budget} |",
            f"| 参考ZK笔记 | {', '.join(self.zk_notes) if self.zk_notes else '无'} |",
            "",
            "## 🏷️ 推荐标题",
            f"```\n{self.title_template}\n```",
            "",
            "### 备选模板",
        ]
        for i, t in enumerate(self.title_templates[1:4], 1):
            lines.append(f"{i}. `{t}`")

        lines += [
            "",
            "## 🔑 关键词建议",
            "",
            "### Broad Match（广泛匹配）",
        ]
        for kw in self.keywords.get("broad", [])[:8]:
            lines.append(f"- {kw}")

        lines += ["", "### Phrase Match（词组匹配）"]
        for kw in self.keywords.get("phrase", [])[:5]:
            lines.append(f"- {kw}")

        lines += ["", "### Exact Match（精确匹配）"]
        for kw in self.keywords.get("exact", [])[:3]:
            lines.append(f"- {kw}")

        lines += [
            "",
            "### 🚫 否定关键词",
        ]
        for kw in self.negative_keywords[:5]:
            lines.append(f"- {kw}")

        if self.competitor_insight:
            lines += [
                "",
                "## 🔍 竞品洞察",
                self.competitor_insight,
            ]

        if self.competitor_titles:
            lines += [
                "",
                "### 竞品标题参考",
            ]
            for ct in self.competitor_titles[:5]:
                lines.append(f"- `{ct}`")

        lines += [
            "",
            "## 📋 周检查清单",
        ]
        for item in self.weekly_checklist:
            lines.append(f"- [ ] {item}")

        if self.search_queries:
            lines += [
                "",
                "## 🔎 建议搜索词（用于市场调研）",
            ]
            for q in self.search_queries[:5]:
                lines.append(f"- `{q}`")

        return "\n".join(lines)


class SKUAdvisor:
    """SKU 维度投词建议引擎。

    整合:
      1. 销售数据 → SKU 评价 + 潜力预判
      2. 类目路由 → ZK知识库 → 标题模板 + 关键词词库
      3. 市场搜索词生成
    """

    def __init__(self, sales_df: pd.DataFrame = None, ad_df: pd.DataFrame = None):
        self.sales_df = sales_df
        self.ad_df = ad_df
        self.sku_evaluator = SKUEvaluator(sales_df) if sales_df is not None else None
        self.keyword_optimizer = KeywordOptimizer(ad_df) if ad_df is not None else None

        # 缓存
        self._sku_info_cache: dict = {}
        self._evaluated = False

    def _ensure_evaluated(self):
        """确保 SKU 评分和关键词优化已执行。"""
        if self._evaluated:
            return
        if self.sku_evaluator and self.sku_evaluator.evaluated_df is None:
            self.sku_evaluator.evaluate_all()
        if self.keyword_optimizer and self.keyword_optimizer.optimized_df is None:
            self.keyword_optimizer.optimize()
        self._evaluated = True

    def load_sku_info_from_sales(self, sku: str) -> dict:
        """从销售数据中读取 SKU 的基本信息。"""
        if self.sales_df is None:
            return {}

        match = self.sales_df[self.sales_df['SKU'].astype(str) == str(sku)]
        if len(match) == 0:
            return {}

        row = match.iloc[0]
        return {
            "sku": sku,
            "category": str(row.get("三级目录", "")),
            "brand": str(row.get("适配品牌", "")).replace("nan", ""),
            "model": str(row.get("适配车型", "")).replace("nan", ""),
            "year": str(row.get("适配年份", "")).replace("nan", ""),
            "product_name": str(row.get("产品名称", "")).replace("nan", ""),
            "color": str(row.get("颜色", "")).replace("nan", ""),
            "material": str(row.get("材质", "")).replace("nan", ""),
            "sales_15d": int(row.get("15天销量", 0)) if pd.notna(row.get("15天销量", 0)) else 0,
            "sales_30d": int(row.get("30天销量", 0)) if pd.notna(row.get("30天销量", 0)) else 0,
            "revenue_15d": float(row.get("15天销售额", 0)) if pd.notna(row.get("15天销售额", 0)) else 0.0,
            "ad_orders_15d": int(row.get("15广告订单(光环）", 0)) if pd.notna(row.get("15广告订单(光环）", 0)) else 0,
            "ad_cost_15d": float(row.get("15总广告费", 0)) if pd.notna(row.get("15总广告费", 0)) else 0.0,
            "growth_rate": str(row.get("销量环比", "")),
        }

    def get_sku_priority(self, sku: str) -> tuple:
        """获取 SKU 的投放优先级和评分。"""
        self._ensure_evaluated()
        if self.sku_evaluator and self.sku_evaluator.evaluated_df is not None:
            match = self.sku_evaluator.evaluated_df[
                self.sku_evaluator.evaluated_df['SKU'].astype(str) == str(sku)
            ]
            if len(match) > 0:
                row = match.iloc[0]
                priority = str(row.get("投放优先级", "E"))
                score = int(row.get("投放评分", 0))
                ad_type = str(row.get("推荐广告类型", ""))
                return priority, score, ad_type
        return "E", 0, "PLP(Advanced)按点击测款"

    def get_existing_keywords(self, sku: str) -> pd.DataFrame:
        """获取 SKU 当前在投的高效关键词。"""
        self._ensure_evaluated()
        if self.keyword_optimizer and self.keyword_optimizer.optimized_df is not None:
            result = self.keyword_optimizer.recommend_for_sku(
                sku,
                ad_df=self.ad_df,
                sku_evaluator=self.sku_evaluator,
                sales_df=self.sales_df,
            )
            recs = result.get("recommended", [])
            if recs:
                return pd.DataFrame(recs)
        return pd.DataFrame()

    def generate_search_queries(self, sku_info: dict) -> list[str]:
        """生成用于市场调研的搜索词列表。"""
        queries = []
        category = sku_info.get("category", "")
        model = sku_info.get("model", "")
        brand = sku_info.get("brand", "Harley")
        year = sku_info.get("year", "")
        year_short = resolve_year_range(year) if year else ""

        config = get_category_config(category)
        product_keywords = config.get("core_keywords", {}).get("product_type", []) if config else []
        model_keywords = get_model_keywords(model)

        for pk in product_keywords[:3]:
            for mk in model_keywords[:2]:
                q = f"ebay {brand} {pk} {mk} {year_short}".strip()
                queries.append(q)

        # 加上外观词
        if config:
            attrs = config.get("core_keywords", {}).get("attributes", [])
            for attr in attrs[:2]:
                queries.append(f"ebay {brand} {product_keywords[0]} {attr}".strip())

        return list(dict.fromkeys(queries))[:6]  # 去重取前6

    def analyze(self, sku: str, sku_info_override: dict = None) -> SKUAdvisorResult:
        """对指定 SKU 执行完整分析，输出投词建议。

        Args:
            sku: SKU 编号
            sku_info_override: 手动覆盖 SKU 信息（用于飞书等外部数据源）

        Returns:
            SKUAdvisorResult: 完整投词方案
        """
        # 1. 获取 SKU 信息
        if sku_info_override:
            sku_info = sku_info_override
        else:
            sku_info = self.load_sku_info_from_sales(sku)

        if not sku_info:
            # 没有销售数据，返回空结果提示需要手动输入
            return SKUAdvisorResult(
                sku=sku,
                category="未知",
                competitor_insight="SKU不在销售数据中。请提供类目、车型、年份等基本信息。",
            )

        sku_info.setdefault("category", "")
        sku_info.setdefault("brand", "Harley")
        sku_info.setdefault("model", "")
        sku_info.setdefault("year", "")
        sku_info.setdefault("color", "")
        sku_info.setdefault("material", "")
        sku_info.setdefault("sku", sku)

        # 2. 类目路由
        config = get_category_config(sku_info.get("category", ""))
        zk_notes = config.get("zk_notes", []) if config else []

        # 3. 生成标题
        title = build_title(sku_info)
        templates = config.get("templates", []) if config else []

        # 4. 生成关键词
        keywords = generate_keyword_list(sku_info)

        # 5. 获取优先级
        priority, score, ad_type = self.get_sku_priority(sku)

        # 6. 日预算
        budget_map = {
            "A": "$8-12/天", "B": "$5-8/天", "C": "$3-5/天",
            "D": "$1-3/天", "E": "$1-2/天",
        }
        daily_budget = budget_map.get(priority, "$1-3/天")

        # 7. 搜索词
        search_queries = self.generate_search_queries(sku_info)

        # 8. 竞品洞察（从 ZK 笔记继承）
        competitor_insight = config.get("competitor_insight", "") if config else ""

        # 9. 周检查清单
        weekly_checklist = [
            f"ACoS是否<30%（目标：<25%）",
            f"CTR是否>0.5%（目标：>1%）",
            f"曝光量是否>500/周",
        ]
        if keywords.get("broad"):
            top_kw = keywords["broad"][0]
            weekly_checklist.append(f"核心词「{top_kw}」是否有搜索量")
        if sku_info.get("color"):
            weekly_checklist.append(f"颜色词「{sku_info['color']}」是否有独立搜索入口")

        # 10. Item Specifics
        item_specifics = get_item_specifics(sku_info.get("category", ""))

        # 11. 年份处理
        year = sku_info.get("year", "")
        year_short = resolve_year_range(year)

        return SKUAdvisorResult(
            sku=sku,
            category=sku_info.get("category", ""),
            product_name=sku_info.get("product_name", ""),
            model=sku_info.get("model", ""),
            model_keywords=get_model_keywords(sku_info.get("model", "")),
            year_range=year_short,
            year_display=year,
            color=sku_info.get("color", ""),
            material=sku_info.get("material", ""),
            priority=priority,
            priority_score=score,
            ad_type=ad_type,
            daily_budget=daily_budget,
            title_template=title,
            title_templates=templates if templates else [],
            keywords=keywords,
            negative_keywords=config.get("negative_keywords", []) if config else [],
            competitor_insight=competitor_insight,
            zk_notes=zk_notes,
            item_specifics=item_specifics,
            search_queries=search_queries,
            weekly_checklist=weekly_checklist,
        )


# ── CLI 入口 ──
if __name__ == "__main__":
    import os

    sales_file = "广告源数据/EBAY半月销售监测.xlsx"
    ad_file = "广告源数据/CPC Download 20260701063134.xlsx"

    advisor = SKUAdvisor()
    if os.path.exists(sales_file):
        advisor.sales_df = pd.read_excel(sales_file)
        advisor.sku_evaluator = SKUEvaluator(advisor.sales_df)
    if os.path.exists(ad_file):
        from .data_loader import load_ad_data
        advisor.ad_df = load_ad_data(ad_file)
        advisor.keyword_optimizer = KeywordOptimizer(advisor.ad_df)

    # 测试 SKU
    test_skus = ["90409001", "90107051", "90201129"]

    for sku in test_skus:
        print(f"\n{'='*70}")
        result = advisor.analyze(sku)
        print(result.to_markdown())
