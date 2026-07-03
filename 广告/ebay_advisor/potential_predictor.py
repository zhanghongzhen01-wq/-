import pandas as pd
import numpy as np


class PotentialPredictor:
    def __init__(self, sales_df):
        self.sales_df = sales_df
        self.predicted_df = None
    
    def predict(self):
        self.predicted_df = self.sales_df.copy()
        self.predicted_df['潜力评分'] = self.sales_df.apply(self._calculate_potential, axis=1)
        self.predicted_df['潜力等级'] = self._assign_potential_level(self.predicted_df['潜力评分'])
        self.predicted_df['潜力分析'] = self.sales_df.apply(self._analyze_potential, axis=1)
        return self.predicted_df
    
    def _calculate_potential(self, row):
        score = 0
        
        sales_15d = row['15天销量']
        sales_30d = row['30天销量']
        growth_rate = row['销量环比']
        revenue_15d = row['15天销售额']
        ad_exposure = row['15广告曝光']
        ad_clicks = row['15广告点击']
        plp_sales = row['15PLP销售额']
        plg_sales = row['15PLG销售额（光环）']
        
        if sales_15d == 0 and sales_30d == 0:
            score += 10
        elif 0 < sales_15d <= 3:
            score += 20
        elif sales_15d <= 5:
            score += 30
        
        if isinstance(growth_rate, str) and '%' in growth_rate:
            try:
                growth = float(growth_rate.replace('%', ''))
                if growth >= 100:
                    score += 30
                elif growth >= 50:
                    score += 20
                elif growth >= 20:
                    score += 10
            except:
                pass
        
        if revenue_15d >= 100 and sales_15d <= 5:
            score += 20
        elif revenue_15d >= 50 and sales_15d <= 3:
            score += 15
        
        if ad_clicks > 0 and sales_15d == 0:
            score += 15
        elif ad_exposure > 500 and sales_15d == 0:
            score += 10
        
        if plg_sales > 0 and plp_sales == 0:
            score += 10
        
        return min(score, 100)
    
    def _assign_potential_level(self, scores):
        conditions = [
            scores >= 70,
            scores >= 50,
            scores >= 30,
            scores >= 10,
            scores < 10
        ]
        choices = ['高潜力', '中潜力', '低潜力', '观察期', '无潜力']
        return np.select(conditions, choices, default='无潜力')
    
    def _analyze_potential(self, row):
        sales_15d = row['15天销量']
        growth_rate = row['销量环比']
        ad_exposure = row['15广告曝光']
        ad_clicks = row['15广告点击']
        revenue_15d = row['15天销售额']
        
        reasons = []
        
        if sales_15d == 0:
            reasons.append('新品或低曝光期')
        elif sales_15d <= 3:
            reasons.append('起步阶段，增长空间大')
        
        if isinstance(growth_rate, str) and '%' in growth_rate:
            try:
                growth = float(growth_rate.replace('%', ''))
                if growth >= 50:
                    reasons.append(f'销量环比增长{growth_rate}，增长迅猛')
                elif growth >= 20:
                    reasons.append(f'销量环比增长{growth_rate}，稳步上升')
            except:
                pass
        
        if ad_clicks > 0 and sales_15d == 0:
            reasons.append('有广告点击但未转化，优化空间大')
        elif ad_exposure > 1000 and sales_15d == 0:
            reasons.append('曝光量充足，需优化转化')
        
        if revenue_15d >= 100 and sales_15d <= 5:
            reasons.append('单价较高，利润空间大')
        
        if not reasons:
            reasons.append('数据表现平稳')
        
        return '; '.join(reasons)
    
    def get_high_potential_skus(self):
        if self.predicted_df is None:
            self.predict()
        return self.predicted_df[self.predicted_df['潜力等级'].isin(['高潜力', '中潜力'])]
    
    def get_new_product_opportunities(self):
        if self.predicted_df is None:
            self.predict()
        return self.predicted_df[
            (self.predicted_df['15天销量'] == 0) & 
            (self.predicted_df['潜力等级'].isin(['高潜力', '中潜力']))
        ]
