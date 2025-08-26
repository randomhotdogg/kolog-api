from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
import json

from database import get_db
from models.auth_models import User, UserStock
from models.schemas import UserStockCreate, UserStockResponse
from auth.utils import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[UserStockResponse])
async def get_user_stocks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取得當前使用者的所有追蹤股票"""
    stocks = db.query(UserStock).filter(UserStock.user_id == current_user.id).all()
    return [UserStockResponse.from_orm(stock) for stock in stocks]

@router.post("/", response_model=UserStockResponse)
async def add_user_stock(
    stock_data: UserStockCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """新增股票到使用者追蹤清單"""
    # 檢查是否已經追蹤該股票
    existing_stock = db.query(UserStock).filter(
        UserStock.user_id == current_user.id,
        UserStock.symbol == stock_data.symbol
    ).first()
    
    if existing_stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已經在追蹤這支股票"
        )
    
    # 建立新的追蹤股票
    db_stock = UserStock(
        user_id=current_user.id,
        symbol=stock_data.symbol,
        company_name=stock_data.company_name,
        custom_name=stock_data.custom_name,
        start_tracking_date=stock_data.start_tracking_date,
        start_price=stock_data.start_price,
        currency=stock_data.currency,
        youtube_analysis=stock_data.youtube_analysis
    )
    
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    
    return UserStockResponse.from_orm(db_stock)

@router.put("/{stock_id}", response_model=UserStockResponse)
async def update_user_stock(
    stock_id: int,
    stock_data: UserStockCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新使用者追蹤的股票資訊"""
    stock = db.query(UserStock).filter(
        UserStock.id == stock_id,
        UserStock.user_id == current_user.id
    ).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到該追蹤股票"
        )
    
    # 更新股票資訊
    for field, value in stock_data.dict(exclude_unset=True).items():
        setattr(stock, field, value)
    
    db.commit()
    db.refresh(stock)
    
    return UserStockResponse.from_orm(stock)

@router.delete("/{stock_id}")
async def delete_user_stock(
    stock_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """從使用者追蹤清單移除股票"""
    stock = db.query(UserStock).filter(
        UserStock.id == stock_id,
        UserStock.user_id == current_user.id
    ).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到該追蹤股票"
        )
    
    db.delete(stock)
    db.commit()
    
    return {"message": "成功移除追蹤股票"}

@router.patch("/{stock_id}/name")
async def update_stock_custom_name(
    stock_id: int,
    custom_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新股票的自訂名稱"""
    stock = db.query(UserStock).filter(
        UserStock.id == stock_id,
        UserStock.user_id == current_user.id
    ).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到該追蹤股票"
        )
    
    # 限制字數最多15字
    trimmed_name = custom_name.strip()[:15] if custom_name.strip() else None
    stock.custom_name = trimmed_name
    
    db.commit()
    db.refresh(stock)
    
    return {"message": "成功更新股票名稱", "custom_name": trimmed_name}