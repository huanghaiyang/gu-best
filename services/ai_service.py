from typing import List, Dict
import requests

class AIService:
    def __init__(self):
        self.model = None
        self.api_config = None
        self.params = None
    
    def set_model_config(self, model_type, api_config, params):
        """设置模型配置"""
        self.model = model_type
        self.api_config = api_config
        self.params = params
    
    def _make_chat_request(self, messages, temperature=0.7, max_tokens=1000):
        """统一的REST API请求方法"""
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            # 根据不同的模型设置请求头和请求体
            if self.model == 'openai':
                headers['Authorization'] = f"Bearer {self.api_config.get('apiKey')}"
                data = {
                    'model': self.api_config.get('model'),
                    'messages': messages,
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
                response = requests.post(
                    f"{self.api_config.get('apiUrl')}/chat/completions",
                    json=data,
                    headers=headers,
                    timeout=30
                )
                
            elif self.model == 'claude':
                headers['x-api-key'] = self.api_config.get('apiKey')
                headers['anthropic-version'] = '2023-06-01'
                data = {
                    'model': self.api_config.get('model'),
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'messages': messages
                }
                response = requests.post(
                    f"{self.api_config.get('apiUrl')}/messages",
                    json=data,
                    headers=headers,
                    timeout=30
                )
                
            elif self.model == 'gemini':
                headers['Authorization'] = f"Bearer {self.api_config.get('apiKey')}"
                # Gemini的API格式不同，需要转换消息格式
                prompt = '\n'.join([msg['content'] for msg in messages])
                data = {
                    'contents': [{'parts': [{'text': prompt}]}],
                    'generationConfig': {
                        'temperature': temperature,
                        'maxOutputTokens': max_tokens
                    }
                }
                response = requests.post(
                    f"{self.api_config.get('apiUrl')}/models/{self.api_config.get('model')}:generateContent",
                    json=data,
                    headers=headers,
                    timeout=30
                )
                
            elif self.model == 'qwen':
                headers['Authorization'] = f"Bearer {self.api_config.get('apiKey')}"
                data = {
                    'model': self.api_config.get('model'),
                    'input': {
                        'messages': messages
                    },
                    'parameters': {
                        'temperature': temperature,
                        'max_tokens': max_tokens
                    }
                }
                response = requests.post(
                    self.api_config.get('apiUrl'),
                    json=data,
                    headers=headers,
                    timeout=30
                )
                
            elif self.model == 'ernie':
                # 文心一言需要access_token
                headers['Content-Type'] = 'application/json'
                data = {
                    'messages': messages,
                    'temperature': temperature,
                    'max_output_tokens': max_tokens
                }
                # 文心一言需要先获取access_token
                token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_config.get('apiKey')}&client_secret={self.api_config.get('secretKey', '')}"
                token_response = requests.post(token_url, timeout=10)
                if token_response.status_code == 200:
                    access_token = token_response.json().get('access_token')
                    headers['Authorization'] = f"Bearer {access_token}"
                    response = requests.post(
                        self.api_config.get('apiUrl'),
                        json=data,
                        headers=headers,
                        timeout=30
                    )
                else:
                    raise Exception("获取文心一言access_token失败")
                    
            elif self.model == 'volcengine':
                headers['Authorization'] = f"Bearer {self.api_config.get('apiKey')}"
                # 豆包API的正确请求格式（Responses API）
                data = {
                    'model': self.api_config.get('model'),
                    'input': messages,
                    'max_output_tokens': max_tokens,
                    'temperature': temperature
                }
                response = requests.post(
                    self.api_config.get('apiUrl'),
                    json=data,
                    headers=headers,
                    timeout=30
                )
                
            else:
                raise Exception(f"不支持的模型类型: {self.model}")
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API请求失败，状态码: {response.status_code}, 响应: {response.text}")
                
        except Exception as e:
            raise Exception(f"REST API请求失败: {str(e)}")
    
    def analyze_stock(self, stock_code: str, stock_name: str, stock_data: Dict) -> Dict:
        if not self.model or not self.api_config:
            return self._mock_analysis(stock_code, stock_name, stock_data)
        
        try:
            prompt = self._build_analysis_prompt(stock_code, stock_name, stock_data)
            
            # 使用用户设置的参数
            temperature = self.params.get('temperature', 0.7) if self.params else 0.7
            max_tokens = self.params.get('maxTokens', 1000) if self.params else 1000
            
            # 构造消息格式
            messages = [
                {"role": "system", "content": "你是一位专业的股票分析师，擅长分析A股市场龙头股。请用简洁专业的语言进行分析。"},
                {"role": "user", "content": prompt}
            ]
            
            # 使用统一的REST API请求
            response_data = self._make_chat_request(messages, temperature, max_tokens)
            
            # 根据不同的模型解析响应
            if self.model == 'openai':
                analysis_text = response_data['choices'][0]['message']['content']
            elif self.model == 'claude':
                analysis_text = response_data['content'][0]['text']
            elif self.model == 'gemini':
                analysis_text = response_data['candidates'][0]['content']['parts'][0]['text']
            elif self.model == 'qwen':
                analysis_text = response_data['output']['text']
            elif self.model == 'ernie':
                analysis_text = response_data['result']
            elif self.model == 'volcengine':
                analysis_text = response_data['choices'][0]['message']['content']
            else:
                return self._mock_analysis(stock_code, stock_name, stock_data)
            
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
        if not self.model or not self.api_config:
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
            
            # 使用用户设置的参数
            temperature = self.params.get('temperature', 0.7) if self.params else 0.7
            max_tokens = self.params.get('maxTokens', 1500) if self.params else 1500
            
            # 构造消息格式
            messages = [
                {"role": "system", "content": "你是一位专业的股市分析师，擅长撰写市场分析报告。"},
                {"role": "user", "content": prompt}
            ]
            
            # 使用统一的REST API请求
            response_data = self._make_chat_request(messages, temperature, max_tokens)
            
            # 根据不同的模型解析响应
            if self.model == 'openai':
                return response_data['choices'][0]['message']['content']
            elif self.model == 'claude':
                return response_data['content'][0]['text']
            elif self.model == 'gemini':
                return response_data['candidates'][0]['content']['parts'][0]['text']
            elif self.model == 'qwen':
                return response_data['output']['text']
            elif self.model == 'ernie':
                return response_data['result']
            elif self.model == 'volcengine':
                return response_data['choices'][0]['message']['content']
            else:
                return self._mock_market_summary(leader_stocks)
                
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
    
    def test_model(self, model: str, params: Dict, api_config: Dict) -> Dict:
        """测试模型配置是否正确"""
        try:
            # 临时设置模型配置用于测试
            original_model = self.model
            original_api_config = self.api_config
            original_params = self.params
            
            self.model = model
            self.api_config = api_config
            self.params = params
            
            # 构造测试消息
            messages = [
                {"role": "system", "content": "你是一个测试助手"},
                {"role": "user", "content": "测试连接，请回复'测试成功'"}
            ]
            
            # 使用统一的REST API请求
            temperature = params.get('temperature', 0.7) if params else 0.7
            max_tokens = params.get('maxTokens', 100) if params else 100
            
            response_data = self._make_chat_request(messages, temperature, max_tokens)
            
            # 根据不同的模型解析响应
            if model == 'openai':
                response_text = response_data['choices'][0]['message']['content']
            elif model == 'claude':
                response_text = response_data['content'][0]['text']
            elif model == 'gemini':
                response_text = response_data['candidates'][0]['content']['parts'][0]['text']
            elif model == 'qwen':
                response_text = response_data['output']['text']
            elif model == 'ernie':
                response_text = response_data['result']
            elif model == 'volcengine':
                # 解析Responses API的响应格式
                for item in response_data.get('output', []):
                    if item.get('type') == 'message' and item.get('role') == 'assistant':
                        for content_item in item.get('content', []):
                            if content_item.get('type') == 'output_text':
                                response_text = content_item.get('text')
                                break
                        break
            else:
                return {'status': 'error', 'message': f'不支持的模型类型: {model}'}
            
            # 恢复原始配置
            self.model = original_model
            self.api_config = original_api_config
            self.params = original_params
            
            return {
                'status': 'success',
                'message': '模型测试成功',
                'response': response_text
            }
            
        except Exception as e:
            # 恢复原始配置
            self.model = original_model
            self.api_config = original_api_config
            self.params = original_params
            
            return {'status': 'error', 'message': f'测试过程中发生错误: {str(e)}'}
