# KOLOG Backend

完整的 Python FastAPI 後端服務，提供 YouTube 影片分析、使用者認證和股票追蹤功能。

## 功能特色

- 🎥 **YouTube 逐字稿獲取**: 支援多語言逐字稿提取
- 🤖 **AI 智能分析**: 整合 Google Gemini AI 進行股票分析
- 📊 **影片元數據**: 獲取 YouTube 影片資訊和發布日期
- 🔐 **使用者認證**: JWT token 認證 + Google OAuth 登入
- 📈 **股票追蹤**: 個人化股票追蹤清單管理
- 🚀 **高效能 API**: 基於 FastAPI 的異步處理
- 📖 **自動化文檔**: 內建 Swagger UI 和 ReDoc

## API 端點

### 🔐 使用者認證
```
POST /api/v1/auth/register      # 使用者註冊
POST /api/v1/auth/login         # 使用者登入
POST /api/v1/auth/google        # Google OAuth 登入
GET  /api/v1/auth/me            # 取得當前使用者資訊
POST /api/v1/auth/logout        # 使用者登出
GET  /api/v1/auth/verify-token  # 驗證 token 有效性
```

### 📈 股票追蹤管理
```
GET    /api/v1/user/stocks/           # 取得使用者追蹤股票清單
POST   /api/v1/user/stocks/           # 新增股票到追蹤清單
PUT    /api/v1/user/stocks/{id}       # 更新追蹤股票資訊
DELETE /api/v1/user/stocks/{id}       # 移除追蹤股票
PATCH  /api/v1/user/stocks/{id}/name  # 更新股票自訂名稱
```

### 🎥 YouTube 逐字稿
```
POST /api/v1/youtube/transcript
```
獲取 YouTube 影片的逐字稿內容

### 📊 影片元數據
```
POST /api/v1/youtube/metadata  
```
使用 YouTube Data API 獲取影片資訊

### 🤖 AI 分析
```
POST /api/v1/analysis/gemini
```
使用 Google Gemini AI 分析影片內容並識別股票

## 快速開始

### 本地開發

1. **安裝依賴**：
```bash
pip install -r requirements.txt
```

2. **建立測試用戶** (可選)：
```bash
python create_test_user.py
```

3. **啟動開發服務器**：
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **查看 API 文檔**：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康檢查: http://localhost:8000/health

### 使用 Docker (推薦)

1. **複製環境變數文件**：
```bash
cp .env.example .env
```

2. **啟動服務**：
```bash
docker-compose up -d
```

### 測試帳號

系統提供以下測試帳號供開發使用：
```
Email: test@kolog.com
Password: password123

Email: demo@kolog.com  
Password: demo123456

Email: admin@kolog.com
Password: admin123456
```

## 環境變數

參考 `.env.example` 文件配置以下變數：

### 必要設定
- `SECRET_KEY`: JWT token 加密密鑰
- `DATABASE_URL`: 資料庫連接字串 (預設: SQLite)

### Google OAuth (選填)
- `GOOGLE_CLIENT_ID`: Google OAuth Client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth Client Secret

### API 服務設定
- `ALLOWED_ORIGINS`: CORS 允許的來源域名
- `API_HOST`: API 伺服器主機地址  
- `API_PORT`: API 伺服器端口
- `API_DEBUG`: 是否開啟除錯模式
- `LOG_LEVEL`: 日誌等級

### AI 服務 (選填)
- `GEMINI_API_KEY`: Google Gemini AI API 密鑰

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

## 資料庫架構

系統使用 SQLAlchemy ORM 管理資料庫：

### 資料表
- **users**: 使用者資訊 (email, password_hash, google_id, 等)
- **user_stocks**: 使用者股票追蹤 (symbol, company_name, start_price, 等)

### 初始化
資料庫會在首次啟動時自動建立表格，無需手動設定。

## 開發說明

### 專案結構
```
app/
├── main.py                  # FastAPI 主應用
├── database.py              # 資料庫連接配置
├── auth/
│   ├── config.py           # 認證配置
│   └── utils.py            # JWT 和密碼處理工具
├── models/
│   ├── schemas.py          # Pydantic 資料模型
│   └── auth_models.py      # SQLAlchemy 資料庫模型
├── routers/
│   ├── auth.py             # 認證 API 路由
│   ├── user_stocks.py      # 股票追蹤 API 路由
│   ├── transcript.py       # 逐字稿 API 路由
│   ├── metadata.py         # 元數據 API 路由
│   └── analysis.py         # 分析 API 路由
└── services/
    ├── youtube_service.py  # YouTube 服務邏輯
    └── gemini_service.py   # Gemini AI 服務邏輯

create_test_user.py          # 測試用戶建立腳本
```

### 認證機制
- **JWT Token**: 30 天有效期
- **Google OAuth**: 支援 Google 帳號登入
- **受保護端點**: 需要 Bearer Token 認證