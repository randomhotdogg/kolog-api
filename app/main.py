from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from routers import transcript, analysis, metadata

# 建立 FastAPI 應用
app = FastAPI(
    title="YouTube Stock Analysis API",
    description="獨立的 Python 後端，提供 YouTube 影片分析和逐字稿服務",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js 開發環境
        "https://your-nextjs-domain.vercel.app",  # 正式環境域名
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(transcript.router, prefix="/api/v1", tags=["transcript"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(metadata.router, prefix="/api/v1", tags=["metadata"])

# 根路由
@app.get("/")
async def root():
    return {
        "message": "YouTube Stock Analysis API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 健康檢查端點
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "youtube-analysis-api"}

# 全域異常處理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "success": False}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "伺服器內部錯誤",
            "success": False,
            "detail": str(exc) if app.debug else None
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )