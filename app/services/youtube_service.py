import re
import json
from typing import Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import httpx
from fastapi import HTTPException

class YouTubeService:
    """YouTube 相關服務類"""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """從 YouTube URL 提取影片 ID"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None

    @staticmethod
    async def get_transcript(video_url: str) -> Dict[str, Any]:
        """獲取 YouTube 影片的逐字稿"""
        try:
            # 提取影片 ID
            video_id = YouTubeService.extract_video_id(video_url)
            if not video_id:
                return {
                    'success': False,
                    'error': '無效的 YouTube URL'
                }
            
            # 嘗試獲取逐字稿（優先中文，其次英文）
            try:
                ytt_api = YouTubeTranscriptApi()
                transcript_list = ytt_api.list(video_id)
                
                # 嘗試獲取逐字稿的優先順序
                transcript = None
                
                # 1. 優先中文
                for lang in ['zh-TW', 'zh-CN', 'zh']:
                    try:
                        transcript = transcript_list.find_transcript([lang])
                        break
                    except:
                        continue
                
                # 2. 其次英文
                if not transcript:
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                    except:
                        pass
                
                # 3. 最後嘗試任何手動創建的逐字稿
                if not transcript:
                    try:
                        transcript = transcript_list.find_manually_created_transcript(['zh-TW', 'zh-CN', 'zh', 'en'])
                    except:
                        pass
                
                # 4. 最後嘗試任何自動生成的逐字稿
                if not transcript:
                    try:
                        transcript = transcript_list.find_generated_transcript(['zh-TW', 'zh-CN', 'zh', 'en'])
                    except:
                        pass
                
                # 5. 如果還是沒有，嘗試獲取任何可用的逐字稿
                if not transcript:
                    try:
                        # 獲取所有可用的逐字稿語言
                        available_transcripts = list(transcript_list)
                        if available_transcripts:
                            transcript = available_transcripts[0]  # 使用第一個可用的
                        else:
                            return {
                                'success': False,
                                'error': '此影片沒有可用的逐字稿'
                            }
                    except:
                        return {
                            'success': False,
                            'error': '此影片沒有可用的逐字稿'
                        }
                
                # 獲取逐字稿數據
                transcript_data = transcript.fetch()
                
                # 格式化為純文字
                formatter = TextFormatter()
                transcript_text = formatter.format_transcript(transcript_data)
                
                # 檢查逐字稿是否為空
                if not transcript_text or len(transcript_text.strip()) < 10:
                    return {
                        'success': False,
                        'error': '獲取的逐字稿內容過短或為空'
                    }
                
                return {
                    'success': True,
                    'transcript': transcript_text,
                    'language': transcript.language_code,
                    'video_id': video_id
                }
                
            except Exception as e:
                error_msg = str(e)
                if "Could not retrieve a transcript" in error_msg:
                    return {
                        'success': False,
                        'error': '此影片沒有可用的逐字稿（可能是私人影片、已刪除或不支援逐字稿）'
                    }
                elif "no element found" in error_msg:
                    return {
                        'success': False,
                        'error': '影片無法存取或已被移除'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'獲取逐字稿時發生錯誤：{error_msg}'
                    }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'處理 YouTube URL 時發生錯誤：{str(e)}'
            }

    @staticmethod
    async def get_video_metadata(video_id: str, api_key: str) -> Dict[str, Any]:
        """使用 YouTube Data API v3 獲取影片元數據"""
        try:
            youtube_api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(youtube_api_url)
                
                if not response.is_success:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                    
                    if response.status_code == 403:
                        error_message = error_data.get('error', {}).get('message', "")
                        if "quotaExceeded" in error_message:
                            raise HTTPException(
                                status_code=429,
                                detail="YouTube API 配額已用完，請稍後再試或檢查 API Key 限制"
                            )
                        else:
                            raise HTTPException(
                                status_code=403,
                                detail="YouTube API Key 無效或權限不足"
                            )
                    elif response.status_code == 400:
                        raise HTTPException(
                            status_code=400,
                            detail="無效的影片 ID 或 API 請求格式錯誤"
                        )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="YouTube Data API 暫時無法使用"
                        )
                
                data = response.json()
                
                # 檢查是否找到影片
                if not data.get('items') or len(data['items']) == 0:
                    raise HTTPException(
                        status_code=404,
                        detail="找不到指定的 YouTube 影片"
                    )
                
                video_data = data['items'][0]
                snippet = video_data.get('snippet')
                
                if not snippet:
                    raise HTTPException(
                        status_code=500,
                        detail="無法獲取影片詳細資訊"
                    )
                
                # 格式化回傳資料
                metadata = {
                    "video_id": video_id,
                    "title": snippet.get('title', '無標題'),
                    "published_at": snippet.get('publishedAt'),
                    "description": snippet.get('description', ''),
                    "channel_title": snippet.get('channelTitle', '未知頻道'),
                    "thumbnails": {
                        "default": snippet.get('thumbnails', {}).get('default', {"url": ""}),
                        "medium": snippet.get('thumbnails', {}).get('medium', {"url": ""}),
                        "high": snippet.get('thumbnails', {}).get('high', {"url": ""})
                    }
                }
                
                return {
                    'success': True,
                    'metadata': metadata,
                    'publish_date': snippet.get('publishedAt')
                }
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail="無法連接到 YouTube 服務，請檢查網路連線"
            )