import pandas as pd

with open('data_report.txt', 'w', encoding='utf-8') as f:
    f.write("=== 销售数据 ===\n")
    sales_df = pd.read_excel('广告源数据/EBAY半月销售监测.xlsx')
    f.write(f"行数: {len(sales_df)}, 列数: {len(sales_df.columns)}\n")
    f.write("列名: " + str(sales_df.columns.tolist()) + "\n")
    f.write("\n前5行:\n")
    f.write(sales_df.head().to_string() + "\n")
    f.write("\n数据类型:\n")
    f.write(sales_df.dtypes.to_string() + "\n")

    f.write("\n\n=== 广告数据 ===\n")
    ad_df = pd.read_excel('广告源数据/CPC Download 20260701063134.xlsx')
    f.write(f"行数: {len(ad_df)}, 列数: {len(ad_df.columns)}\n")
    f.write("列名: " + str(ad_df.columns.tolist()) + "\n")
    f.write("\n前5行:\n")
    f.write(ad_df.head().to_string() + "\n")
    f.write("\n数据类型:\n")
    f.write(ad_df.dtypes.to_string() + "\n")

print("Done!")
