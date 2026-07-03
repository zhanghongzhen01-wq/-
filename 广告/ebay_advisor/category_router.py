"""
类目路由模块 —— SKU类目 → ZK知识库映射 → 投词策略

从 uTools 知识库 ZK 系列笔记中抽取每个品类的：
  - 黄金标题公式
  - 核心关键词词库
  - 标题模板
  - 竞品差异化建议
  - Item Specifics 关键字段
"""

CATEGORY_MAP = {
    "手把": {
        "zk_notes": ["ZK-003", "ZK-005"],
        "display_name": "Handlebar",
        "formula": "[Height\"] [Style] [Handlebar/Bar] [Pre-wired] [Diameter] [Harley] [车型] [年份] [Color]",
        "core_keywords": {
            "product_type": ["Handlebar", "Handle Bar", "Ape Hanger", "Meathook Bar", "Bagger Bar"],
            "attributes": ["Pre-wired", "Pre wired", "1.25\"", "1.5\"", "14\"", "16\"", "18\""],
            "fitment": ["Harley Touring", "Road Glide", "Street Glide", "Dyna", "Softail", "Sportster"],
            "material": ["Steel", "Chrome", "Black", "Gloss Black"],
        },
        "templates": [
            "{height}\" {style} Handlebar Pre-wired {diameter} Harley {model} {year} {color}",
            "{style} Bar PW {height}\" {diameter} For Harley {model} {year}",
        ],
        "negative_keywords": ["bicycle", "bike pedal", "ATV"],
        "competitor_insight": "Pre-wired 是核心差异词，竞品标题常缺。主图标注 PRE-WIRED 提升 CTR",
    },

    "手把组合": {
        "zk_notes": ["ZK-014"],
        "display_name": "Handlebar + Cable Kit Combo",
        "formula": "[Height\"] [Style] [Bar + Cable Kit] [TBW Clutch Brake] [Harley] [车型] [年份]",
        "core_keywords": {
            "product_type": ["Handlebar Combo", "Bar + Cable Kit", "Handlebar Cable Kit Combo"],
            "attributes": ["TBW", "Clutch", "Brake Line", "ABS", "14\"", "16\"", "Ape Hanger", "Meathook"],
            "fitment": ["Harley Road Glide", "Street Glide", "Touring", "Electra Glide"],
            "material": ["Chrome", "Black", "Stainless Steel Braided"],
        },
        "templates": [
            "{height}\" {style} Bar + Cable Kit TBW Clutch Brake Harley {model} {year}",
            "{height}\" {style} Handlebar Combo Cable Brake Kit TBW Clutch Harley Touring {year}",
        ],
        "negative_keywords": ["bicycle", "dirt bike", "ATV"],
        "competitor_insight": "Combo 关键词强化'一套搞定'感知，支撑更高定价。Pre-wired 砍掉放 Item Specifics 省 10 字符",
    },

    "护杠前": {
        "zk_notes": ["ZK-006"],
        "display_name": "Front Crash Bar / Engine Guard",
        "formula": "[Front] [Engine Guard] [Highway Crash Bar] [Material] [Diameter] [Harley] [车型] [年份] [Color]",
        "core_keywords": {
            "product_type": ["Engine Guard", "Highway Crash Bar", "Front Crash Bar", "Highway Bar"],
            "attributes": ["1.25\"", "1.5\"", "Black", "Chrome", "Highway Peg Mountable"],
            "fitment": ["Harley Touring", "Road Glide", "Street Glide", "Softail", "Dyna", "Sportster"],
            "material": ["Steel", "Stainless Steel", "Black Powder Coat"],
        },
        "templates": [
            "Front Engine Guard Highway Crash Bar {diameter} Harley {model} {year} {color}",
            "Highway Engine Guard Bar Crash {model} Harley {year} {color}",
        ],
        "negative_keywords": ["rear", "saddlebag", "pair", "set"],
        "competitor_insight": "Engine Guard + Highway Crash Bar 必须同时出现，覆盖两套搜索词",
    },

    "护杠后": {
        "zk_notes": ["ZK-004"],
        "display_name": "Rear Crash Bar / Saddlebag Guard",
        "formula": "[Rear] [Crash Bar] [Saddlebag Guard] [Frame Slider] [Harley] [车型] [年份] [Color]",
        "core_keywords": {
            "product_type": ["Rear Crash Bar", "Saddlebag Guard", "Frame Slider", "Crash Rails", "Saddlebag Bracket Guard"],
            "attributes": ["1.25\"", "1.5\"", "Delrin Slider", "Black", "Chrome"],
            "fitment": ["Harley Touring", "Road Glide", "Street Glide", "Softail", "Low Rider"],
            "material": ["Steel", "Stainless Steel"],
        },
        "templates": [
            "Rear Crash Bar Saddlebag Guard Harley {model} {year} {color}",
            "Rear Saddlebag Guard Crash Bar Bracket Harley Touring {year}",
        ],
        "negative_keywords": ["front", "engine", "highway"],
        "competitor_insight": "Touring 用 Saddlebag Guard，Softail 用 Frame Slider，不可混用",
    },

    "护杠组合": {
        "zk_notes": ["ZK-008"],
        "display_name": "Front & Rear Crash Bar Set",
        "formula": "[Front Rear] [Crash Bar] [Engine Guard] [Highway] [Saddlebag Guard] [Harley] [车型] [年份] [Color]",
        "core_keywords": {
            "product_type": ["Front Rear Crash Bar", "Engine Guard Set", "Crash Bar Combo", "Highway Saddlebag Guard"],
            "attributes": ["1.25\"", "1.5\"", "Black", "Chrome", "Flat-Out Bar"],
            "fitment": ["Harley Touring", "Road Glide", "Street Glide", "Electra Glide", "Road King", "Low Rider ST"],
            "material": ["Steel", "Stainless Steel"],
        },
        "templates": [
            "Front Rear Crash Bar Highway Engine Guard Saddlebag Harley {model} {year}",
            "Front Engine Guard Highway Crash Bar Rear Saddlebag Bracket Harley Touring {year} {color}",
        ],
        "negative_keywords": ["single", "one side", "left only", "right only"],
        "competitor_insight": "标题必须同时覆盖前护杠Engine Guard+Highway Crash Bar和后护杠Rear Crash Bar+Saddlebag Guard。Crash Bar一词两吃放中间",
    },

    "鞍袋护杠": {
        "zk_notes": ["ZK-013"],
        "display_name": "Saddlebag Guard + Highway Footrest",
        "formula": "[Saddlebag Guard] [Engine Guard] [Highway Footrest] [Crash Bar] [Foot Pegs] [Harley] [车型] [年份]",
        "core_keywords": {
            "product_type": ["Saddlebag Guard", "Engine Guard", "Highway Footrest", "Crash Bar", "Foot Pegs"],
            "attributes": ["Black", "Chrome", "1.25\"", "1.5\"", "Quick Release"],
            "fitment": ["Harley Touring", "Road Glide", "Street Glide", "Electra Glide", "Road King"],
            "material": ["Steel", "Billet Aluminum"],
        },
        "templates": [
            "Saddlebag Guard Engine Crash Bar Highway Footrest Harley {model} {year}",
        ],
        "negative_keywords": ["front only", "rear only"],
        "competitor_insight": "护杠+脚步双搜索词族，需同时覆盖两套变体词",
    },

    "脚踏": {
        "zk_notes": ["ZK-018"],
        "display_name": "Floorboards Kit",
        "formula": "[Floorboards] [Footpegs] [Shifter] [Brake] [Diamond] [Anodized] [Color] [Harley] [车型] [年份]",
        "core_keywords": {
            "product_type": ["Floorboards", "Footboards", "Foot Pegs", "Footpegs", "Floorboard Kit"],
            "attributes": ["Diamond", "Anodized", "CNC", "Billet", "6061", "Aluminum", "Extended", "Stretched"],
            "components": ["Shifter", "Shift Lever", "Shift Linkage", "Brake Pedal", "Brake Lever", "Brake Arm", "Heel Toe Shifter"],
            "color": ["Black Gold", "Black White", "Two-Tone", "Dual Color"],
            "fitment": ["Harley Touring", "Road Glide", "Street Glide", "Electra Glide", "Road King", "Softail", "Fat Boy", "Heritage"],
            "material": ["6061 Aluminum", "CNC Machined", "Anodized"],
        },
        "templates": [
            "Floorboards Footpegs Shifter Brake Diamond Anodized {color} Harley {model} {year}",
            "Diamond Floorboards Kit Shifter Brake Footpegs Anodized Harley {model} {year}",
            "Diamond Anodized Floorboards Footpegs Shifter Brake Kit Harley {model} {year} {color}",
        ],
        "negative_keywords": ["OEM", "stock", "original", "take off"],
        "competitor_insight": "所有竞品标题都没写外观词（Diamond/Anodized/双色）→ 你的蓝海关键词",
    },

    "拉线油门": {
        "zk_notes": ["ZK-011"],
        "display_name": "Throttle Idle Cable Kit",
        "formula": "[Throttle] [Idle] [Cable Kit] [Length] [Harley] [车型] [年份] [Material]",
        "core_keywords": {
            "product_type": ["Throttle Cable", "Idle Cable", "Cable Kit", "Throttle Idle Cable Set"],
            "attributes": ["+6\"", "+8\"", "+10\"", "Stainless Steel", "Braided"],
            "fitment": ["Harley Dyna", "Softail", "Touring", "Sportster"],
            "material": ["Stainless Steel Braided", "Black Vinyl"],
        },
        "templates": [
            "Throttle Idle Cable Kit {length} Harley {model} {year} {material}",
        ],
        "negative_keywords": ["TBW", "electronic", "drive by wire"],
        "competitor_insight": "机械油门线，强调长度（+X\"），和TBW电子油门区分",
    },

    "拉线总成": {
        "zk_notes": ["ZK-013"],
        "display_name": "Cable & Brake Line Extension Kit",
        "formula": "[Clutch] [TBW] [Brake] [Cable Kit] [+X\"] [ABS] [Harley] [车型] [年份]",
        "core_keywords": {
            "product_type": ["Cable Kit", "Brake Line Extension Kit", "Clutch Cable", "TBW Extension", "ABS Brake Line"],
            "attributes": ["+4\"", "+6\"", "+8\"", "TBW", "ABS", "Hydraulic", "Braided"],
            "fitment": ["Harley Road Glide", "Street Glide", "Touring", "Ultra Limited"],
            "material": ["Stainless Steel Braided"],
        },
        "templates": [
            "Cable Brake Line Kit +{length}\" TBW Clutch ABS Harley {model} {year}",
            "Handlebar Cable Brake Line Extension Kit TBW Clutch Harley {model} {year}",
        ],
        "negative_keywords": ["mechanical", "carburetor"],
        "competitor_insight": "TBW + ABS 是现代哈雷的双硬门槛，必须标注",
    },

    "手把延长线": {
        "zk_notes": ["ZK-016"],
        "display_name": "Hand Control Extension Wire w/ TBW",
        "formula": "[Hand Control] [Extension Wire] [TBW] [Harness] [Harley] [车型] [年份] [+X\"]",
        "core_keywords": {
            "product_type": ["Hand Control Extension", "Wire Extension", "TBW Extension", "Wire Harness", "Handlebar Switch Extension"],
            "attributes": ["+6\"", "+8\"", "+12\"", "TBW", "Plug and Play"],
            "fitment": ["Harley Road Glide", "Street Glide", "Touring"],
            "material": ["OEM Connector"],
        },
        "templates": [
            "Hand Control Extension Wire TBW Harley {model} {year} +{length}\"",
        ],
        "negative_keywords": ["cable", "clutch", "brake line", "mechanical"],
        "competitor_insight": "纯电子线束（非拉线），强调 TBW 适配和即插即用",
    },

    "后视镜": {
        "zk_notes": ["ZK-007"],
        "display_name": "Rear View Mirrors",
        "formula": "[Color] [Mirror] [车型关键词] [Harley] [车型列表] [年份] [Style]",
        "core_keywords": {
            "product_type": ["Mirror", "Rear View Mirror", "Fairing Mirror", "Stem Mirror", "Side Mirror"],
            "attributes": ["Black", "Chrome", "Convex", "LED", "Wide Angle", "10mm", "5/16\""],
            "fitment": ["Harley Street Glide", "Road Glide", "Road King", "Electra Glide", "Dyna", "Sportster"],
            "material": ["Aluminum", "ABS Plastic", "Glass"],
        },
        "templates": [
            "{color} Mirror {model_keyword} Harley {model_list} {year} {style}",
        ],
        "negative_keywords": ["car", "truck", "SUV", "bicycle"],
        "competitor_insight": "颜色与车型列表优先于造型词。Fairing Mirror 和 Stem Mirror 是两种不同的搜索入口",
    },

    "LED大灯": {
        "zk_notes": ["ZK-017"],
        "display_name": "Motorcycle LED Headlight",
        "formula": "[Size\"] [LED] [Headlight] [Daymaker] [Style] [Harley] [车型] [年份] [Color]",
        "core_keywords": {
            "product_type": ["LED Headlight", "Daymaker", "Headlamp", "Passing Lamp", "LED Light Kit"],
            "attributes": ["7\"", "5.75\"", "4.5\"", "DOT Approved", "Halo Ring", "DRL", "Dual Burn", "H4", "H13"],
            "fitment": ["Harley Road Glide", "Street Glide", "Dyna", "Softail", "Sportster"],
            "style": ["Black", "Chrome", "Smoke", "Projector"],
        },
        "templates": [
            "{size}\" LED Headlight Daymaker {style} Harley {model} {year}",
            "LED Headlight Daymaker Halo DRL DOT Harley {model} {year} {color}",
        ],
        "negative_keywords": ["halogen", "OEM stock", "car", "truck", "Jeep"],
        "competitor_insight": "7寸是最卷规格。Daymaker是哈雷圈的约定俗成叫法，必须出现在标题中",
    },

    "衬套": {
        "zk_notes": ["ZK-010", "ZK-012"],
        "display_name": "Handlebar Riser Bushing",
        "formula": "[Handlebar] [Riser] [Bushing Kit] [Material] [Anti-Vibration] [Harley] [车型] [年份]",
        "core_keywords": {
            "product_type": ["Handlebar Riser Bushing", "Riser Bushing Kit", "Handlebar Bushing", "Polyurethane Bushing"],
            "attributes": ["Polyurethane", "PU", "Anti Vibration", "1\"", "1.25\"", "Upgrade"],
            "fitment": ["Harley Touring", "Road Glide", "Street Glide", "Dyna", "Softail"],
        },
        "templates": [
            "Handlebar Riser Bushing Kit {material} Anti-Vibration Harley {model} {year}",
        ],
        "negative_keywords": ["rubber", "OEM"],
        "competitor_insight": "PU材质是核心差异点，强调比OEM橡胶更耐用、减震更好",
    },

    "三星": {
        "zk_notes": ["ZK-009"],
        "display_name": "Triple Tree",
        "formula": "[Triple Tree] [Upper/Lower] [Fork Clamp] [Harley] [车型] [年份] [Color]",
        "core_keywords": {
            "product_type": ["Triple Tree", "Triple Clamp", "Fork Clamp", "Upper Triple Tree", "Lower Triple Tree"],
            "attributes": ["Billet", "CNC", "Black", "Chrome", "Raked"],
            "fitment": ["Harley Dyna", "Softail", "Sportster", "Touring"],
            "material": ["6061 Aluminum", "Billet Aluminum"],
        },
        "templates": [
            "Triple Tree Fork Clamp {material} Harley {model} {year} {color}",
        ],
        "negative_keywords": ["bicycle", "MTB"],
        "competitor_insight": "Triple Tree 和 Triple Clamp 都要覆盖，是两个不同的搜索入口",
    },
}


