#!/usr/bin/env python3
"""
測試用戶建立腳本
建立測試帳號供開發和測試使用

使用方式：
cd kolog-backend
python create_test_user.py
"""

import sys
import os

# 添加 app 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from passlib.context import CryptContext

# 建立新的 Base 和 engine 避免衝突
DATABASE_URL = "sqlite:///./app/kolog.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 密碼加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 直接定義 User 模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

def create_test_users():
    """建立測試用戶"""
    
    # 確保資料庫表格存在
    Base.metadata.create_all(bind=engine)
    
    # 建立資料庫會話
    db: Session = SessionLocal()
    
    try:
        # 測試用戶資料
        test_users = [
            {
                "email": "test@kolog.com",
                "password": "password123",
                "full_name": "測試用戶",
            },
            {
                "email": "demo@kolog.com", 
                "password": "demo123456",
                "full_name": "示範用戶",
            }
        ]
        
        for user_data in test_users:
            # 檢查用戶是否已存在
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            
            if existing_user:
                print(f"用戶 {user_data['email']} 已存在，跳過建立")
                continue
            
            # 建立新用戶
            hashed_password = get_password_hash(user_data["password"])
            new_user = User(
                email=user_data["email"],
                password_hash=hashed_password,
                full_name=user_data["full_name"],
                is_active=True
            )
            
            db.add(new_user)
            print(f"✅ 建立測試用戶: {user_data['email']} (密碼: {user_data['password']})")
        
        # 提交變更
        db.commit()
        print("\n🎉 測試用戶建立完成！")
        
        print("\n📋 測試帳號清單：")
        print("=" * 50)
        for user_data in test_users:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"名稱: {user_data['full_name']}")
            print("-" * 30)
        
        print("\n🚀 現在可以使用這些帳號進行測試!")
        
    except Exception as e:
        print(f"❌ 建立測試用戶時發生錯誤: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 建立 KOLOG 測試用戶...")
    create_test_users()