import sys
import traceback

log_file = 'run_log.txt'

with open(log_file, 'w', encoding='utf-8') as log:
    try:
        log.write("开始执行...\n")
        
        import os
        log.write("导入os完成\n")
        
        from ebay_advisor import (
            load_sales_data,
            load_ad_data,
            SKUEvaluator,
            KeywordOptimizer,
            PotentialPredictor,
            ReportGenerator
        )
        log.write("导入ebay_advisor模块完成\n")
        
        sales_file = '广告源数据/EBAY半月销售监测.xlsx'
        ad_file = '广告源数据/CPC Download 20260701063134.xlsx'
        
        log.write(f"销售文件存在: {os.path.exists(sales_file)}\n")
        log.write(f"广告文件存在: {os.path.exists(ad_file)}\n")
        
        log.write("\n加载销售数据...\n")
        sales_df = load_sales_data(sales_file)
        log.write(f"销售数据: {len(sales_df)}条\n")
        
        log.write("\n加载广告数据...\n")
        ad_df = load_ad_data(ad_file)
        log.write(f"广告数据: {len(ad_df)}条\n")
        
        log.write("\n评估SKU...\n")
        sku_evaluator = SKUEvaluator(sales_df)
        sku_evaluator.evaluate_all()
        log.write("SKU评估完成\n")
        
        log.write("\n优化关键词...\n")
        keyword_optimizer = KeywordOptimizer(ad_df)
        keyword_optimizer.optimize()
        log.write("关键词优化完成\n")
        
        log.write("\n预测潜力...\n")
        potential_predictor = PotentialPredictor(sales_df)
        potential_predictor.predict()
        log.write("潜力预测完成\n")
        
        log.write("\n生成报告...\n")
        report_generator = ReportGenerator()
        report = report_generator.generate_full_report(
            sku_evaluator,
            keyword_optimizer,
            potential_predictor
        )
        
        output_file = 'eBay广告投放分析报告.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        log.write(f"\n报告已保存: {output_file}\n")
        
    except Exception as e:
        log.write(f"\n错误: {e}\n")
        log.write(traceback.format_exc())

print("Done!")