# ── 车型关键词映射 ──
MODEL_KEYWORDS = {
    "Touring": ["Touring", "Road Glide", "Street Glide", "Electra Glide", "Road King", "Ultra Limited"],
    "Road Glide": ["Road Glide", "FLTR", "FLTRX", "FLTRU", "FLTRK"],
    "Street Glide": ["Street Glide", "FLHX", "FLHXS", "FLHXST"],
    "Electra Glide": ["Electra Glide", "FLHT", "FLHTCU", "FLHTK", "Ultra Limited"],
    "Road King": ["Road King", "FLHR", "FLHRC", "FLHRXS"],
    "Softail": ["Softail", "Fat Boy", "Heritage", "FLSTF", "FLSTC", "FLSTN", "FLS", "FLSS"],
    "Dyna": ["Dyna", "Street Bob", "Low Rider", "Wide Glide", "FXD", "FXDB", "FXDL"],
    "Sportster": ["Sportster", "Iron 883", "Forty Eight", "XL", "XL883N", "XL1200X"],
    "Trike": ["Trike", "Tri Glide", "Freewheeler", "FLHTCUTG", "FLRT"],
}


def get_category_config(category_name: str) -> dict | None:
    """根据类目名获取投词配置。支持模糊匹配。"""
    for key, config in CATEGORY_MAP.items():
        if key in category_name or category_name in key:
            return config
    return None


