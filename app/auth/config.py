import os
from datetime import timedelta

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 天

# Google OAuth 配置
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid_configuration"

# 允許的來源 (CORS)
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-domain.com"  # 替換成您的正式域名
]