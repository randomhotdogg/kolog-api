import json
from typing import Dict, Any
import httpx
from fastapi import HTTPException
from datetime import datetime

class GeminiService:
    """Google Gemini AI 分析服務類"""
    
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    
    @staticmethod
    def _create_analysis_prompt(transcript: str) -> str:
        """建立分析 prompt"""
        return f"""
你是一位專業的美股分析師。請仔細分析以下 YouTube 影片逐字稿，識別其中提到的美股股票，並提供投資觀點分析。

逐字稿內容：
{transcript}

## 股票提及類型分類（新增 - 最重要）

請根據上下文判斷每個股票的提及類型：

**主要投資標的（PRIMARY）**：
- 作者明確推薦買入/賣出/持有的股票
- 詳細分析財務表現、業務前景的公司
- 影片的主要討論焦點
- 給出具體投資建議或價格目標

**案例參考（CASE_STUDY）**：
- 作為成功/失敗例子的歷史案例
- 用來說明投資策略或市場趨勢的範例
- "像是..."、"例如..."、"曾經..."等語境

**比較對象（COMPARISON）**：
- 用作行業比較、競爭分析的公司
- 簡單提及但非投資焦點的標的
- "相比之下..."、"跟XX比較..."等語境

**簡單提及（MENTION）**：
- 僅作為背景資訊或順帶提到
- 沒有任何投資含義的提及

## 股票代號識別規則

1. 美股股票代號格式：1-5個大寫英文字母，如 AAPL、MSFT、GOOGL、BRK.B
2. 只識別明確提到的股票代號，不要猜測或推斷
3. 公司名稱不等於股票代號（例如：蘋果公司=AAPL，微軟=MSFT，特斯拉=TSLA）
4. 如果只提到公司名稱而沒有明確代號，請根據常識對應正確代號
5. 不確定的情況下，寧可不識別也不要錯誤識別

## 公司名稱識別規則

除了明確的股票代號，還要識別影片中提及的美股相關公司名稱：
1. 識別所有提及的知名美股公司名稱
2. 記錄提及的上下文（前後文內容）
3. 根據提及類型評估信心度和重要性

## 信心度評分標準（新增）

**90-100分**：主要投資標的，有詳細分析和明確建議
**70-89分**：重要案例研究，有投資價值討論
**50-69分**：比較對象，有一定分析價值
**30-49分**：簡單提及，投資參考價值低
**10-29分**：純粹舉例或背景提及

## 回答格式

請按照以下 JSON 格式回答，不要包含任何額外的文字。**重要**：所有中文文字與英文/數字之間必須加空格：

{{
  "summary": "影片內容摘要（100-200字）",
  "stockAnalyses": [
    {{
      "symbol": "股票代號（必須是1-5個大寫英文字母）",
      "companyName": "完整公司名稱",
      "mentionType": "PRIMARY/CASE_STUDY/COMPARISON/MENTION",
      "sentiment": "bullish/bearish/neutral",
      "confidence": 信心度數字(0-100),
      "reasoning": "分析理由和依據（50-100字）",
      "keyPoints": ["具體論點1", "具體論點2", "具體論點3"],
      "identificationReason": "為什麼識別出這個股票代號的理由",
      "contextQuote": "原文中相關的關鍵句子（20-50字）"
    }}
  ],
  "mentionedCompanies": [
    {{
      "companyName": "公司名稱（如：蘋果公司、特斯拉、微軟等）",
      "context": "提及的上下文內容（20-50字的前後文）",
      "mentionType": "PRIMARY/CASE_STUDY/COMPARISON/MENTION", 
      "confidence": 信心度數字(0-100)
    }}
  ],
  "overallSentiment": "bullish/bearish/neutral"
}}

## 範例說明

**文字格式範例**（重要）：
- 正確：「AAPL 股價持續上漲，Q3 財報表現亮眼，上漲 15%」
- 錯誤：「AAPL股價持續上漲，Q3財報表現亮眼，上漲15%」

**主要投資標的範例**：
- "我強烈推薦買入蘋果公司..." → mentionType: "PRIMARY", confidence: 90+
- "SFM 是我目前最看好的股票..." → mentionType: "PRIMARY", confidence: 85+

**案例參考範例**：
- "就像特斯拉當年一樣..." → mentionType: "CASE_STUDY", confidence: 60-70
- "Beyond Meat 的失敗告訴我們..." → mentionType: "CASE_STUDY", confidence: 50-60

**比較對象範例**：
- "相較於亞馬遜，這家公司..." → mentionType: "COMPARISON", confidence: 40-50
- "跟 Nvidia 比護城河..." → mentionType: "COMPARISON", confidence: 30-40

## 嚴格要求

1. symbol 必須是有效的美股代號格式（1-5個大寫字母）
2. 只有非常確定的股票才加入 stockAnalyses
3. mentionType 必須是四種類型之一
4. 根據 mentionType 調整 confidence 分數
5. PRIMARY 類型的股票應該有更詳細的 reasoning 和 keyPoints
6. 避免重複：如果已在 stockAnalyses 中的公司，不要再加入 mentionedCompanies
7. sentiment 只能是 "bullish"、"bearish"、"neutral" 其中一個
8. confidence 必須是 0-100 的整數
9. 必須返回有效的 JSON 格式
10. **文字格式要求**：所有中文輸出（包括 summary、reasoning、keyPoints、context 等）必須確保中文與英文/數字之間有空格，例如：「AAPL 股價」、「上漲 15%」、「Q3 財報」
"""

    @staticmethod
    async def analyze_transcript(transcript: str, api_key: str, video_url: str) -> Dict[str, Any]:
        """使用 Google Gemini API 分析影片逐字稿"""
        try:
            analysis_prompt = GeminiService._create_analysis_prompt(transcript)
            
            request_body = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": analysis_prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "topK": 32,
                    "topP": 1,
                    "maxOutputTokens": 2048,
                },
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{GeminiService.GEMINI_API_URL}?key={api_key}",
                    headers={"Content-Type": "application/json"},
                    json=request_body,
                    timeout=30.0
                )
                
                if not response.is_success:
                    if response.status_code == 400:
                        raise HTTPException(
                            status_code=400,
                            detail="API Key 無效或請求格式錯誤"
                        )
                    elif response.status_code == 429:
                        raise HTTPException(
                            status_code=429,
                            detail="API 請求次數已達上限，請稍後再試"
                        )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="Google Gemini API 暫時無法使用"
                        )
                
                gemini_data = response.json()
                
                # 提取 AI 回應內容
                ai_response = gemini_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
                
                if not ai_response:
                    raise HTTPException(
                        status_code=500,
                        detail="AI 分析服務返回了空的回應"
                    )
                
                # 解析 AI 的 JSON 回應
                try:
                    # 清理 AI 回應中可能的多餘字符
                    import re
                    # 移除可能的 markdown 代碼塊標記
                    cleaned_response = re.sub(r'```json\s*', '', ai_response)
                    cleaned_response = re.sub(r'\s*```', '', cleaned_response)
                    cleaned_response = cleaned_response.strip()
                    
                    # 額外清理，以防有殘留的標記
                    if cleaned_response.startswith('```json'):
                        cleaned_response = cleaned_response[7:].strip()
                    if cleaned_response.endswith('```'):
                        cleaned_response = cleaned_response[:-3].strip()
                    
                    analysis_result = json.loads(cleaned_response)
                except json.JSONDecodeError as parse_error:
                    raise HTTPException(
                        status_code=500,
                        detail="AI 分析結果格式錯誤，請稍後再試"
                    )
                
                # 驗證分析結果格式
                if not analysis_result.get('summary') or not isinstance(analysis_result.get('stockAnalyses'), list):
                    raise HTTPException(
                        status_code=500,
                        detail="AI 分析結果格式不完整"
                    )
                
                # 股票代號格式驗證
                def is_valid_stock_symbol(symbol: str) -> bool:
                    if not symbol or not isinstance(symbol, str):
                        return False
                    # 美股代號格式：1-5個大寫字母，可能包含一個點
                    import re
                    stock_symbol_regex = r'^[A-Z]{1,5}(\.[A-Z])?$'
                    return bool(re.match(stock_symbol_regex, symbol.strip().upper()))
                
                # 過濾和驗證股票分析結果
                valid_stock_analyses = []
                for analysis in analysis_result.get('stockAnalyses', []):
                    # 基本欄位檢查
                    has_required_fields = (
                        analysis.get('symbol') and
                        analysis.get('companyName') and
                        analysis.get('sentiment') in ['bullish', 'bearish', 'neutral'] and
                        isinstance(analysis.get('confidence'), int) and
                        0 <= analysis.get('confidence', -1) <= 100
                    )
                    
                    # 股票代號格式檢查
                    has_valid_symbol = is_valid_stock_symbol(analysis.get('symbol', ''))
                    
                    if has_required_fields and has_valid_symbol:
                        # 轉換為 Pydantic 期望的格式 (使用 alias 欄位名稱)
                        formatted_analysis = {
                            'symbol': analysis['symbol'].strip().upper(),
                            'company_name': analysis.get('companyName'),
                            'mention_type': analysis.get('mentionType'),
                            'sentiment': analysis.get('sentiment'),
                            'confidence': analysis.get('confidence'),
                            'reasoning': analysis.get('reasoning', ''),
                            'key_points': analysis.get('keyPoints', []),
                            'identification_reason': analysis.get('identificationReason'),
                            'context_quote': analysis.get('contextQuote')
                        }
                        valid_stock_analyses.append(formatted_analysis)
                
                # 轉換 mentionedCompanies 格式
                mentioned_companies = []
                for company in analysis_result.get('mentionedCompanies', []):
                    formatted_company = {
                        'company_name': company.get('companyName'),
                        'context': company.get('context', ''),
                        'mention_type': company.get('mentionType'),
                        'confidence': company.get('confidence', 0)
                    }
                    mentioned_companies.append(formatted_company)
                
                # 轉換欄位名稱為 Pydantic 模型期望的格式 (使用 alias)
                formatted_analysis = {
                    'video_title': analysis_result.get('videoTitle'),
                    'summary': analysis_result.get('summary'),
                    'stock_analyses': valid_stock_analyses,
                    'mentioned_companies': mentioned_companies,
                    'overall_sentiment': analysis_result.get('overallSentiment'),
                    'video_url': video_url,
                    'analyzed_at': datetime.now().isoformat()
                }
                
                return {
                    'success': True,
                    'analysis': formatted_analysis
                }
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail="無法連接到 AI 分析服務，請檢查網路連線"
            )