def get_model_keywords(model_name: str) -> list[str]:
    """根据车型名返回相关搜索关键词列表。"""
    for key, keywords in MODEL_KEYWORDS.items():
        if key.lower() in model_name.lower() or model_name.lower() in key.lower():
            return keywords
    # 兜底：返回原始车型名
    return [model_name] if model_name else []


def resolve_year_range(year_str: str) -> str:
    """标准化年份格式。"""
    year_str = str(year_str).strip()
    # 已经是简写格式
    if '-' in year_str and len(year_str) <= 7:
        return year_str
    # 全写年份转简写
    import re
    years = re.findall(r'\d{4}', year_str)
    if len(years) >= 2:
        return f"{years[0][2:]}-{years[-1][2:]}"
    if len(years) == 1:
        return f"{years[0][2:]}-Up"
    return year_str


def build_title(sku_info: dict) -> str:
    """根据 SKU 信息自动生成 eBay 标题。

    sku_info 应包含:
        - category: 类目名（如 "脚踏"）
        - brand: 适配品牌（如 "Harley"）
        - model: 适配车型（如 "Touring"）
        - year: 适配年份（如 "2014-2026"）
        - color: 颜色（如 "Black Gold"）
        - material: 材质（如 "6061 Aluminum"）
    """
    config = get_category_config(sku_info.get("category", ""))
    if not config:
        return ""

    templates = config.get("templates", [])
    if not templates:
        return ""

    template = templates[0]  # 默认用第一个模板
    year = resolve_year_range(sku_info.get("year", ""))

    # 从车型关键词中取最热门的
    model_keywords = get_model_keywords(sku_info.get("model", ""))
    model_str = model_keywords[0] if model_keywords else sku_info.get("model", "")

    return template.format(
        height=sku_info.get("height", "14"),
        style=sku_info.get("style", ""),
        diameter=sku_info.get("diameter", ""),
        color=sku_info.get("color", "Black"),
        model=model_str,
        year=year,
        brand=sku_info.get("brand", "Harley"),
        material=sku_info.get("material", ""),
        length=sku_info.get("length", "+6"),
        model_keyword=sku_info.get("model_keyword", model_str),
        model_list=sku_info.get("model_list", model_str),
        size=sku_info.get("size", "7"),
    ).strip()


