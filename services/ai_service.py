from typing import List, Dict, Optional
from config import Config
import json

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("警告: openai未安装，将使用模拟AI分析模式")

class AIService:
    def __init__(self):
        self.client = None
        if HAS_OPENAI and Config.OPENAI_API_KEY:
            try:
                self.client = OpenAI(
                    api_key=Config.OPENAI_API_KEY,
                    base_url=Config.OPENAI_BASE_URL
                )
            except Exception as e:
                print(f"初始化OpenAI客户端失败: {e}")
        self.model = Config.OPENAI_MODEL
    
    def analyze_stock(self, stock_code: str, stock_name: str, stock_data: Dict) -> Dict:
        if not self.client:
            return self._mock_analysis(stock_code, stock_name, stock_data)
        
        try:
            prompt = self._build_analysis_prompt(stock_code, stock_name, stock_data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的股票分析师，擅长分析A股市场龙头股。请用简洁专业的语言进行分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'analysis': analysis_text,
                'recommendation': self._extract_recommendation(analysis_text),
                'confidence': self._calculate_confidence(stock_data)
            }
        except Exception as e:
            print(f"AI分析失败: {e}")
            return self._mock_analysis(stock_code, stock_name, stock_data)
    
    def batch_analyze_stocks(self, stocks: List[Dict]) -> List[Dict]:
        results = []
        for stock in stocks:
            analysis = self.analyze_stock(
                stock.get('code'),
                stock.get('name'),
                stock
            )
            results.append(analysis)
        return results
    
    def _build_analysis_prompt(self, stock_code: str, stock_name: str, stock_data: Dict) -> str:
        prompt = f"""
请分析以下股票是否具备龙头股特征：

股票代码: {stock_code}
股票名称: {stock_name}
当前价格: {stock_data.get('price', 'N/A')}
涨跌幅: {stock_data.get('change_pct', 'N/A')}%
量比: {stock_data.get('volume_ratio', 'N/A')}
换手率: {stock_data.get('turnover_rate', 'N/A')}%
总市值: {stock_data.get('market_cap', 'N/A')}亿
综合得分: {stock_data.get('score', 'N/A')}

请从以下维度进行分析：
1. 市场表现分析（涨跌幅、成交量、换手率）
2. 龙头股特征判断（是否具备板块带动效应）
3. 风险提示
4. 投资建议（买入/观望/卖出）

请给出简洁专业的分析结论。
"""
        return prompt
    
    def _extract_recommendation(self, analysis_text: str) -> str:
        if '买入' in analysis_text:
            return '买入'
        elif '卖出' in analysis_text:
            return '卖出'
        else:
            return '观望'
    
    def _calculate_confidence(self, stock_data: Dict) -> float:
        confidence = 0.5
        
        change_pct = stock_data.get('change_pct', 0)
        if change_pct > 5:
            confidence += 0.2
        elif change_pct > 2:
            confidence += 0.1
        
        volume_ratio = stock_data.get('volume_ratio', 0)
        if volume_ratio > 2:
            confidence += 0.15
        elif volume_ratio > 1.5:
            confidence += 0.1
        
        turnover_rate = stock_data.get('turnover_rate', 0)
        if 5 < turnover_rate < 15:
            confidence += 0.15
        
        return min(confidence, 1.0)
    
    def _mock_analysis(self, stock_code: str, stock_name: str, stock_data: Dict = None) -> Dict:
        if stock_data is None:
            stock_data = {}
        
        change_pct = stock_data.get('change_pct', 0)
        volume_ratio = stock_data.get('volume_ratio', 0)
        turnover_rate = stock_data.get('turnover_rate', 0)
        score = stock_data.get('score', 0)
        
        if change_pct > 5 and volume_ratio > 2:
            recommendation = '买入'
            analysis = f"""【{stock_name}({stock_code})分析报告】

1. 市场表现分析：
   该股票今日表现强势，涨幅达{change_pct:.2f}%，量比{volume_ratio:.2f}，显示资金大幅流入。
   换手率{turnover_rate:.2f}%，成交活跃，市场关注度高。

2. 龙头股特征判断：
   该股具备明显的龙头特征：
   - 涨幅居前，带动板块效应明显
   - 量能放大，资金持续流入
   - 综合得分{score:.1f}分，排名靠前

3. 风险提示：
   - 短期涨幅较大，注意回调风险
   - 关注大盘走势及板块轮动
   - 建议设置止损位

4. 投资建议：买入
   该股技术面强势，资金面配合，建议逢低布局。
"""
        elif change_pct > 2:
            recommendation = '观望'
            analysis = f"""【{stock_name}({stock_code})分析报告】

1. 市场表现分析：
   该股票今日上涨{change_pct:.2f}%，量比{volume_ratio:.2f}，表现相对稳健。
   换手率{turnover_rate:.2f}%，交投活跃度一般。

2. 龙头股特征判断：
   该股具备一定龙头特征，但力度不够：
   - 涨幅尚可，但未形成明显带动效应
   - 量能一般，需观察后续资金动向
   - 综合得分{score:.1f}分

3. 风险提示：
   - 关注板块整体走势
   - 注意量能变化
   - 警惕大盘系统性风险

4. 投资建议：观望
   建议等待更明确的信号，关注回调后的低吸机会。
"""
        else:
            recommendation = '观望'
            analysis = f"""【{stock_name}({stock_code})分析报告】

1. 市场表现分析：
   该股票今日表现一般，涨跌幅{change_pct:.2f}%，量比{volume_ratio:.2f}。
   换手率{turnover_rate:.2f}%，市场关注度较低。

2. 龙头股特征判断：
   该股目前龙头特征不明显：
   - 涨幅落后，未能带动板块
   - 量能不足，资金参与度低
   - 综合得分{score:.1f}分

3. 风险提示：
   - 短期缺乏上涨动力
   - 关注基本面变化
   - 注意市场整体风险

4. 投资建议：观望
   建议暂时观望，等待更好的入场时机。
"""
        
        return {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'analysis': analysis,
            'recommendation': recommendation,
            'confidence': self._calculate_confidence(stock_data)
        }
    
    def generate_market_summary(self, leader_stocks: List[Dict]) -> str:
        if not self.client:
            return self._mock_market_summary(leader_stocks)
        
        try:
            stocks_info = "\n".join([
                f"- {s.get('name')}({s.get('code')}): 涨幅{s.get('change_pct', 0):.2f}%, 得分{s.get('score', 0):.2f}"
                for s in leader_stocks[:10]
            ])
            
            prompt = f"""
以下是今日筛选出的龙头股列表：

{stocks_info}

请生成一份市场总结报告，包括：
1. 今日市场整体表现概述
2. 热门板块分析
3. 龙头股特征总结
4. 后市展望

请用简洁专业的语言撰写。
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的股市分析师，擅长撰写市场分析报告。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"生成市场总结失败: {e}")
            return self._mock_market_summary(leader_stocks)
    
    def _mock_market_summary(self, leader_stocks: List[Dict]) -> str:
        avg_change = sum(s.get('change_pct', 0) for s in leader_stocks) / len(leader_stocks) if leader_stocks else 0
        avg_score = sum(s.get('score', 0) for s in leader_stocks) / len(leader_stocks) if leader_stocks else 0
        
        return f"""【今日龙头股市场总结】

1. 市场表现概述：
   今日市场整体活跃，龙头股平均涨幅{avg_change:.2f}%，平均得分{avg_score:.1f}分。
   资金流向明显集中在强势板块，市场情绪积极。

2. 热门板块分析：
   科技、新能源等板块持续活跃，龙头股带动效应明显。
   人工智能、半导体等板块涨幅居前，资金关注度高。

3. 龙头股特征总结：
   筛选出的龙头股普遍具备以下特征：
   - 涨幅居前，多数涨幅超过3%
   - 量能放大，量比普遍大于1.5
   - 换手活跃，市场参与度高
   - 市值适中，流动性良好

4. 后市展望：
   短期市场有望延续活跃态势，建议关注龙头股的持续性。
   注意风险控制，把握结构性机会，避免追高。
"""
