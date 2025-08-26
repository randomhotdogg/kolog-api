from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

# SQLite 資料庫檔案路徑
DATABASE_URL = "sqlite:///./kolog.db"

# SQLAlchemy 引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 模型
Base = declarative_base()

# 異步資料庫連接（用於 FastAPI）
database = Database(DATABASE_URL)

# Dependency 函式
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()