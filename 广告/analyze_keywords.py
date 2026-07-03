import pandas as pd
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 400)
pd.set_option('display.max_colwidth', 80)

def find_keyword_section(df):
    """
    Find the 'Sell Keyword' section in the eBay Seller Campaign Report.
    Returns the data rows with proper column mapping.
    """
    # Look for the row that contains "Sell Keyword"
    for i, row in df.iterrows():
        row_vals = [str(v).strip() for v in row.values if pd.notna(v)]
        if 'Sell Keyword' in row_vals:
            # The keyword data starts from the next row
            keyword_data_start = i + 1
            break
    else:
        # fallback: look for any row with "Search Keyword"
        for i, row in df.iterrows():
            row_vals = [str(v).strip() for v in row.values if pd.notna(v)]
            if 'Search Keyword' in row_vals:
                keyword_data_start = i + 1
                break
        else:
            print("  Could not find 'Sell Keyword' section!")
            return pd.DataFrame()

    # Collect keyword rows until we hit a summary/empty row or end
    keyword_rows = []
    for i in range(keyword_data_start, len(df)):
        row = df.iloc[i]
        # Check if this is a data row (has keyword text and numeric data)
        row_vals = [v for v in row.values if pd.notna(v)]
        if len(row_vals) == 0:
            continue

        # The search keyword is typically in the 5th column (index 4) or later
        # Looking at raw data, col index ~4 has the keyword text, col ~5 has impressions
        # Try to find the keyword column - it's the one with text content
        keyword = None
        impressions = None
        clicks = None

        # Try different column alignments based on observed data patterns
        # Pattern: text keyword in one column, followed by numbers
        for j in range(len(row)):
            val = row.iloc[j]
            if pd.isna(val):
                continue
            if isinstance(val, str) and len(val) > 2 and not val.replace('%','').replace('.','').replace('$','').replace(' ','').replace(',','').isdigit():
                # This might be the keyword
                # Check if next few columns have numbers
                if j + 3 < len(row):
                    next_vals = [row.iloc[j+k] for k in range(1, 4)]
                    numeric_count = sum(1 for v in next_vals if pd.notna(v) and (isinstance(v, (int, float)) or (isinstance(v, str) and v.replace('%','').replace('.','').strip().isdigit())))
                    if numeric_count >= 2:
                        keyword = val
                        # Now extract numeric data
                        if j + 1 < len(row):
                            impressions = row.iloc[j+1]
                        if j + 2 < len(row):
                            clicks = row.iloc[j+2]
                        break

        if keyword is None:
            continue

        # Skip header rows that might have leaked in
        if keyword.strip().lower() in ['search keyword', 'sell keyword', 'ad group name', 'keyword']:
            continue
        if keyword.strip().startswith('Consolidated data'):
            continue

        # Now extract all metrics
        def safe_num(val, default=0):
            if pd.isna(val):
                return default
            if isinstance(val, (int, float)):
                return float(val)
            s = str(val).strip().replace('$', '').replace(',', '')
            if s.endswith('%'):
                s = s[:-1]
            try:
                return float(s)
            except:
                return default

        def safe_pct(val):
            """Extract percentage as a float (e.g., '1.39%' -> 1.39)"""
            if pd.isna(val):
                return 0.0
            if isinstance(val, (int, float)):
                return float(val)
            s = str(val).strip().replace('%', '')
            try:
                return float(s)
            except:
                return 0.0

        row_data = {}
        row_data['keyword'] = keyword.strip()

        # Based on observed data, after keyword:
        # +1=Impressions, +2=Clicks, +3=CTR, +4=Sales, +5=ConversionRate,
        # +6=SaleAmount, +7=AdFees, +8=ROAS, +9=ACOS, +10=ROI,
        # +11=AvgCostPerSale, +12=CostPerClick

        for offset, name in [(1, 'impressions'), (2, 'clicks'), (3, 'ctr'),
                              (4, 'sales'), (5, 'conversion_rate'),
                              (6, 'sale_amount'), (7, 'ad_fees'),
                              (8, 'roas'), (9, 'acos'), (10, 'roi'),
                              (11, 'avg_cost_per_sale'), (12, 'cost_per_click')]:
            col_idx = j + offset
            if col_idx < len(row):
                val = row.iloc[col_idx]
                if name in ['ctr', 'conversion_rate', 'roas', 'acos', 'roi']:
                    row_data[name] = safe_pct(val)
                else:
                    row_data[name] = safe_num(val)
            else:
                row_data[name] = 0

        keyword_rows.append(row_data)

    return pd.DataFrame(keyword_rows)

