import pandas as pd
import numpy as np


class SKUEvaluator:
    def __init__(self, sales_df):
        self.sales_df = sales_df
        self.evaluated_df = None
    
    def evaluate_all(self):
        self.evaluated_df = self.sales_df.copy()
        self.evaluated_df['投放评分'] = self.sales_df.apply(self._calculate_score, axis=1)
        self.evaluated_df['投放优先级'] = self._assign_priority(self.evaluated_df['投放评分'])
        self.evaluated_df['推荐广告类型'] = self.sales_df.apply(self._recommend_ad_type, axis=1)
        self.evaluated_df['建议预算占比'] = self.sales_df.apply(self._calculate_budget_ratio, axis=1)
        return self.evaluated_df
    
    def _calculate_score(self, row):
        score = 0
        
        sales_15d = row['15天销量']
        sales_30d = row['30天销量']
        growth_rate = row['销量环比']
        revenue_15d = row['15天销售额']
        ad_revenue_15d = row['15广告销售额(去重）']
        ad_orders_15d = row['15广告订单(光环）']
        total_ad_cost = row['15总广告费']
        
        if sales_15d >= 10:
            score += 25
        elif sales_15d >= 5:
            score += 15
        elif sales_15d >= 1:
            score += 5
        
        if sales_30d >= sales_15d * 1.5:
            score += 15
        elif sales_30d >= sales_15d:
            score += 10
        
        if isinstance(growth_rate, str) and '%' in growth_rate:
            try:
                growth = float(growth_rate.replace('%', ''))
                if growth >= 50:
                    score += 20
                elif growth >= 20:
                    score += 10
                elif growth < -20:
                    score -= 10
            except:
                pass
        
        if revenue_15d >= 500:
            score += 20
        elif revenue_15d >= 200:
            score += 10
        
        if ad_orders_15d > 0 and total_ad_cost > 0:
            roas = ad_revenue_15d / total_ad_cost
            if roas >= 5:
                score += 20
            elif roas >= 3:
                score += 10
        
        return min(score, 100)
    
    def _assign_priority(self, scores):
        conditions = [
            scores >= 80,
            scores >= 60,
            scores >= 40,
            scores >= 20,
            scores < 20
        ]
        choices = ['A', 'B', 'C', 'D', 'E']
        return np.select(conditions, choices, default='E')
    
    def _recommend_ad_type(self, row):
        sales_15d = row['15天销量']
        conversion_rate = row.get('转化率', 0)
        
        if sales_15d == 0:
            return 'PLG为主，先测试曝光'
        elif sales_15d < 5:
            return 'PLG为主，PLP辅助'
        elif sales_15d >= 10:
            if conversion_rate >= 0.02:
                return 'PLP为主，最大化转化'
            else:
                return 'PLG+PLP组合，优化转化'
        else:
            return 'PLG+PLP组合'
    
    def _calculate_budget_ratio(self, row):
        score = self._calculate_score(row)
        if score >= 80:
            return 0.15
        elif score >= 60:
            return 0.10
        elif score >= 40:
            return 0.05
        elif score >= 20:
            return 0.02
        else:
            return 0.0
    
    def get_top_skus(self, n=20):
        if self.evaluated_df is None:
            self.evaluate_all()
        return self.evaluated_df.sort_values('投放评分', ascending=False).head(n)
    
    def get_low_priority_skus(self):
        if self.evaluated_df is None:
            self.evaluate_all()
        return self.evaluated_df[self.evaluated_df['投放优先级'] == 'E']
