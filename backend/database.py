from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os

# 데이터베이스 URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://utawaku:utawakupass123@localhost:5433/utawakufinder")

# SQLAlchemy 설정
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 아티스트 모델
class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    name_korean = Column(String(255))
    name_english = Column(String(255))
    name_romanized = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    song_masters = relationship("SongMaster", back_populates="artist")

# 우타이테 모델
class Utaite(Base):
    __tablename__ = "utaites"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    name_korean = Column(String(255))
    name_english = Column(String(255))
    name_romanized = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    performances = relationship("Performance", back_populates="utaite")

# 곡 마스터 모델
class SongMaster(Base):
    __tablename__ = "song_masters"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    title_korean = Column(String(500))
    title_english = Column(String(500))
    title_romanized = Column(String(500))
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False, index=True)
    album_art_url = Column(Text)
    tags = Column(ARRAY(String))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    artist = relationship("Artist", back_populates="song_masters")
    performances = relationship("Performance", back_populates="song_master")

# 비디오 모델
class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    channel = Column(String(255))
    thumbnail_url = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    performances = relationship("Performance", back_populates="video")

# 공연 기록 모델
class Performance(Base):
    __tablename__ = "performances"
    
    id = Column(Integer, primary_key=True, index=True)
    song_master_id = Column(Integer, ForeignKey("song_masters.id"), nullable=False, index=True)
    utaite_id = Column(Integer, ForeignKey("utaites.id"), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False, index=True)
    start_time = Column(String(20), nullable=False)  # "HH:MM:SS" 형식
    date = Column(TIMESTAMP, nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    song_master = relationship("SongMaster", back_populates="performances")
    utaite = relationship("Utaite", back_populates="performances")
    video = relationship("Video", back_populates="performances")