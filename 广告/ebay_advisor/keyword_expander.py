"""
关键词扩展模块 —— 从外部平台获取高价值搜索词。

来源:
  1. Amazon 搜索自动补全 (completion.amazon.com)
  2. Google 搜索建议 (suggestqueries.google.com)
  3. 基于现有高效词的派生组合
"""
import urllib.request
import urllib.parse
import json
import ssl
import pandas as pd
from collections import OrderedDict


def _fetch_json(url, timeout=10):
    """带 SSL 容错的 JSON 请求"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            data = resp.read().decode('utf-8')
            return json.loads(data)
    except Exception as e:
        return None


def get_amazon_suggestions(seed_keyword, market='com', max_results=10):
    """从 Amazon 自动补全获取相关搜索词。

    Args:
        seed_keyword: 种子词，如 'harley handlebar'
        market: 站点后缀，com/us/de/uk 等
        max_results: 最多返回条数

    Returns:
        list of dict: [{keyword, source, relevance}]
    """
    # Amazon 自动补全 API
    # marketplace IDs: https://images-na.ssl-images-amazon.com/images/G/01/rainier/help/xsd/release_4_1/MarketplaceIDs.html
    market_ids = {
        'com': 'ATVPDKIKX0DER',  # US
        'de': 'A1PA6795UKMFR9',  # Germany
        'uk': 'A1F83G8C2ARO7P',  # UK
    }
    mid = market_ids.get(market, 'ATVPDKIKX0DER')
    encoded = urllib.parse.quote(seed_keyword[:50])
    url = f'https://completion.amazon.com/api/2017/suggestions?mid={mid}&alias=aps&prefix={encoded}&limit=10'
    data = _fetch_json(url)

    if not data or 'suggestions' not in data:
        return []

    results = []
    seen = {seed_keyword.lower()}
    for item in data['suggestions']:
        kw = item.get('value', '')
        if not kw or kw.lower() in seen:
            continue
        seen.add(kw.lower())
        results.append({
            'keyword': kw,
            'source': f'Amazon {market} autocomplete',
            'relevance': 'high',  # Amazon 用户真实搜索
        })
        if len(results) >= max_results:
            break
    return results


def get_google_suggestions(seed_keyword, max_results=10):
    """从 Google Suggest 获取相关搜索词"""
    encoded = urllib.parse.quote(seed_keyword[:50])
    url = f'https://suggestqueries.google.com/complete/search?client=firefox&q={encoded}'
    data = _fetch_json(url)

    if not data or len(data) < 2:
        return []

    results = []
    seen = {seed_keyword.lower()}
    for kw in data[1]:
        if isinstance(kw, list):
            kw = kw[0] if kw else ''
        kw = str(kw).strip()
        if not kw or kw.lower() in seen:
            continue
        seen.add(kw.lower())
        results.append({
            'keyword': kw,
            'source': 'Google Suggest',
            'relevance': 'medium',
        })
        if len(results) >= max_results:
            break
    return results


def expand_keywords(seed_keywords, sources=None, max_per_seed=10):
    """批量扩展关键词：给定一组种子词，从多个平台获取相关词。

    Args:
        seed_keywords: 种子词列表
        sources: 数据源列表，默认 ['amazon', 'google', 'trend']
        max_per_seed: 每个种子词最多扩展多少条

    Returns:
        DataFrame: [keyword, source, relevance, seed_keyword]
    """
    if sources is None:
        sources = ['amazon', 'trend']

    all_results = []
    seen_kw = set()

    # ── 内置趋势关键词（2026年巡洋舰改装热点）──
    TREND_KEYWORDS = {
        # Harley 热门车型 + 零件组合
        'harley handlebar': [
            'ape hanger 14 inch harley', 'meathook handlebar', 't bar dyna',
            'prewired handlebar harley', '1.5 inch handlebar harley touring',
            'handlebar riser 1 to 1.25 harley', 'cable kit handlebar harley',
        ],
        'harley crash bar': [
            'highway crash bar harley touring', 'engine guard softail 2018',
            'sportster crash bar 1.25', 'front engine guard harley dyna',
            'rear crash bar harley saddlebag protector',
        ],
        'harley mirrors': [
            'harley led mirror', 'black mirror harley street glide',
            'chrome mirror harley road king', 'convex mirror harley dyna',
            'bar end mirror harley sportster',
        ],
        'harley foot peg': [
            'forward control foot peg harley', 'floorboard harley touring',
            'highway peg harley crash bar mount', 'passenger foot peg harley',
            'foot peg adapter harley softail',
        ],
        # LED 照明趋势（2026 热点）
        'harley led light': [
            'led headlight harley road glide', 'led passing lamp harley',
            'led turn signal harley dyna', 'led tail light harley sportster',
            'led accent light harley bagger', 'led underglow kit motorcycle',
        ],
        # 印度安/川崎/胜利（长尾品牌）
        'indian crash bar': [
            'indian scout crash bar', 'indian chief engine guard',
            'indian challenger highway bar', 'indian chieftain saddlebag guard',
        ],
        'kawasaki crash bar': [
            'kawasaki vulcan crash bar', 'kawasaki vaquero engine guard',
            'kawasaki ninja frame slider',
        ],
    }

    if 'trend' in sources:
        for seed in seed_keywords:
            seed_lower = seed.lower().strip()
            for trend_seed, keywords in TREND_KEYWORDS.items():
                # 匹配语义相近的种子词
                if any(w in seed_lower for w in trend_seed.split()):
                    for kw in keywords[:max_per_seed]:
                        if kw.lower() not in seen_kw:
                            seen_kw.add(kw.lower())
                            all_results.append({
                                'keyword': kw,
                                'source': '2026 Trend Research',
                                'relevance': 'high',
                                'seed_keyword': seed
                            })

    for seed in seed_keywords:
        seed = str(seed).strip()
        if not seed or len(seed) < 3:
            continue

        for src in sources:
            if src == 'amazon':
                suggestions = get_amazon_suggestions(seed, max_results=max_per_seed)
            elif src == 'google':
                suggestions = get_google_suggestions(seed, max_results=max_per_seed)
            else:
                continue

            for s in suggestions:
                kw_lower = s['keyword'].lower()
                if kw_lower not in seen_kw:
                    seen_kw.add(kw_lower)
                    s['seed_keyword'] = seed
                    all_results.append(s)

    return pd.DataFrame(all_results) if all_results else pd.DataFrame(
        columns=['keyword', 'source', 'relevance', 'seed_keyword']
    )


if __name__ == '__main__':
    # 测试
    seeds = ['harley handlebar', 'harley crash bar', 'harley mirrors']
    df = expand_keywords(seeds)
    print(f'扩展出 {len(df)} 个新词')
    for _, r in df.head(15).iterrows():
        print(f'  {r["keyword"][:50]}  [{r["source"]}]')
