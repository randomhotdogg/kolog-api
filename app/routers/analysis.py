from fastapi import APIRouter, HTTPException
from models.schemas import AnalysisRequest, AnalysisResponse, ErrorResponse
from services.gemini_service import GeminiService

router = APIRouter()

@router.post("/analysis/gemini",
             response_model=AnalysisResponse,
             responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze_with_gemini(request: AnalysisRequest):
    """
    使用 Google Gemini AI 分析影片逐字稿
    
    - **transcript**: 影片逐字稿文本內容
    - **api_key**: Google Gemini API Key
    - **video_url**: YouTube 影片 URL
    
    返回 AI 分析結果，包含股票分析、投資觀點和市場情緒
    """
    try:
        result = await GeminiService.analyze_transcript(
            request.transcript,
            request.api_key,
            str(request.video_url)
        )
        
        return AnalysisResponse(
            success=True,
            analysis=result['analysis']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"伺服器內部錯誤: {str(e)}"
        )