def analyze_file(filepath, label):
    print(f"\n{'='*80}")
    print(f"=== {label} ===")
    print(f"文件: {filepath}")
    print(f"{'='*80}")

    df = pd.read_excel(filepath)

    # Show campaign name
    campaign = df.iloc[0, 0] if len(df) > 0 else 'N/A'
    print(f"广告系列: {campaign}")

    # Show summary
    impressions = df.iloc[0, 10] if len(df) > 0 else 0
    clicks = df.iloc[0, 11] if len(df) > 0 else 0
    ctr = df.iloc[0, 12] if len(df) > 0 else 0
    ad_fees = df.iloc[0, 16] if len(df) > 0 else 0
    print(f"汇总: 曝光={impressions}, 点击={clicks}, CTR={ctr}, 花费={ad_fees}")

    # Extract keyword data
    kw_df = find_keyword_section(df)

    if len(kw_df) == 0:
        print("未找到关键词数据!")
        return

    print(f"\n提取到 {len(kw_df)} 个关键词数据行")

    # Show raw data for debugging
    print("\n--- 所有关键词数据 (原始) ---")
    for _, row in kw_df.iterrows():
        print(f"  [{row['keyword']}] Imp={row['impressions']:.0f} Clicks={row['clicks']:.0f} "
              f"CTR={row['ctr']:.2f}% Sales={row['sales']:.0f} eCVR={row['conversion_rate']:.2f}% "
              f"AdFee=${row['ad_fees']:.2f} CPC=${row['cost_per_click']:.2f}")

    # Summary of keywords with clicks > 0
    with_clicks = kw_df[kw_df['clicks'] > 0]
    print(f"\n--- 有点击的关键词 (共{len(with_clicks)}个) ---")
    for _, row in with_clicks.iterrows():
        print(f"  [{row['keyword']}] Imp={row['impressions']:.0f} Clicks={row['clicks']:.0f} "
              f"CTR={row['ctr']:.2f}% Sales={row['sales']:.0f} eCVR={row['conversion_rate']:.2f}% "
              f"AdFee=${row['ad_fees']:.2f} CPC=${row['cost_per_click']:.2f}")

    # Keywords with clicks AND sales
    with_sales = kw_df[kw_df['sales'] > 0]
    if len(with_sales) > 0:
        print(f"\n--- 有转化的关键词 (共{len(with_sales)}个) ---")
        for _, row in with_sales.iterrows():
            print(f"  [{row['keyword']}] Imp={row['impressions']:.0f} Clicks={row['clicks']:.0f} "
                  f"CTR={row['ctr']:.2f}% Sales={row['sales']:.0f} eCVR={row['conversion_rate']:.2f}% "
                  f"Revenue=${row['sale_amount']:.2f} AdFee=${row['ad_fees']:.2f} "
                  f"ROAS={row['roas']:.2f} CPC=${row['cost_per_click']:.2f}")

    # === SELECTION CRITERIA ===
    # Good keywords = CTR > 0.5% AND (Sales > 0 OR high CTR potential)
    # Priority 1: Has sales (conversion) with decent CTR
    # Priority 2: High CTR (>1%) even without sales (still has click-through appeal)
    # Priority 3: Moderate CTR (0.3%-1%) with at least some clicks

    print(f"\n{'='*40}")
    print(f"=== 推荐继续手动投词的关键词 ===")
    print(f"筛选标准: CTR > 0.3% 且有至少1次点击")
    print(f"{'='*40}")

    # Candidates: keywords with some clicks and reasonable CTR
    candidates = kw_df[(kw_df['clicks'] > 0) & (kw_df['ctr'] > 0.3)]
    # Sort by clicks * CTR (a simple engagement score)
    if len(candidates) > 0:
        candidates = candidates.copy()
        candidates['engagement_score'] = candidates['clicks'] * candidates['ctr']
        candidates = candidates.sort_values('engagement_score', ascending=False)

        print(f"\n找到 {len(candidates)} 个推荐关键词:\n")
        for rank, (_, row) in enumerate(candidates.iterrows(), 1):
            has_sale = "✓ 有转化" if row['sales'] > 0 else "○ 无转化"
            print(f"  #{rank} [{row['keyword']}] "
                  f"曝光={row['impressions']:.0f} 点击={row['clicks']:.0f} "
                  f"CTR={row['ctr']:.2f}% "
                  f"销量={row['sales']:.0f} eCVR={row['conversion_rate']:.2f}% "
                  f"花费=${row['ad_fees']:.2f} CPC=${row['cost_per_click']:.2f} "
                  f"{has_sale}")
    else:
        print("\n  没有符合标准的关键词。")
        print("\n  所有有点击的关键词:")
        all_with_clicks = kw_df[kw_df['clicks'] > 0].sort_values('clicks', ascending=False)
        for _, row in all_with_clicks.iterrows():
            print(f"  [{row['keyword']}] CTR={row['ctr']:.2f}% Clicks={row['clicks']:.0f}")

    return kw_df


# Analyze both files
files = [
    ('CPC Download 20260624061747.xlsx', 'SKU 1: 2008-2013 Touring'),
    ('CPC Download 20260624062557.xlsx', 'SKU 2: 2014-2026 Touring'),
]

results = {}
for fpath, label in files:
    kw_df = analyze_file(fpath, label)
    results[label] = kw_df

print(f"\n{'='*80}")
print("=== 综合分析完成 ===")
print(f"{'='*80}")
