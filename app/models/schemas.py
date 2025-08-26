from pydantic import BaseModel, HttpUrl, Field, EmailStr
from typing import List, Optional, Literal
from datetime import datetime

# 基本回應模型
class BaseResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class ErrorResponse(BaseResponse):
    error: str
    success: bool = False

# YouTube 逐字稿相關模型
class TranscriptRequest(BaseModel):
    url: HttpUrl = Field(..., description="YouTube 影片 URL")

class TranscriptResponse(BaseResponse):
    transcript: Optional[str] = None
    language: Optional[str] = None
    video_id: Optional[str] = None
    success: bool = True

# YouTube 元數據相關模型
class MetadataRequest(BaseModel):
    video_id: str = Field(..., description="YouTube 影片 ID")
    api_key: str = Field(..., description="YouTube Data API Key")

class YouTubeThumbnail(BaseModel):
    url: str

class YouTubeThumbnails(BaseModel):
    default: YouTubeThumbnail
    medium: YouTubeThumbnail
    high: YouTubeThumbnail

class YouTubeMetadata(BaseModel):
    video_id: str
    title: str
    published_at: str
    description: str
    channel_title: str
    thumbnails: YouTubeThumbnails

class MetadataResponse(BaseResponse):
    metadata: Optional[YouTubeMetadata] = None
    publish_date: Optional[str] = None
    success: bool = True

# AI 分析相關模型
class AnalysisRequest(BaseModel):
    transcript: str = Field(..., description="影片逐字稿內容")
    api_key: str = Field(..., description="Google Gemini API Key")
    video_url: HttpUrl = Field(..., description="YouTube 影片 URL")

class StockAnalysis(BaseModel):
    symbol: str
    companyName: str = Field(..., alias="company_name")
    mentionType: Optional[Literal["PRIMARY", "CASE_STUDY", "COMPARISON", "MENTION"]] = Field(None, alias="mention_type")
    sentiment: Literal["bullish", "bearish", "neutral"]
    confidence: int = Field(..., ge=0, le=100)
    reasoning: str
    keyPoints: List[str] = Field(..., alias="key_points")
    identificationReason: Optional[str] = Field(None, alias="identification_reason")
    contextQuote: Optional[str] = Field(None, alias="context_quote")

class MentionedCompany(BaseModel):
    companyName: str = Field(..., alias="company_name")
    context: str
    mentionType: Optional[Literal["PRIMARY", "CASE_STUDY", "COMPARISON", "MENTION"]] = Field(None, alias="mention_type")
    confidence: int = Field(..., ge=0, le=100)

class GeminiAnalysisResult(BaseModel):
    videoTitle: Optional[str] = Field(None, alias="video_title")
    summary: str
    stockAnalyses: List[StockAnalysis] = Field(..., alias="stock_analyses")
    mentionedCompanies: Optional[List[MentionedCompany]] = Field(None, alias="mentioned_companies")
    overallSentiment: Literal["bullish", "bearish", "neutral"] = Field(..., alias="overall_sentiment")
    videoUrl: HttpUrl = Field(..., alias="video_url")
    analyzedAt: datetime = Field(..., alias="analyzed_at")

class AnalysisResponse(BaseResponse):
    analysis: Optional[GeminiAnalysisResult] = None
    success: bool = True

# 認證相關 schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class GoogleAuthRequest(BaseModel):
    token: str

# 股票追蹤相關 schemas
class UserStockCreate(BaseModel):
    symbol: str
    company_name: str
    custom_name: Optional[str] = None
    start_tracking_date: datetime
    start_price: float
    currency: str
    youtube_analysis: Optional[str] = None  # JSON 字串

class UserStockResponse(BaseModel):
    id: int
    symbol: str
    company_name: str
    custom_name: Optional[str] = None
    start_tracking_date: datetime
    start_price: float
    currency: str
    youtube_analysis: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True