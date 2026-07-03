"""
本地产品信息加载器 —— 从 Excel/CSV/JSON/TXT 读取 SKU 信息

用法:
    loader = ProductLoader("产品信息.xlsx")
    loader = ProductLoader("90409001 描述.txt")
    info = loader.get_sku("90409001")
    # → {sku, category, brand, model, year, color, material, ...}

支持格式:
  - Excel (.xlsx/.xls) — 一行一个 SKU
  - CSV (.csv) — 同上
  - TXT (.txt) — SKU 描述文件（如 "90409001 描述.txt"）
  - JSON (.json) — {"skus": [{"sku": ..., "category": ..., ...}, ...]}
  - 直接 dict — 手动传入
"""

import pandas as pd
import json
import os
import re
from typing import Optional


# ── 类目推断规则：产品名关键词 → 类目 ──
CATEGORY_PATTERNS = [
    (["floorboard", "footboard", "foot peg", "footpeg", "floor board"], "脚踏"),
    (["handlebar", "handle bar", "ape hanger", "meathook", "bagger bar"], "手把"),
    (["cable kit", "cable set", "throttle cable", "idle cable", "clutch cable", "brake line"], "拉线总成"),
    (["extension wire", "hand control", "wire harness", "tbw extension"], "手把延长线"),
    (["crash bar", "engine guard", "highway bar", "saddlebag guard", "frame slider"], "护杠"),
    (["mirror", "rear view"], "后视镜"),
    (["headlight", "head light", "daymaker", "led light", "passing lamp"], "LED大灯"),
    (["bushing", "riser bushing"], "衬套"),
    (["triple tree", "triple clamp", "fork clamp"], "三星"),
    (["shifter", "shift lever", "brake pedal", "brake lever", "shift linkage"], "脚踏"),
    (["throttle", "idle cable"], "拉线油门"),
    (["saddlebag guard", "highway footrest", "bar foot peg"], "鞍袋护杠"),
    (["handlebar", "cable", "combo"], "手把组合"),
]


def infer_category(product_name: str, description: str = "") -> str:
    """从产品名称推断类目。"""
    text = f"{product_name} {description}".lower()
    for patterns, category in CATEGORY_PATTERNS:
        for pat in patterns:
            if pat in text:
                return category
    return ""


class ProductLoader:
    """从本地文件加载 SKU 产品信息。

    文件应包含以下列（中文/英文均可）:
      - SKU / sku
      - 类目 / 三级目录 / category
      - 适配品牌 / brand
      - 适配车型 / model
      - 适配年份 / year
      - 颜色 / color
      - 材质 / material
      - 产品名称 / product_name
    """

    # 列名映射（中→英）
    COLUMN_MAP = {
        "SKU": "sku",
        "sku": "sku",
        "三级目录": "category",
        "类目": "category",
        "category": "category",
        "适配品牌": "brand",
        "brand": "brand",
        "品牌": "brand",
        "适配车型": "model",
        "model": "model",
        "车型": "model",
        "适配年份": "year",
        "year": "year",
        "年份": "year",
        "颜色": "color",
        "color": "color",
        "材质": "material",
        "material": "material",
        "产品名称": "product_name",
        "product_name": "product_name",
        "名称": "product_name",
        "name": "product_name",
    }

    def __init__(self, source=None):
        """
        Args:
            source: 文件路径、dict、或 None（后续手动 set_data）
        """
        self.df = None
        self.data = {}
        if source is not None:
            self.load(source)

    def load(self, source):
        """加载数据源。

        Args:
            source: str (文件路径) / dict (直接数据) / pd.DataFrame
        """
        if isinstance(source, str):
            self._load_file(source)
        elif isinstance(source, dict):
            self._load_dict(source)
        elif isinstance(source, pd.DataFrame):
            self.df = source
            self._normalize_columns()
        else:
            raise ValueError(f"不支持的数据源类型: {type(source)}")

    def _load_file(self, filepath: str):
        """从文件加载。"""
        ext = os.path.splitext(filepath)[1].lower()
        if ext in (".xlsx", ".xls"):
            self.df = pd.read_excel(filepath)
            self._normalize_columns()
        elif ext == ".csv":
            self.df = pd.read_csv(filepath)
            self._normalize_columns()
        elif ext == ".txt":
            self._load_txt(filepath)
        elif ext == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._load_dict(data)
            return
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

        if self.df is not None:
            print(f"已加载 {len(self.df)} 个 SKU 的产品信息")

    def _load_dict(self, data: dict):
        """从 dict 加载。"""
        # {"sku": {...}} 格式
        if any(k.isdigit() or "-" in k for k in data.keys()):
            self.data = data
        # {"skus": [...]} 格式
        elif "skus" in data:
            records = data["skus"]
            self.df = pd.DataFrame(records)
            self._normalize_columns()
        # 直接是 SKU 信息 dict
        else:
            self.data = {"_single": data}

    def _load_txt(self, filepath: str):
        """从 TXT 描述文件解析 SKU 信息。

        支持的格式（如 "90409001 描述.txt"）:
            90409001 描述

            Fitment:
            Compatible with Harley Davidson Touring 2014-2026 ...

            Specifications
            Item：Diamond Armor Floorboards Kit
            Material：6061 ALuminum
            Color：Black and Gold
            Process: Two-color anodizing
            ...
        """
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        records = []
        # 按 "SKU 描述" 分隔多个 SKU（一个文件可能有多个）
        # 通常一个文件只有一个 SKU
        sku_match = re.search(r"(\d{6,10})\s*描述", text)
        sku = sku_match.group(1) if sku_match else os.path.basename(filepath).split()[0]

        info = {"sku": sku}

        # 提取 Item / 产品名
        item_match = re.search(r"Item[：:]\s*(.+?)(?:\n|$)", text)
        if item_match:
            info["product_name"] = item_match.group(1).strip()

        # 提取 Material
        mat_match = re.search(r"Material[：:]\s*(.+?)(?:\n|$)", text)
        if mat_match:
            info["material"] = mat_match.group(1).strip()

        # 提取 Color
        color_match = re.search(r"Color[：:]\s*(.+?)(?:\n|$)", text)
        if color_match:
            info["color"] = color_match.group(1).strip()

        # 提取品牌（从 "Compatible with Harley Davidson" 等）
        brand_match = re.search(r"Compatible with (Harley[-\s]?Davidson|Harley|Indian|Kawasaki|Honda|Yamaha|BMW|Ducati|Triumph|Victory)", text, re.IGNORECASE)
        if brand_match:
            brand = brand_match.group(1).strip()
            brand = brand.replace("Harley Davidson", "Harley").replace("Harley-Davidson", "Harley")
            info["brand"] = brand
        else:
            info["brand"] = "Harley"  # 默认哈雷

        # 提取车型和年份
        model_patterns = [
            (r"Compatible with Harley\s*(?:Davidson)?\s*(Touring)\s*(\d{4}\s*[-–]\s*\d{4})", "Touring"),
            (r"Compatible with Harley\s*(?:Davidson)?\s*(Softail)\s*(?:FL\s*)?(\d{4}\s*[-–]\s*\d{4})", "Softail"),
            (r"Compatible with Harley\s*(?:Davidson)?\s*(Dyna)\s*(\d{4}\s*[-–]\s*\d{4})", "Dyna"),
            (r"Compatible with Harley\s*(?:Davidson)?\s*(Sportster)\s*(\d{4}\s*[-–]\s*\d{4})", "Sportster"),
            (r"Fits Harley\s*(?:Davidson)?\s*(Touring)\s*(\d{4}\s*[-–]\s*\d{4})", "Touring"),
            (r"Fits Harley\s*(?:Davidson)?\s*(Softail)\s*(?:FL\s*)?(\d{4}\s*[-–]\s*\d{4})", "Softail"),
            (r"Fits Harley\s*(?:Davidson)?\s*(Dyna)\s*(\d{4}\s*[-–]\s*\d{4})", "Dyna"),
        ]
        for pattern, model_name in model_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                info["model"] = model_name
                year_raw = m.group(2).strip().replace("–", "-").replace(" ", "")
                # 提取年份简写
                years = re.findall(r"\d{4}", year_raw)
                if len(years) >= 2:
                    info["year"] = f"{years[0]}-{years[-1]}"
                elif len(years) == 1:
                    info["year"] = f"{years[0]}-Up"
                else:
                    info["year"] = year_raw
                break

        # 如果没匹配到具体车型，尝试从整个文本找
        if "model" not in info:
            # 找 "Compatible with ... Touring ..." 等
            for kw in ["Touring", "Softail", "Dyna", "Sportster", "Road Glide", "Street Glide"]:
                if kw.lower() in text.lower():
                    info["model"] = kw
                    break

        # 提取年份
        if "year" not in info:
            year_search = re.search(r"(?:Compatible with|Fits).*?(\d{4})\s*[-–]\s*(\d{4}|\w+)", text)
            if year_search:
                info["year"] = f"{year_search.group(1)}-{year_search.group(2)}"
            else:
                year_search = re.search(r"(\d{4})\s*[-–]\s*(?:later|up|newer)", text, re.IGNORECASE)
                if year_search:
                    info["year"] = f"{year_search.group(1)}-Up"

        # 推断类目
        product_name = info.get("product_name", "")
        category = infer_category(product_name, text)
        if category:
            info["category"] = category

        records.append(info)
        self.df = pd.DataFrame(records)
        print(f"从 TXT 解析 SKU: {sku} | 类目: {category or '未知'} | 车型: {info.get('model', '?')} | 年份: {info.get('year', '?')}")

    def _normalize_columns(self):
        """统一列名。"""
        if self.df is None:
            return
        rename = {}
        for col in self.df.columns:
            if col in self.COLUMN_MAP:
                rename[col] = self.COLUMN_MAP[col]
        self.df = self.df.rename(columns=rename)

    def get_sku(self, sku: str) -> Optional[dict]:
        """获取指定 SKU 的产品信息。

        Returns:
            dict: {sku, category, brand, model, year, color, material, product_name}
                 如果 SKU 不存在返回 None
        """
        # 从 DataFrame 查
        if self.df is not None and "sku" in self.df.columns:
            match = self.df[self.df["sku"].astype(str).str.strip() == str(sku).strip()]
            if len(match) > 0:
                row = match.iloc[0]
                return {
                    "sku": sku,
                    "category": str(row.get("category", "")).replace("nan", ""),
                    "brand": str(row.get("brand", "")).replace("nan", ""),
                    "model": str(row.get("model", "")).replace("nan", ""),
                    "year": str(row.get("year", "")).replace("nan", ""),
                    "color": str(row.get("color", "")).replace("nan", ""),
                    "material": str(row.get("material", "")).replace("nan", ""),
                    "product_name": str(row.get("product_name", "")).replace("nan", ""),
                }

        # 从 dict 查
        if sku in self.data:
            info = self.data[sku].copy()
            info.setdefault("sku", sku)
            return info

        return None

    def list_skus(self) -> list:
        """列出所有 SKU。"""
        if self.df is not None and "sku" in self.df.columns:
            return self.df["sku"].astype(str).tolist()
        return list(self.data.keys())

    def search_category(self, keyword: str) -> list:
        """按类目关键词搜索 SKU。"""
        if self.df is not None and "category" in self.df.columns:
            match = self.df[self.df["category"].astype(str).str.contains(keyword, na=False)]
            return match["sku"].astype(str).tolist()
        return []


def quick_load(sku_info_dict: dict) -> dict:
    """快捷方法：直接传一个 SKU 的 dict，标准化字段名。

    用法:
        info = quick_load({
            "sku": "90409001",
            "类目": "脚踏",
            "车型": "Harley Touring 2014-2026",
            "颜色": "黑金",
        })
    """
    # 标准化字段名（中→英）
    normalized = {}
    for key, val in sku_info_dict.items():
        eng_key = ProductLoader.COLUMN_MAP.get(key, key)
        normalized[eng_key] = val
    normalized.setdefault("sku", sku_info_dict.get("sku", ""))
    return normalized


# ── 测试 ──
if __name__ == "__main__":
    # 测试1：直接 dict
    print("=== 测试1：dict 输入 ===")
    loader = ProductLoader({
        "90409001": {"category": "脚踏", "brand": "Harley", "model": "Touring",
                      "year": "2014-2026", "color": "Black Gold", "material": "6061 Aluminum"}
    })
    info = loader.get_sku("90409001")
    print(info)

    # 测试2：quick_load
    print("\n=== 测试2：quick_load ===")
    info = quick_load({"sku": "90101013", "类目": "手把", "车型": "Touring", "年份": "2014-2023"})
    print(info)

    print("\n✅ 测试通过")