def generate_keyword_list(sku_info: dict) -> dict:
    """根据 SKU 信息生成关键词建议（Broad/Phrase/Exact 三级）。

    返回:
        {
            "broad": [...],
            "phrase": [...],
            "exact": [...],
            "negative": [...]
        }
    """
    config = get_category_config(sku_info.get("category", ""))
    if not config:
        return {"broad": [], "phrase": [], "exact": [], "negative": []}

    keywords = config.get("core_keywords", {})
    model_kws = get_model_keywords(sku_info.get("model", ""))
    brand = sku_info.get("brand", "Harley")
    year = resolve_year_range(sku_info.get("year", ""))

    broad = []
    phrase = []
    exact = []

    # 产品类型 × 车型 = Broad
    for pt in keywords.get("product_type", [])[:3]:
        for mk in model_kws[:2]:
            broad.append(f"{pt} {brand} {mk}".strip())

    # 产品类型 + 关键属性 = Phrase
    for pt in keywords.get("product_type", [])[:2]:
        for attr in keywords.get("attributes", [])[:2]:
            p = f"{pt} {attr} {brand}".strip()
            if p not in phrase:
                phrase.append(p)

    # 精确短语 = Exact
    title = build_title(sku_info)
    if title:
        exact.append(f"[{title}]")

    negative = config.get("negative_keywords", [])

    return {
        "broad": broad[:8],
        "phrase": phrase[:5],
        "exact": exact[:3],
        "negative": negative,
    }


