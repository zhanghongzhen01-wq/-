import os
from ebay_advisor import (
    load_sales_data,
    load_ad_data,
    SKUEvaluator,
    KeywordOptimizer,
    PotentialPredictor,
    ReportGenerator
)


def main():
    sales_file = '广告源数据/EBAY半月销售监测.xlsx'
    ad_file = '广告源数据/CPC Download 20260701063134.xlsx'
    
    if not os.path.exists(sales_file):
        print(f"错误：销售数据文件不存在 - {sales_file}")
        return
    
    if not os.path.exists(ad_file):
        print(f"错误：广告数据文件不存在 - {ad_file}")
        return
    
    print("正在加载数据...")
    sales_df = load_sales_data(sales_file)
    ad_df = load_ad_data(ad_file)
    
    print(f"销售数据: {len(sales_df)}条记录")
    print(f"广告数据: {len(ad_df)}条记录")
    
    print("\n正在评估SKU投放价值...")
    sku_evaluator = SKUEvaluator(sales_df)
    sku_evaluator.evaluate_all()
    
    print("正在优化广告词组...")
    keyword_optimizer = KeywordOptimizer(ad_df)
    keyword_optimizer.optimize()
    
    print("正在预判SKU投放潜力...")
    potential_predictor = PotentialPredictor(sales_df)
    potential_predictor.predict()
    
    print("\n正在生成分析报告...")
    report_generator = ReportGenerator()
    report = report_generator.generate_full_report(
        sku_evaluator,
        keyword_optimizer,
        potential_predictor
    )
    
    output_txt = 'eBay广告投放分析报告.txt'
    output_xlsx = 'eBay广告投放分析报告.xlsx'
    output_html = 'eBay广告投放分析报告.html'

    report_generator.save_report(output_txt)
    report_generator.save_excel(output_xlsx, sku_evaluator, keyword_optimizer, potential_predictor)
    report_generator.save_html(output_html, sku_evaluator, keyword_optimizer, potential_predictor)

    print(f"\n报告已生成:")
    print(f"  TXT  : {output_txt}")
    print(f"  Excel: {output_xlsx}")
    print(f"  HTML : {output_html}")


if __name__ == '__main__':
    main()
