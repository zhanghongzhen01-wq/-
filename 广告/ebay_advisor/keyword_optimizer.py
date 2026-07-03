import pandas as pd
import numpy as np


class KeywordOptimizer:
    def __init__(self, ad_df):
        self.ad_df = ad_df
        self.optimized_df = None

    def optimize(self):
        self.optimized_df = self.ad_df.copy()
        self.optimized_df['建议操作'] = self.ad_df.apply(self._determine_action, axis=1)
        self.optimized_df['优化建议'] = self.ad_df.apply(self._generate_suggestion, axis=1)
        return self.optimized_df

    def _sf(self, v):
        try:
            return float(v) if v and not pd.isna(v) else 0.0
        except:
            return 0.0

    # ============================================================
    #  决策树核心
    # ============================================================
    def _determine_action(self, row):
        impressions = self._sf(row.get('Impressions'))
        clicks = self._sf(row.get('Clicks'))
        sales = self._sf(row.get('Sales'))
        acos = self._sf(row.get('ACOS'))
        roas = self._sf(row.get('ROAS'))
        ad_fees = self._sf(row.get('Ad Fees'))
        status = str(row.get('Status', '')).upper().strip()
        keyword = str(row.get('Keyword', '')).strip()

        if not keyword:
            return '无数据'

        # PAUSED
        if status == 'PAUSED':
            if sales > 0 and roas > 3:
                return '建议重启'
            return '保持暂停'

        # ── 第一阶段：曝光期 ──
        if impressions < 100:
            return '观察'

        # ── 第二阶段：曝光→点击断层 ──
        # PLP按点击收费，曝光不花钱，零点击≠浪费，继续观察
        if clicks == 0:
            return '观察'

        # ── 第三阶段：点击→转化断层 ──
        if sales == 0:
            if clicks >= 15 and ad_fees >= 3:
                return '空烧关停'       # 来了15+人没一个买，还花了≥$3
            if clicks >= 15 and ad_fees < 3:
                return '观察+优化listing' # 流量来了没接住，检查listing
            return '观察'                # 点击<15，样本不够

        # ── 第四阶段：有转化，ACoS定生死 ──
        if acos > 0:
            if acos <= 0.15:
                return '追加预算'
            elif acos <= 0.30:
                return '保持'
            elif acos <= 0.60:
                return '降价优化'
            elif acos <= 1.00:
                return '降价优化'       # 30-100%都需优化
            else:
                return '空烧关停'       # ACoS > 100%
        else:
            # 有销量但ACoS=0（无广告费数据），保守保持
            return '保持'

        return '保持'

    # ============================================================
    #  建议文案
    # ============================================================
    def _generate_suggestion(self, row):
        action = row.get('建议操作', '')
        impressions = self._sf(row.get('Impressions'))
        clicks = self._sf(row.get('Clicks'))
        sales = self._sf(row.get('Sales'))
        acos = self._sf(row.get('ACOS'))
        roas = self._sf(row.get('ROAS'))
        ad_fees = self._sf(row.get('Ad Fees'))

        if action == '空烧关停':
            parts = []
            if impressions >= 500 and clicks == 0:
                parts.append(f'{int(impressions)}次曝光零点击，关键词不匹配搜索意图')
            elif sales == 0:
                if clicks >= 15:
                    parts.append(f'{int(clicks)}次点击零转化，花费${ad_fees:.2f}')
                if acos > 1.0:
                    parts.append(f'ACoS={acos:.0%}，越投越亏')
            parts.append('建议暂停或删除')
            return '; '.join(parts)

        if action == '追加预算':
            return f'ACoS仅{acos:.0%}，ROAS={roas:.1f}x；建议提高出价20-30%或增加日预算'

        if action == '保持':
            return f'ACoS={acos:.0%}，在健康区间内，维持当前策略'

        if action == '降价优化':
            return f'ACoS={acos:.0%}偏高；建议降低出价15-25%，1周后复查'

        if action == '观察':
            if impressions < 100:
                return f'曝光仅{int(impressions)}次，刚上线，继续观察7-14天'
            if clicks < 15 and sales == 0:
                return f'仅{int(clicks)}次点击，样本不足，继续观察'
            if 100 <= impressions < 500 and clicks == 0:
                return f'曝光{int(impressions)}次但无点击，可能出价偏低，建议小幅提价测试'
            return '数据积累中，继续观察'

        if action == '观察+优化listing':
            return f'{int(clicks)}次点击但零转化（花费${ad_fees:.2f}）；流量没问题但listing接不住，检查主图/价格/描述'

        if action == '建议重启':
            return f'暂停前有{sales:.0f}单成交，ROAS={roas:.1f}x；建议以原出价70%重启测试'

        if action == '保持暂停':
            return '已暂停且无足够恢复数据'

        return ''

    # ============================================================
    #  对外查询接口
    # ============================================================
    def get_shutdown_list(self, limit=None):
        if self.optimized_df is None:
            self.optimize()
        result = self.optimized_df[
            (self.optimized_df['建议操作'] == '空烧关停') &
            (self.optimized_df['Status'].astype(str).str.upper().str.strip() != 'PAUSED')
        ]
        return result.head(limit) if limit else result

    def get_expand_list(self):
        if self.optimized_df is None:
            self.optimize()
        return self.optimized_df[self.optimized_df['建议操作'] == '追加预算']

    def get_optimize_list(self):
        """降价优化的词组"""
        if self.optimized_df is None:
            self.optimize()
        return self.optimized_df[self.optimized_df['建议操作'] == '降价优化']

    def get_suggested_keywords(self):
        """基于追加预算和保持的优质词，生成新词组建议"""
        expand = self.get_expand_list()
        maintain = self.optimized_df[self.optimized_df['建议操作'] == '保持'].head(10) if self.optimized_df is not None else pd.DataFrame()

        source = pd.concat([expand, maintain]) if len(maintain) > 0 else expand
        if len(source) == 0:
            return pd.DataFrame(columns=['原始关键词', '建议关键词', '建议原因'])

        suggested = []
        seen = set()

        for _, row in source.iterrows():
            kw = str(row.get('Keyword', '')).strip()
            if not kw or len(kw) < 3:
                continue

            # 从Campaign名提取产品属性（如 "1寸" "Softail" "Touring"）
            campaign = str(row.get('Campaign', ''))
            parts = campaign.split('#')
            attrs = [p.strip() for p in parts
                     if len(p.strip()) >= 2 and len(p.strip()) <= 20
                     and p.strip() not in
                     ('摩配A', '大小词', '手动广告', '自动', '手动', '词组', '精准', '宽泛',
                      '关掉PLG', '关掉PLP')]

            # 属性+关键词组合
            for attr in attrs[:3]:
                if attr.lower() not in kw.lower():
                    new = f'{attr} {kw}'.strip()
                    if new not in seen:
                        seen.add(new)
                        suggested.append({
                            '原始关键词': kw,
                            '建议关键词': new,
                            '建议原因': f'添加产品属性「{attr}」提高精准度'
                        })

            # 词组匹配 → 精确匹配变体
            kw_parts = kw.split()
            if len(kw_parts) >= 2:
                exact = f'[{kw}]'
                if exact not in seen:
                    seen.add(exact)
                    suggested.append({
                        '原始关键词': kw,
                        '建议关键词': exact,
                        '建议原因': '切换为精确匹配减少无效曝光'
                    })

        # 兜底：给表现好的词加基础后缀
        if len(suggested) < 5 and len(expand) > 0:
            defaults = ['for harley', 'replacement', 'aftermarket']
            for _, row in expand.head(3).iterrows():
                kw = str(row.get('Keyword', '')).strip()
                for suffix in defaults:
                    if suffix not in kw.lower():
                        new = f'{kw} {suffix}'
                        if new not in seen:
                            seen.add(new)
                            suggested.append({
                                '原始关键词': kw,
                                '建议关键词': new,
                                '建议原因': '基础长尾拓展'
                            })

        return pd.DataFrame(suggested) if suggested else pd.DataFrame(columns=['原始关键词', '建议关键词', '建议原因'])

    def recommend_for_sku(self, sku, ad_df, sku_evaluator=None, sales_df=None):
        """基于类目+车型匹配，为指定SKU推荐广告词。
        
        参数:
            sku: SKU编号
            ad_df: load_ad_data() 返回的关键词DataFrame（52k+词）
            sku_evaluator: SKU评分器（获取优先级和推荐广告类型）
            sales_df: 销售数据（获取类目和车型信息）
        
        返回 dict:
            sku_info: SKU基本信息（类目/品牌/车型/优先级）
            existing_keywords: 同Campaign类目下当前在投的高效词
            recommended: 推荐新词 + 匹配类型 + 出价
        """
        import pandas as pd, numpy as np

        # 确保关键词数据已优化
        if self.optimized_df is None:
            self.ad_df = ad_df
            self.optimize()

        # 从销售数据取SKU的类目和车型
        sku_cat = ''
        sku_brand = ''
        sku_model = ''
        priority = '未知'
        ad_type = 'PLP(Advanced)按点击测试'

        if sku_evaluator and sku_evaluator.evaluated_df is not None:
            match = sku_evaluator.evaluated_df[
                sku_evaluator.evaluated_df['SKU'].astype(str) == str(sku)
            ]
            if len(match) > 0:
                row = match.iloc[0]
                sku_cat = str(row.get('三级目录', ''))
                sku_brand = str(row.get('适配品牌', '')).replace('nan', '')
                sku_model = str(row.get('适配车型', '')).replace('nan', '')
                priority = str(row.get('投放优先级', '未知'))
                sales_15d = row.get('15天销量', 0)
                if priority in ('A', 'B'):
                    ad_type = 'PLG(Standard)按成交收割'
                elif sales_15d == 0:
                    ad_type = 'PLP(Advanced)按点击测款'
                else:
                    ad_type = 'PLP+PLG组合'

        # 用类目名匹配Campaign名称
        # 如三级目录="手把" → 找Campaign名称含"手把"的
        cat_keywords = ['手把', '护杠', '后视镜', '脚踏', '刹车', '三星', '置物架', '拉线', '灯架', '减震', '压块']
        matched_cat = sku_cat
        for ck in cat_keywords:
            if ck in sku_cat:
                matched_cat = ck
                break

        # 找同类别Campaign的关键词
        if matched_cat:
            cat_kw = self.optimized_df[
                self.optimized_df['Campaign'].astype(str).str.contains(matched_cat, na=False)
            ]
        else:
            cat_kw = self.optimized_df

        # 车型匹配加分（同品牌同车型Campaign排前面）
        brand_model_kw = pd.DataFrame()
        if sku_brand and sku_brand not in ('', 'nan'):
            brand_model_kw = cat_kw[
                cat_kw['Campaign'].astype(str).str.contains(sku_brand, case=False, na=False)
            ]
            if sku_model and sku_model not in ('', 'nan'):
                brand_model_kw = brand_model_kw[
                    brand_model_kw['Campaign'].astype(str).str.contains(sku_model, case=False, na=False)
                ]

        # 优先用品牌车型匹配的结果，没匹配到就用类目结果
        source_kw = brand_model_kw if len(brand_model_kw) >= 3 else cat_kw

        # 筛选高效词: 有销量 + ACoS<30%
        good_kw = source_kw[
            (source_kw['Sales'] > 0) &
            (pd.notna(source_kw['ACOS'])) &
            (source_kw['ACOS'] < 0.30)
        ].sort_values('Sales', ascending=False).head(10)

        # 若高效词不够，降标准到ACoS<50%
        if len(good_kw) < 3:
            good_kw = source_kw[
                (source_kw['Sales'] > 0) &
                (pd.notna(source_kw['ACOS'])) &
                (source_kw['ACOS'] < 0.50)
            ].sort_values('Sales', ascending=False).head(10)

        recommended = []
        seen = set()
        for _, r in good_kw.iterrows():
            kw = str(r.get('Keyword', '')).strip()
            if not kw or len(kw) < 3 or kw in seen:
                continue
            seen.add(kw)

            sales = int(r.get('Sales', 0))
            acos_val = r.get('ACOS', 0)
            bid = str(r.get('My bid', '0.30 USD'))

            # 三种匹配类型
            for mt, bid_adj in [('BROAD', 0.8), ('PHRASE', 1.0), ('EXACT', 1.2)]:
                try:
                    base_bid = float(bid.replace(' USD', '')) * bid_adj
                    sug_bid = f'{base_bid:.2f} USD'
                except:
                    sug_bid = bid
                recommended.append({
                    'keyword': kw,
                    'match_type': mt,
                    'suggested_bid': sug_bid,
                    'reason': f'同类目「{matched_cat}」高效词(销量{sales}, ACoS{acos_val:.0%})'
                })

            if len(recommended) >= 30:
                break

        # 预算建议
        budget_map = {'A': '$8-12/天', 'B': '$5-8/天', 'C': '$3-5/天', 'D': '$1-3/天', 'E': '$1-2/天'}
        budget = budget_map.get(priority, '$1-3/天')

        return {
            'sku': sku,
            'category': sku_cat,
            'brand': sku_brand,
            'model': sku_model,
            'priority': priority,
            'ad_type': ad_type,
            'budget': budget,
            'matched_campaigns': len(source_kw['Campaign'].unique()) if len(source_kw) > 0 else 0,
            'recommended_count': len(recommended),
            'recommended': recommended
        }
