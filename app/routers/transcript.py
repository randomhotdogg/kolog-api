from fastapi import APIRouter, HTTPException
from models.schemas import TranscriptRequest, TranscriptResponse, ErrorResponse
from services.youtube_service import YouTubeService

router = APIRouter()

@router.post("/youtube/transcript", 
             response_model=TranscriptResponse,
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_youtube_transcript(request: TranscriptRequest):
    """
    獲取 YouTube 影片逐字稿
    
    - **url**: YouTube 影片完整 URL
    
    返回影片的逐字稿文本、語言和影片 ID
    """
    try:
        result = await YouTubeService.get_transcript(str(request.url))
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result['error']
            )
        
        return TranscriptResponse(
            success=True,
            transcript=result['transcript'],
            language=result['language'],
            video_id=result['video_id']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"伺服器內部錯誤: {str(e)}"
        )