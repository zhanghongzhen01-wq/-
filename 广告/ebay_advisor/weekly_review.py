"""
周迭代引擎 —— 对比投词计划 vs 实际表现，输出迭代方案

用法:
    reviewer = WeeklyReviewer(ad_df_new)
    report = reviewer.review(last_week_plan, sku)
    print(report.to_markdown())
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional

from .keyword_optimizer import KeywordOptimizer
from .sku_advisor import SKUAdvisorResult


@dataclass
class KeywordIteration:
    """单个关键词的迭代建议"""
    keyword: str
    match_type: str = ""
    planned_action: str = ""       # 上周建议
    actual_impressions: int = 0
    actual_clicks: int = 0
    actual_sales: int = 0
    actual_acos: float = 0.0
    actual_spend: float = 0.0
    actual_roas: float = 0.0
    verdict: str = ""              # 保留/追加/降价/关停/数据不足
    new_bid: str = ""
    reason: str = ""


@dataclass
class WeeklyReviewResult:
    """周迭代报告"""
    sku: str
    review_date: str = ""
    plan_date: str = ""
    summary: str = ""

    # 整体指标
    total_impressions: int = 0
    total_clicks: int = 0
    total_sales: int = 0
    total_spend: float = 0.0
    total_revenue: float = 0.0
    overall_acos: float = 0.0
    overall_roas: float = 0.0

    # 分类
    keywords_keep: list = field(default_factory=list)      # 保留/追加
    keywords_reduce: list = field(default_factory=list)    # 降价
    keywords_pause: list = field(default_factory=list)     # 关停
    keywords_new: list = field(default_factory=list)       # 新增建议
    keywords_insufficient: list = field(default_factory=list)  # 数据不足

    # 迭代记录
    iterations: list = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"# 🔄 SKU {self.sku} 周迭代报告",
            f"",
            f"| 字段 | 内容 |",
            f"|------|------|",
            f"| SKU | {self.sku} |",
            f"| 计划日期 | {self.plan_date} |",
            f"| 复盘日期 | {self.review_date} |",
            f"",
            f"## 📊 本周数据总览",
            f"",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 总曝光 | {self.total_impressions:,} |",
            f"| 总点击 | {self.total_clicks:,} |",
            f"| 总销量 | {self.total_sales} |",
            f"| 总花费 | ${self.total_spend:.2f} |",
            f"| 总营收 | ${self.total_revenue:.2f} |",
            f"| 整体 ACoS | {self.overall_acos:.1%} |",
            f"| 整体 ROAS | {self.overall_roas:.1f}x |",
            f"",
            f"## ✅ 保留/追加预算（{len(self.keywords_keep)}个）",
        ]
        for kw in self.keywords_keep:
            lines.append(f"- **{kw.get('keyword','?')}** — {kw.get('reason','')} | ACoS={kw.get('acos',0):.0%} | 建议出价 {kw.get('new_bid','保持')}")
        if not self.keywords_keep:
            lines.append("- 无")

        lines += [
            f"",
            f"## ⚠️ 降价优化（{len(self.keywords_reduce)}个）",
        ]
        for kw in self.keywords_reduce:
            lines.append(f"- **{kw.get('keyword','?')}** — {kw.get('reason','')} | ACoS={kw.get('acos',0):.0%} | 建议出价 {kw.get('new_bid','?')}")
        if not self.keywords_reduce:
            lines.append("- 无")

        lines += [
            f"",
            f"## 🛑 建议关停（{len(self.keywords_pause)}个）",
        ]
        for kw in self.keywords_pause:
            lines.append(f"- **{kw.get('keyword','?')}** — {kw.get('reason','')} | 花费=${kw.get('spend',0):.2f} | 销量={kw.get('sales',0)}")
        if not self.keywords_pause:
            lines.append("- 无")

        lines += [
            f"",
            f"## 🆕 新增尝试（{len(self.keywords_new)}个）",
        ]
        for kw in self.keywords_new:
            lines.append(f"- **{kw.get('keyword','?')}** — {kw.get('reason','')} | 建议出价 {kw.get('bid','?')}")
        if not self.keywords_new:
            lines.append("- 无")

        lines += [
            f"",
            f"## ⏳ 数据不足继续观察（{len(self.keywords_insufficient)}个）",
        ]
        for kw in self.keywords_insufficient:
            lines.append(f"- **{kw.get('keyword','?')}** — {kw.get('reason','')}")
        if not self.keywords_insufficient:
            lines.append("- 无")

        lines += [
            f"",
            f"## 📝 本周总结",
            f"",
            self.summary,
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return asdict(self)


class WeeklyReviewer:
    """周迭代审查器。

    输入：
      - 上周投词计划（SKUAdvisorResult 的 JSON 或 dict）
      - 本周最新 CPC 数据（Excel 文件路径或 DataFrame）

    输出：
      - WeeklyReviewResult（分类：保留/降价/关停/新增/观察）
    """

    def __init__(self, ad_df: pd.DataFrame = None):
        self.ad_df = ad_df
        self.keyword_optimizer = KeywordOptimizer(ad_df) if ad_df is not None else None

    def load_plan(self, plan_path: str) -> dict:
        """加载上周投词计划（JSON 文件）。"""
        with open(plan_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_plan(self, plan: dict, output_dir: str = ".") -> str:
        """保存本周投词计划，供下周复盘使用。"""
        os.makedirs(output_dir, exist_ok=True)
        sku = plan.get("sku", "unknown")
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"ad_plan_{sku}_{date_str}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        return filepath

    def _match_keyword_in_cpc(self, keyword: str, cpc_df: pd.DataFrame) -> Optional[pd.Series]:
        """在 CPC 数据中查找匹配的关键词行。"""
        if cpc_df is None or len(cpc_df) == 0:
            return None

        # 精确匹配
        match = cpc_df[cpc_df['Keyword'].astype(str).str.strip() == keyword.strip()]
        if len(match) > 0:
            return match.iloc[0]

        # 模糊匹配（关键词包含）- regex=False 避免特殊字符报错
        match = cpc_df[cpc_df['Keyword'].astype(str).str.contains(keyword.strip(), case=False, na=False, regex=False)]
        if len(match) > 0:
            return match.iloc[0]

        return None

    def _sf(self, v, default=0.0):
        """安全转浮点数。"""
        try:
            if pd.isna(v):
                return default
            return float(v)
        except:
            return default

    def review(self, last_week_plan: dict, sku: str, cpc_df: pd.DataFrame = None) -> WeeklyReviewResult:
        """执行周迭代审查。

        Args:
            last_week_plan: 上周的 SKUAdvisorResult dict
            sku: SKU 编号
            cpc_df: 最新的 CPC 关键词数据（如不传则用初始化时的 ad_df）

        Returns:
            WeeklyReviewResult
        """
        if cpc_df is not None:
            self.ad_df = cpc_df
            self.keyword_optimizer = KeywordOptimizer(cpc_df)
            self.keyword_optimizer.optimize()

        if self.keyword_optimizer is None:
            raise ValueError("需要提供 CPC 数据")

        result = WeeklyReviewResult(
            sku=sku,
            review_date=datetime.now().strftime("%Y-%m-%d"),
            plan_date=last_week_plan.get("plan_date", "未知"),
        )

        # 获取所有关键词的表现
        all_kw = []
        plan_keywords = []

        # 从计划中提取关键词列表
        kw_dict = last_week_plan.get("keywords", {})
        for level in ["broad", "phrase", "exact"]:
            for kw in kw_dict.get(level, []):
                plan_keywords.append({"keyword": kw, "match_type": level})

        if not plan_keywords:
            result.summary = "上周投词计划中无关键词，请先执行 SKUAdvisor.analyze()"
            return result

        # 对每个计划关键词，在 CPC 数据中查找实际表现
        iterations = []
        total_impressions = 0
        total_clicks = 0
        total_sales = 0
        total_spend = 0.0
        total_revenue = 0.0

        for pk in plan_keywords:
            kw = pk["keyword"]
            mt = pk.get("match_type", "broad")

            row = self._match_keyword_in_cpc(kw, self.ad_df)

            if row is None:
                iterations.append(KeywordIteration(
                    keyword=kw, match_type=mt,
                    verdict="数据不足", reason="CPC报表中未找到此关键词"
                ))
                continue

            impressions = int(self._sf(row.get("Impressions")))
            clicks = int(self._sf(row.get("Clicks")))
            sales = int(self._sf(row.get("Sales")))
            acos = self._sf(row.get("ACOS"))
            roas = self._sf(row.get("ROAS"))
            spend = self._sf(row.get("Ad Fees"))
            revenue = self._sf(row.get("Sale amount"))
            status = str(row.get("Status", "")).upper().strip()

            total_impressions += impressions
            total_clicks += clicks
            total_sales += sales
            total_spend += spend
            total_revenue += revenue

            # 决策树（与 keyword_optimizer 保持一致）
            verdict, reason, new_bid = self._decide(impressions, clicks, sales, acos, roas, spend, status)

            iterations.append(KeywordIteration(
                keyword=kw,
                match_type=mt,
                actual_impressions=impressions,
                actual_clicks=clicks,
                actual_sales=sales,
                actual_acos=acos,
                actual_spend=spend,
                actual_roas=roas,
                verdict=verdict,
                new_bid=new_bid,
                reason=reason,
            ))

        # 分类
        for it in iterations:
            entry = {
                "keyword": it.keyword,
                "match_type": it.match_type,
                "impressions": it.actual_impressions,
                "clicks": it.actual_clicks,
                "sales": it.actual_sales,
                "acos": it.actual_acos,
                "spend": it.actual_spend,
                "roas": it.actual_roas,
                "reason": it.reason,
                "new_bid": it.new_bid,
            }
            if it.verdict in ("追加预算", "保持"):
                result.keywords_keep.append(entry)
            elif it.verdict in ("降价优化",):
                result.keywords_reduce.append(entry)
            elif it.verdict in ("空烧关停", "建议关停"):
                result.keywords_pause.append(entry)
            else:
                result.keywords_insufficient.append(entry)

        # 新增建议：从同 Campaign 的高效词中推荐
        campaign_words = self._find_new_opportunities(last_week_plan, iterations)
        result.keywords_new = campaign_words

        # 汇总
        result.total_impressions = total_impressions
        result.total_clicks = total_clicks
        result.total_sales = total_sales
        result.total_spend = total_spend
        result.total_revenue = total_revenue
        result.overall_acos = total_spend / total_revenue if total_revenue > 0 else 0
        result.overall_roas = total_revenue / total_spend if total_spend > 0 else 0
        result.iterations = [asdict(it) for it in iterations]

        # 生成总结
        result.summary = self._generate_summary(result)

        return result

    def _decide(self, impressions, clicks, sales, acos, roas, spend, status) -> tuple:
        """单个关键词的决策逻辑。返回 (verdict, reason, new_bid)。"""
        # 已暂停
        if status == "PAUSED":
            if sales > 0 and roas > 3:
                return "保持", "暂停前有转化且ROAS优秀，建议以原出价70%重启", ""
            return "建议关停", "已暂停且无足够恢复数据", ""

        # 数据不足
        if impressions < 100:
            return "数据不足", f"仅{impressions}次曝光，继续观察1周", ""
        if clicks == 0:
            return "数据不足", f"{impressions}次曝光零点击，提高出价或优化关键词", "+20%"
        if clicks < 15 and sales == 0:
            return "数据不足", f"仅{clicks}次点击，样本不足继续观察", ""

        # 有关停风险的
        if sales == 0:
            if clicks >= 15 and spend >= 3:
                return "空烧关停", f"{clicks}次点击零转化，花费${spend:.2f}，建议暂停", "暂停"
            if clicks >= 15 and spend < 3:
                return "数据不足", f"{clicks}次点击零转化但花费低(${spend:.2f})，优化listing后再观察", ""

        # 有转化 → 按 ACoS 决策
        if sales > 0 and acos > 0:
            if acos <= 0.15:
                return "追加预算", f"ACoS仅{acos:.0%}，ROAS={roas:.1f}x，建议加预算20-30%", "+25%"
            elif acos <= 0.30:
                return "保持", f"ACoS={acos:.0%}健康，维持当前策略", "保持"
            elif acos <= 0.60:
                return "降价优化", f"ACoS={acos:.0%}偏高，降价15-25%", "-20%"
            elif acos <= 1.00:
                return "降价优化", f"ACoS={acos:.0%}过高，降价25-30%或暂停", "-25%"
            else:
                return "空烧关停", f"ACoS={acos:.0%}越投越亏，建议暂停", "暂停"

        return "保持", "表现稳定", "保持"

    def _find_new_opportunities(self, plan: dict, existing_iterations: list) -> list:
        """从同类 Campaign 中挖掘新的高潜力关键词。"""
        if self.keyword_optimizer is None:
            return []

        category = plan.get("category", "")
        model = plan.get("model", "")

        # 获取追加预算 + 保持的高效词
        expand = self.keyword_optimizer.get_expand_list()
        if len(expand) == 0:
            return []

        # 过滤已投的词
        existing_kw = {it.keyword.lower().strip() for it in existing_iterations}

        new_ops = []
        for _, row in expand.head(5).iterrows():
            kw = str(row.get("Keyword", "")).strip()
            if kw.lower() in existing_kw:
                continue
            acos = self._sf(row.get("ACOS"))
            sales = int(self._sf(row.get("Sales")))
            bid = str(row.get("My bid", "0.30 USD"))

            new_ops.append({
                "keyword": kw,
                "reason": f"同类目高效词(销量{sales}, ACoS{acos:.0%})，建议新增测试",
                "bid": bid,
                "acos": acos,
                "sales": sales,
            })

        return new_ops

    def _generate_summary(self, result: WeeklyReviewResult) -> str:
        """生成可读的周迭代总结。"""
        parts = []

        # 整体表现
        if result.overall_acos > 0:
            if result.overall_acos <= 0.30:
                parts.append(f"✅ 整体 ACoS {result.overall_acos:.0%}，在健康区间内。")
            elif result.overall_acos <= 0.60:
                parts.append(f"⚠️ 整体 ACoS {result.overall_acos:.0%}，偏高需优化。")
            else:
                parts.append(f"🔴 整体 ACoS {result.overall_acos:.0%}，严重偏离，需立即调整。")

        parts.append(f"总曝光 {result.total_impressions:,}，总点击 {result.total_clicks:,}，总销量 {result.total_sales} 单。")

        # 关键词分类统计
        n_keep = len(result.keywords_keep)
        n_reduce = len(result.keywords_reduce)
        n_pause = len(result.keywords_pause)
        n_new = len(result.keywords_new)
        n_insuf = len(result.keywords_insufficient)

        parts.append(f"保留 {n_keep} 个词、降价 {n_reduce} 个、关停 {n_pause} 个、新增 {n_new} 个、数据不足 {n_insuf} 个。")

        # 行动建议
        if n_pause > 0:
            paused_kw = [k["keyword"] for k in result.keywords_pause[:3]]
            parts.append(f"建议本周关停：{', '.join(paused_kw)}。")

        if n_reduce > 0:
            parts.append(f"建议降价 {n_reduce} 个词，1周后再复查。")

        if n_keep > 0:
            keep_kw = result.keywords_keep[0]["keyword"] if result.keywords_keep else ""
            parts.append(f"核心词「{keep_kw}」表现好，建议追加预算。")

        if n_insuf > 0:
            parts.append(f"{n_insuf} 个词数据不足（新品/低曝光），继续观察1周。")

        return " ".join(parts)


# ── CLI 测试入口 ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")

    from data_loader import load_ad_data

    # 模拟上周计划
    last_week = {
        "sku": "90409001",
        "plan_date": "2026-06-26",
        "category": "脚踏",
        "model": "Touring",
        "keywords": {
            "broad": [
                "harley floorboards touring 14-26",
                "harley diamond floorboard kit",
                "touring footpegs shifter brake combo",
            ],
            "phrase": [
                "harley touring floorboards kit",
                "diamond anodized floorboard harley",
            ],
            "exact": [
                "[harley touring diamond floorboards kit 14-26]",
            ],
            "negative": ["OEM", "stock", "original", "sportster"],
        },
    }

    # 加载最新 CPC 数据
    ad_file = "广告源数据/CPC Download 20260701063134.xlsx"
    if os.path.exists(ad_file):
        ad_df = load_ad_data(ad_file)
        reviewer = WeeklyReviewer(ad_df)
        report = reviewer.review(last_week, "90409001")
        print(report.to_markdown())

        # 保存计划供下周使用
        plan_file = reviewer.save_plan(last_week, output_dir=".")
        print(f"\n计划已保存: {plan_file}")
    else:
        print("CPC数据文件不存在，跳过测试")
