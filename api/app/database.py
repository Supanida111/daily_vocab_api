# api/app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ถ้า docker-compose ตั้ง env DATABASE_URL ไว้ก็จะใช้ค่านั้น
# ถ้าไม่มีก็ใช้ค่า default ตาม workshop
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://vocabuser:vocabpass123@mysql:3306/vocabulary_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
