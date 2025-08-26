from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # OAuth 用戶可能沒有密碼
    google_id = Column(String(255), unique=True, nullable=True)  # Google OAuth ID
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserStock(Base):
    __tablename__ = "user_stocks"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 股票基本資訊
    symbol = Column(String(20), nullable=False)
    company_name = Column(String(255), nullable=False)
    custom_name = Column(String(50), nullable=True)  # 用戶自定義名稱
    
    # 追蹤資訊
    start_tracking_date = Column(DateTime(timezone=True), nullable=False)
    start_price = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    
    # YouTube 分析資料（選填）
    youtube_analysis = Column(Text, nullable=True)  # JSON 格式存儲
    
    # 時間戳記
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 在類別定義完成後設定關聯
User.tracked_stocks = relationship("UserStock", back_populates="user", cascade="all, delete-orphan")
UserStock.user = relationship("User", back_populates="tracked_stocks")