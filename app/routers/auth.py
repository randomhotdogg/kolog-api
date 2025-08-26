from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
import httpx
import json

from database import get_db
from models.auth_models import User
from models.schemas import UserCreate, UserLogin, UserResponse, Token, GoogleAuthRequest
from auth.utils import (
    get_password_hash, 
    authenticate_user, 
    create_access_token,
    get_current_active_user
)
from auth.config import ACCESS_TOKEN_EXPIRE_MINUTES, GOOGLE_CLIENT_ID

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=Token)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """使用者註冊"""
    # 檢查 email 是否已存在
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此電子郵件已被註冊"
        )
    
    # 建立新使用者
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 建立 access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, 
        expires_delta=access_token_expires
    )
    
    user_response = UserResponse.from_orm(db_user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """使用者登入"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="電子郵件或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="帳號未啟用"
        )
    
    # 建立 access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    user_response = UserResponse.from_orm(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """取得當前使用者資訊"""
    return UserResponse.from_orm(current_user)

@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_active_user)):
    """使用者登出（由前端處理 token 移除）"""
    return {"message": "成功登出"}

@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_active_user)):
    """驗證 token 是否有效"""
    return {"valid": True, "user_id": current_user.id}

@router.post("/google", response_model=Token)
async def google_oauth_login(google_auth: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Google OAuth 登入"""
    try:
        # 驗證 Google token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={google_auth.token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="無效的 Google token"
                )
            
            google_data = response.json()
            
            # 驗證 audience (client_id)
            if google_data.get("aud") != GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="無效的 Google client ID"
                )
            
            # 獲取用戶資訊
            email = google_data.get("email")
            google_id = google_data.get("sub")
            full_name = google_data.get("name")
            avatar_url = google_data.get("picture")
            
            if not email or not google_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="無法從 Google 取得必要的用戶資訊"
                )
            
            # 檢查用戶是否已存在
            user = db.query(User).filter(
                (User.email == email) | (User.google_id == google_id)
            ).first()
            
            if user:
                # 更新現有用戶的 Google 資訊
                if not user.google_id:
                    user.google_id = google_id
                if avatar_url:
                    user.avatar_url = avatar_url
                if full_name and not user.full_name:
                    user.full_name = full_name
            else:
                # 建立新用戶
                user = User(
                    email=email,
                    google_id=google_id,
                    full_name=full_name,
                    avatar_url=avatar_url,
                    is_active=True
                )
                db.add(user)
            
            db.commit()
            db.refresh(user)
            
            # 建立 access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user.id)}, 
                expires_delta=access_token_expires
            )
            
            user_response = UserResponse.from_orm(user)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_response
            }
            
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="無法連接到 Google 認證服務"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google OAuth 認證錯誤: {str(e)}"
        )