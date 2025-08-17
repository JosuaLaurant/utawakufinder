"""
PostgreSQL을 사용하는 FastAPI 애플리케이션
정수 ID 기반 최적화된 버전
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_, text
from typing import List, Optional, Dict
import logging
import time
import requests
import os
import asyncio
from datetime import datetime

# PostgreSQL 관련 imports
from database import get_db
from database import Artist as ArtistModel, Utaite as UtaiteModel, SongMaster as SongMasterModel, Video as VideoModel, Performance as PerformanceModel
from schemas import *

# 기존 파싱 로직 imports
from crawler import extract_video_id, find_comment

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Utawakufinder API PostgreSQL", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"요청 시작: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"요청 완료: {request.method} {request.url} - 상태코드: {response.status_code} - 처리시간: {process_time:.2f}초")
    
    return response

# === 기본 정보 ===

@app.get("/")
def root():
    return {"message": "Utawakufinder API PostgreSQL", "version": "3.0.0", "features": ["postgresql", "integer_ids", "optimized"]}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """헬스 체크"""
    try:
        utaites_count = db.query(UtaiteModel).count()
        performances_count = db.query(PerformanceModel).count()
        return {
            "status": "healthy",
            "utaites_count": utaites_count,
            "performances_count": performances_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        raise HTTPException(status_code=500, detail="시스템 오류")

# === 부른 기록 API (기존 호환성) ===

@app.get("/songs")
def get_songs(db: Session = Depends(get_db)):
    """모든 부른 기록 (프론트엔드 호환용)"""
    try:
        # performance_details 뷰를 직접 쿼리
        query = """
        SELECT 
            p.id,
            p.start_time,
            p.date,
            sm.id as song_id,
            sm.title as song_title,
            a.name as song_artist,
            u.id as utaite_id,
            u.name as utaite_name,
            v.video_id,
            v.title as video_title,
            v.channel as video_channel,
            v.thumbnail_url
        FROM performances p
        JOIN song_masters sm ON p.song_master_id = sm.id
        JOIN artists a ON sm.artist_id = a.id
        JOIN utaites u ON p.utaite_id = u.id
        JOIN videos v ON p.video_id = v.id
        ORDER BY p.date DESC
        """
        
        results = db.execute(text(query)).fetchall()
        
        performances = []
        for row in results:
            performances.append(PerformanceDetail(
                id=row.id,
                start_time=row.start_time,
                date=row.date,
                song_id=row.song_id,
                song_title=row.song_title,
                song_artist=row.song_artist,
                utaite_id=row.utaite_id,
                utaite_name=row.utaite_name,
                video_id=row.video_id,
                video_title=row.video_title,
                video_channel=row.video_channel,
                thumbnail_url=row.thumbnail_url
            ))
        
        logger.info(f"부른 기록 조회 성공: {len(performances)}곡")
        return performances
        
    except Exception as e:
        logger.error(f"부른 기록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"부른 기록 조회 중 오류: {str(e)}")

@app.get("/songs/master")
def get_songs_master(db: Session = Depends(get_db)):
    """곡 마스터 정보 (프론트엔드 호환용)"""
    try:
        # 곡 통계와 함께 조회
        query = """
        SELECT 
            sm.id,
            sm.title,
            sm.title_korean,
            sm.title_english,
            sm.title_romanized,
            a.name as artist_name,
            a.name_korean as artist_name_korean,
            a.name_english as artist_name_english,
            a.name_romanized as artist_name_romanized,
            sm.album_art_url,
            sm.tags,
            COALESCE(ss.performance_count, 0) as performance_count,
            sm.created_at,
            sm.updated_at
        FROM song_masters sm
        JOIN artists a ON sm.artist_id = a.id
        LEFT JOIN song_stats ss ON sm.id = ss.id
        ORDER BY COALESCE(ss.performance_count, 0) DESC
        """
        
        results = db.execute(text(query)).fetchall()
        
        songs = []
        for row in results:
            songs.append(SongMasterDetail(
                id=row.id,
                titles={
                    "original": row.title,
                    "korean": row.title_korean,
                    "english": row.title_english,
                    "romanized": row.title_romanized
                },
                artist={
                    "original": row.artist_name,
                    "korean": row.artist_name_korean,
                    "english": row.artist_name_english,
                    "romanized": row.artist_name_romanized
                },
                tags=row.tags or [],
                performance_count=row.performance_count,
                album_art_url=row.album_art_url
            ))
        
        logger.info(f"곡 마스터 조회 성공: {len(songs)}곡")
        return songs
        
    except Exception as e:
        logger.error(f"곡 마스터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"곡 마스터 조회 중 오류: {str(e)}")

@app.get("/songs/by-master/{song_master_id}")
def get_songs_by_master(song_master_id: int, db: Session = Depends(get_db)):
    """특정 곡의 모든 부른 기록"""
    try:
        query = """
        SELECT 
            p.id,
            p.start_time,
            p.date,
            sm.id as song_id,
            sm.title as song_title,
            a.name as song_artist,
            u.id as utaite_id,
            u.name as utaite_name,
            v.video_id,
            v.title as video_title,
            v.channel as video_channel,
            v.thumbnail_url
        FROM performances p
        JOIN song_masters sm ON p.song_master_id = sm.id
        JOIN artists a ON sm.artist_id = a.id
        JOIN utaites u ON p.utaite_id = u.id
        JOIN videos v ON p.video_id = v.id
        WHERE sm.id = :song_master_id
        ORDER BY p.date DESC
        """
        
        results = db.execute(text(query), {"song_master_id": song_master_id}).fetchall()
        
        performances = []
        for row in results:
            performances.append(PerformanceDetail(
                id=row.id,
                start_time=row.start_time,
                date=row.date,
                song_id=row.song_id,
                song_title=row.song_title,
                song_artist=row.song_artist,
                utaite_id=row.utaite_id,
                utaite_name=row.utaite_name,
                video_id=row.video_id,
                video_title=row.video_title,
                video_channel=row.video_channel,
                thumbnail_url=row.thumbnail_url
            ))
        
        logger.info(f"곡별 부른 기록 조회 성공: {song_master_id} - {len(performances)}곡")
        return performances
        
    except Exception as e:
        logger.error(f"곡별 부른 기록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"곡별 부른 기록 조회 중 오류: {str(e)}")

# === 아티스트 API ===

@app.get("/artists")
def get_artists(db: Session = Depends(get_db)):
    """아티스트 목록과 통계 (프론트엔드 호환용)"""
    try:
        logger.info("아티스트 쿼리 시작")
        # 먼저 간단한 쿼리로 테스트
        results = db.execute(text("SELECT * FROM artist_stats WHERE total_performances > 0 ORDER BY total_performances DESC")).fetchall()
        logger.info(f"쿼리 완료, 결과: {len(results)}개")
        
        artists = []
        for row in results:
            # 간단한 버전으로 변경
            artists.append({
                "id": row.id,
                "name": row.name,
                "name_korean": row.name_korean,
                "name_english": row.name_english,
                "name_romanized": row.name_romanized,
                "song_count": row.song_count,
                "total_performances": row.total_performances,
                "latest_performance": {
                    "date": row.latest_performance_date.isoformat() if row.latest_performance_date else None,
                    "thumbnail_url": "/default-thumbnail.jpg",
                    "song_title": "Latest Song"
                } if row.latest_performance_date else None,
                "first_performance": None,
                "top_songs": []
            })
        
        logger.info(f"아티스트 통계 조회 성공: {len(artists)}명")
        return artists
        
    except Exception as e:
        logger.error(f"아티스트 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"아티스트 통계 조회 중 오류: {str(e)}")

@app.get("/artists/songs")
def get_artist_songs(name: str, db: Session = Depends(get_db)):
    """특정 아티스트의 모든 곡"""
    try:
        query = """
        SELECT 
            p.id,
            p.start_time,
            p.date,
            sm.id as song_id,
            sm.title as song_title,
            a.name as song_artist,
            u.id as utaite_id,
            u.name as utaite_name,
            v.video_id,
            v.title as video_title,
            v.channel as video_channel,
            v.thumbnail_url
        FROM performances p
        JOIN song_masters sm ON p.song_master_id = sm.id
        JOIN artists a ON sm.artist_id = a.id
        JOIN utaites u ON p.utaite_id = u.id
        JOIN videos v ON p.video_id = v.id
        WHERE a.name = :artist_name
        ORDER BY p.date DESC
        """
        
        results = db.execute(text(query), {"artist_name": name}).fetchall()
        
        performances = []
        for row in results:
            performances.append(PerformanceDetail(
                id=row.id,
                start_time=row.start_time,
                date=row.date,
                song_id=row.song_id,
                song_title=row.song_title,
                song_artist=row.song_artist,
                utaite_id=row.utaite_id,
                utaite_name=row.utaite_name,
                video_id=row.video_id,
                video_title=row.video_title,
                video_channel=row.video_channel,
                thumbnail_url=row.thumbnail_url
            ))
        
        logger.info(f"아티스트별 곡 조회 성공: {name} - {len(performances)}곡")
        return performances
        
    except Exception as e:
        logger.error(f"아티스트별 곡 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"아티스트별 곡 조회 중 오류: {str(e)}")

# === 우타이테 API ===

@app.get("/utaites")
def get_utaites(db: Session = Depends(get_db)):
    """우타이테 목록과 통계"""
    try:
        query = """
        SELECT 
            u.id,
            u.name,
            u.name_korean,
            u.name_english,
            u.name_romanized,
            COALESCE(ust.total_performances, 0) as total_performances,
            COALESCE(ust.unique_songs, 0) as unique_songs,
            COALESCE(ust.unique_artists, 0) as unique_artists,
            ust.latest_performance_date,
            ust.first_performance_date
        FROM utaites u
        LEFT JOIN utaite_stats ust ON u.id = ust.id
        WHERE COALESCE(ust.total_performances, 0) > 0
        ORDER BY COALESCE(ust.total_performances, 0) DESC
        """
        
        results = db.execute(text(query)).fetchall()
        
        utaites = []
        for row in results:
            latest_performance = None
            first_performance = None
            
            # 최신 공연 정보
            if row.latest_performance_date:
                latest_query = """
                SELECT v.thumbnail_url, sm.title
                FROM performances p
                JOIN videos v ON p.video_id = v.id
                JOIN song_masters sm ON p.song_master_id = sm.id
                WHERE p.utaite_id = :utaite_id AND p.date = :latest_date
                LIMIT 1
                """
                latest_result = db.execute(text(latest_query), {
                    "utaite_id": row.id,
                    "latest_date": row.latest_performance_date
                }).fetchone()
                
                if latest_result:
                    latest_performance = {
                        "date": row.latest_performance_date.isoformat(),
                        "thumbnail_url": latest_result.thumbnail_url,
                        "song_title": latest_result.title
                    }
            
            # 인기 곡들
            top_songs_query = """
            SELECT sm.id, sm.title, a.name as artist_name, COUNT(p.id) as performance_count
            FROM performances p
            JOIN song_masters sm ON p.song_master_id = sm.id
            JOIN artists a ON sm.artist_id = a.id
            WHERE p.utaite_id = :utaite_id
            GROUP BY sm.id, sm.title, a.name
            ORDER BY COUNT(p.id) DESC
            LIMIT 5
            """
            top_songs_results = db.execute(text(top_songs_query), {"utaite_id": row.id}).fetchall()
            
            top_songs = [
                {
                    "id": ts.id,
                    "title": ts.title,
                    "artist_name": ts.artist_name,
                    "performance_count": ts.performance_count
                }
                for ts in top_songs_results
            ]
            
            utaites.append(UtaiteWithStats(
                id=row.id,
                name=row.name,
                name_korean=row.name_korean,
                name_english=row.name_english,
                name_romanized=row.name_romanized,
                total_performances=row.total_performances,
                unique_songs=row.unique_songs,
                unique_artists=row.unique_artists,
                latest_performance=latest_performance,
                first_performance=first_performance,
                top_songs=top_songs
            ))
        
        logger.info(f"우타이테 목록 조회 성공: {len(utaites)}명")
        return utaites
        
    except Exception as e:
        logger.error(f"우타이테 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"우타이테 목록 조회 중 오류: {str(e)}")

@app.get("/utaites/songs")
def get_utaite_songs(name: str, db: Session = Depends(get_db)):
    """특정 우타이테의 모든 곡"""
    try:
        query = """
        SELECT 
            p.id,
            p.start_time,
            p.date,
            sm.id as song_id,
            sm.title as song_title,
            a.name as song_artist,
            u.id as utaite_id,
            u.name as utaite_name,
            v.video_id,
            v.title as video_title,
            v.channel as video_channel,
            v.thumbnail_url
        FROM performances p
        JOIN song_masters sm ON p.song_master_id = sm.id
        JOIN artists a ON sm.artist_id = a.id
        JOIN utaites u ON p.utaite_id = u.id
        JOIN videos v ON p.video_id = v.id
        WHERE u.name = :utaite_name
        ORDER BY p.date DESC
        """
        
        results = db.execute(text(query), {"utaite_name": name}).fetchall()
        
        performances = []
        for row in results:
            performances.append(PerformanceDetail(
                id=row.id,
                start_time=row.start_time,
                date=row.date,
                song_id=row.song_id,
                song_title=row.song_title,
                song_artist=row.song_artist,
                utaite_id=row.utaite_id,
                utaite_name=row.utaite_name,
                video_id=row.video_id,
                video_title=row.video_title,
                video_channel=row.video_channel,
                thumbnail_url=row.thumbnail_url
            ))
        
        logger.info(f"우타이테별 곡 조회 성공: {name} - {len(performances)}곡")
        return performances
        
    except Exception as e:
        logger.error(f"우타이테별 곡 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"우타이테별 곡 조회 중 오류: {str(e)}")

# === 기존 호환성 ===

@app.get("/videos")
def get_videos(db: Session = Depends(get_db)):
    """기존 호환성을 위한 비디오 엔드포인트"""
    return get_songs(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9030)