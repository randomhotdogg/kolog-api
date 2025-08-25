# YouTube Stock Analysis Backend

獨立的 Python FastAPI 後端服務，專門處理 YouTube 影片分析和逐字稿獲取功能。

## 功能特色

- 🎥 **YouTube 逐字稿獲取**: 支援多語言逐字稿提取
- 🤖 **AI 智能分析**: 整合 Google Gemini AI 進行股票分析
- 📊 **影片元數據**: 獲取 YouTube 影片資訊和發布日期
- 🚀 **高效能 API**: 基於 FastAPI 的異步處理
- 📖 **自動化文檔**: 內建 Swagger UI 和 ReDoc

## API 端點

### YouTube 逐字稿
```
POST /api/v1/youtube/transcript
```
獲取 YouTube 影片的逐字稿內容

### 影片元數據
```
POST /api/v1/youtube/metadata  
```
使用 YouTube Data API 獲取影片資訊

### AI 分析
```
POST /api/v1/analysis/gemini
```
使用 Google Gemini AI 分析影片內容並識別股票

## 快速開始

### 使用 Docker (推薦)

1. 複製環境變數文件：
```bash
cp .env.example .env
```

2. 啟動服務：
```bash
docker-compose up -d
```

3. 查看 API 文檔：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 本地開發

1. 安裝依賴：
```bash
pip install -r requirements.txt
```

2. 啟動開發服務器：
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 環境變數

參考 `.env.example` 文件配置以下變數：

- `ALLOWED_ORIGINS`: CORS 允許的來源域名
- `API_HOST`: API 伺服器主機地址
- `API_PORT`: API 伺服器端口
- `API_DEBUG`: 是否開啟除錯模式
- `LOG_LEVEL`: 日誌等級

## 部署建議

### Railway
1. 連接 GitHub 倉庫
2. 設定環境變數
3. Railway 會自動偵測 Dockerfile 並部署

### DigitalOcean App Platform
1. 建立新的 App
2. 選擇 Docker 容器部署
3. 配置環境變數和域名

### AWS ECS/Fargate
1. 推送 Docker 映像到 ECR
2. 建立 ECS 任務定義
3. 配置 Application Load Balancer

## 健康檢查

服務提供健康檢查端點：
```
GET /health
```

## 錯誤處理

API 統一回傳格式：
```json
{
  "success": false,
  "error": "錯誤訊息",
  "detail": "詳細錯誤資訊（除錯模式才顯示）"
}
```

## 開發說明

專案結構：
```
app/
├── main.py              # FastAPI 主應用
├── models/
│   └── schemas.py       # Pydantic 資料模型
├── routers/
│   ├── transcript.py    # 逐字稿 API 路由
│   ├── metadata.py      # 元數據 API 路由
│   └── analysis.py      # 分析 API 路由
└── services/
    ├── youtube_service.py   # YouTube 服務邏輯
    └── gemini_service.py    # Gemini AI 服務邏輯
```