def get_item_specifics(category_name: str) -> dict:
    """根据类目返回推荐的 Item Specifics 字段。"""
    specifics = {
        "Brand": "Unbranded",
        "Placement on Vehicle": "Front",
        "Manufacturer Part Number": "",
        "UPC": "",
    }

    config = get_category_config(category_name)
    if not config:
        return specifics

    material = config.get("core_keywords", {}).get("material", [])
    if material:
        specifics["Material"] = material[0]

    display = config.get("display_name", "")
    specifics["Type"] = display

    return specifics


# ── CLI 测试入口 ──
if __name__ == "__main__":
    # 测试：脚踏 SKU
    test_sku = {
        "category": "脚踏",
        "brand": "Harley",
        "model": "Touring",
        "year": "2014-2026",
        "color": "Black Gold",
        "material": "6061 Aluminum",
    }

    print("=== 类目配置 ===")
    config = get_category_config("脚踏")
    print(f"ZK笔记: {config['zk_notes']}")
    print(f"黄金公式: {config['formula']}")

    print("\n=== 生成标题 ===")
    title = build_title(test_sku)
    print(title)

    print("\n=== 生成关键词 ===")
    kw = generate_keyword_list(test_sku)
    for level, words in kw.items():
        print(f"\n{level}:")
        for w in words:
            print(f"  - {w}")

    print("\n=== 年份处理 ===")
    print(f"2014-2026 → {resolve_year_range('2014-2026')}")
    print(f"2008-2013 → {resolve_year_range('2008-2013')}")
    print(f"2000 → {resolve_year_range('2000')}")
