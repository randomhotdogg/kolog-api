from fastapi import APIRouter, HTTPException
from models.schemas import MetadataRequest, MetadataResponse, ErrorResponse
from services.youtube_service import YouTubeService

router = APIRouter()

@router.post("/youtube/metadata",
             response_model=MetadataResponse,
             responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 
                       404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_youtube_metadata(request: MetadataRequest):
    """
    使用 YouTube Data API v3 獲取影片元數據
    
    - **video_id**: YouTube 影片 ID (11個字符)
    - **api_key**: YouTube Data API Key
    
    返回影片標題、發布日期、頻道名稱等資訊
    """
    try:
        result = await YouTubeService.get_video_metadata(
            request.video_id, 
            request.api_key
        )
        
        return MetadataResponse(
            success=True,
            metadata=result['metadata'],
            publish_date=result['publish_date']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"伺服器內部錯誤: {str(e)}"
        )