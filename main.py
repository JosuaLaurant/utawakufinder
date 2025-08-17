"""
새로운 정규화된 구조를 사용하는 FastAPI 애플리케이션
PostgreSQL 이관 준비된 버전
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
import time
from datetime import datetime

# 새로운 모델과 데이터 매니저 import
from models import *
from data_manager import data_manager
from crawler import extract_video_id, find_comment

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Utawakufinder API v2", version="2.0.0")

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
    return {"message": "Utawakufinder API v2", "version": "2.0.0", "features": ["normalized_data", "postgres_ready"]}

@app.get("/health")
def health_check():
    """헬스 체크"""
    try:
        utaites = data_manager.load_utaites()
        performances = data_manager.load_performances()
        return {
            "status": "healthy",
            "utaites_count": len(utaites),
            "performances_count": len(performances),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        raise HTTPException(status_code=500, detail="시스템 오류")

# === 우타이테 API ===

@app.get("/utaites", response_model=List[UtaiteWithStats])
def get_utaites():
    """우타이테 목록과 통계"""
    try:
        utaites = data_manager.load_utaites()
        performances = data_manager.load_performances()
        songs_master = data_manager.load_songs_master()
        
        # 우타이테별 통계 계산
        utaite_stats = {}
        for utaite in utaites:
            utaite_performances = [p for p in performances if p.utaite_id == utaite.id]
            unique_songs = set(p.song_master_id for p in utaite_performances)
            
            # 아티스트 수 계산
            unique_artists = set()
            for song_id in unique_songs:
                song = next((s for s in songs_master if s.id == song_id), None)
                if song and hasattr(song, 'artist_id'):
                    unique_artists.add(song.artist_id)
            
            # 최신/최오래된 공연
            sorted_perfs = sorted(utaite_performances, key=lambda x: x.date)
            latest_perf = sorted_perfs[-1].date if sorted_perfs else None
            first_perf = sorted_perfs[0].date if sorted_perfs else None
            
            utaite_stats[utaite.id] = UtaiteWithStats(
                id=utaite.id,
                name=utaite.names.get('korean') or utaite.names.get('original', ''),
                names=utaite.names,
                performance_count=len(utaite_performances),
                unique_song_count=len(unique_songs),
                unique_artist_count=len(unique_artists),
                first_performance=first_perf,
                latest_performance=latest_perf,
                latest_thumbnail=f"https://img.youtube.com/vi/{sorted_perfs[-1].video_id}/mqdefault.jpg" if sorted_perfs else None
            )
        
        result = list(utaite_stats.values())
        result.sort(key=lambda x: x.performance_count, reverse=True)
        
        logger.info(f"우타이테 목록 조회 성공: {len(result)}명")
        return result
        
    except Exception as e:
        logger.error(f"우타이테 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"우타이테 목록 조회 중 오류: {str(e)}")

@app.get("/utaites/{utaite_id}/performances", response_model=List[PerformanceWithDetails])
def get_utaite_performances(utaite_id: str):
    """특정 우타이테의 부른 기록"""
    try:
        all_performances = data_manager.get_performances_with_details()
        filtered = [p for p in all_performances if p.utaite_id == utaite_id]
        
        # 날짜순 정렬
        filtered.sort(key=lambda x: x.date, reverse=True)
        
        logger.info(f"우타이테 부른 기록 조회 성공: {utaite_id} - {len(filtered)}곡")
        return filtered
        
    except Exception as e:
        logger.error(f"우타이테 부른 기록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"부른 기록 조회 중 오류: {str(e)}")

# === 곡/아티스트 API ===

@app.get("/songs", response_model=List[PerformanceWithDetails])
def get_songs():
    """모든 부른 기록 (기존 호환성)"""
    try:
        performances = data_manager.get_performances_with_details()
        performances.sort(key=lambda x: x.date, reverse=True)
        
        logger.info(f"부른 기록 조회 성공: {len(performances)}곡")
        return performances
        
    except Exception as e:
        logger.error(f"부른 기록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"부른 기록 조회 중 오류: {str(e)}")

@app.get("/songs/master", response_model=List[SongMaster])
def get_songs_master():
    """곡 마스터 정보"""
    try:
        songs_master = data_manager.load_songs_master()
        logger.info(f"곡 마스터 조회 성공: {len(songs_master)}곡")
        return songs_master
        
    except Exception as e:
        logger.error(f"곡 마스터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"곡 마스터 조회 중 오류: {str(e)}")

@app.get("/artists", response_model=List[Artist])
def get_artists():
    """아티스트 마스터 정보"""
    try:
        artists = data_manager.load_artists()
        logger.info(f"아티스트 조회 성공: {len(artists)}명")
        return artists
        
    except Exception as e:
        logger.error(f"아티스트 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"아티스트 조회 중 오류: {str(e)}")

# === 검색 API ===

@app.get("/search")
def search_songs(q: str, language: str = "original"):
    """다국어 검색"""
    try:
        # 우타이테 검색
        utaites = data_manager.load_utaites()
        matched_utaite_ids = set()
        
        for utaite in utaites:
            if any(q.lower() in name.lower() for name in utaite.names.values() if name):
                matched_utaite_ids.add(utaite.id)
        
        # 곡/아티스트 검색
        songs_master = data_manager.load_songs_master()
        artists = data_manager.load_artists()
        artists_dict = {a.id: a for a in artists}
        matched_song_ids = set()
        
        for song in songs_master:
            # 곡 제목 검색
            if any(q.lower() in title.lower() for title in song.titles.values() if title):
                matched_song_ids.add(song.id)
                continue
            
            # 아티스트명 검색
            if hasattr(song, 'artist_id'):
                artist = artists_dict.get(song.artist_id)
                if artist and any(q.lower() in name.lower() for name in artist.names.values() if name):
                    matched_song_ids.add(song.id)
        
        # 매칭된 부른 기록 찾기
        all_performances = data_manager.get_performances_with_details(language)
        results = [
            p for p in all_performances 
            if p.utaite_id in matched_utaite_ids or p.song_id in matched_song_ids
        ]
        
        # 날짜순 정렬
        results.sort(key=lambda x: x.date, reverse=True)
        
        logger.info(f"검색 완료: '{q}' - {len(results)}개 결과")
        return {
            "query": q,
            "language": language,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"검색 실패: {e}")
        raise HTTPException(status_code=500, detail=f"검색 중 오류: {str(e)}")

# === 곡 저장 API (기존 호환성) ===

@app.post("/parse-video")
def parse_video(request: URLRequest):
    """비디오 파싱 (기존 API 유지)"""
    logger.info(f"비디오 파싱 시작: URL={request.url}")
    
    try:
        # 기존 로직과 동일
        video_id = extract_video_id(request.url)
        if not video_id:
            raise HTTPException(status_code=400, detail="유효하지 않은 유튜브 URL입니다.")
        
        video_info = get_video_info(video_id)
        if not video_info:
            raise HTTPException(status_code=404, detail="비디오 정보를 가져올 수 없습니다.")
        
        comments = find_comment(video_id)
        songs = parse_songs_from_comments(comments, request.parsing_mode)
        song_objects = [ParsedSong(**song) for song in songs]
        
        result = {
            "video_info": video_info,
            "video_url": request.url,
            "songs": song_objects
        }
        
        logger.info(f"비디오 파싱 완료: {len(song_objects)}곡 추출됨")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"비디오 파싱 중 예외 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/save-songs")
def save_songs_endpoint(request: SaveSongsRequest):
    """곡 저장 (새로운 구조로 저장)"""
    logger.info(f"노래 저장 시작: Video ID={request.video_info.id}, 곡 수={len(request.songs)}")
    
    try:
        # 중복 체크
        existing_performances = data_manager.load_performances()
        existing_video_perfs = [p for p in existing_performances if p.video_id == request.video_info.id]
        if existing_video_perfs:
            raise HTTPException(status_code=400, detail="이미 등록된 영상입니다.")
        
        # 부른 사람 결정
        if request.singer_override:
            singer_name = request.singer_override.strip()
        else:
            singer_name = extract_singer_from_title_and_channel(request.video_info.title, request.video_info.channel)
        
        # 우타이테 ID 찾기/생성
        utaite_id = data_manager.find_or_create_utaite(singer_name)
        
        # 새 부른 기록 생성
        new_performances = []
        current_date = datetime.now().isoformat()
        
        for i, song in enumerate(request.songs):
            # 아티스트 찾기/생성
            artist_id = data_manager.find_or_create_artist(song.song_artist)
            
            # 곡 마스터 찾기/생성 
            song_master_id = find_or_create_song_master_v2(song.song_name, artist_id)
            
            # 부른 기록 생성
            performance_id = f"{request.video_info.id}_{i}_{song.start_time.replace(':', '')}"
            performance = Performance(
                id=performance_id,
                song_master_id=song_master_id,
                utaite_id=utaite_id,
                video_id=request.video_info.id,
                start_time=song.start_time,
                start_time_seconds=time_to_seconds(song.start_time),
                date=current_date
            )
            new_performances.append(performance)
        
        # 저장
        all_performances = existing_performances + new_performances
        data_manager.save_performances(all_performances)
        
        # 통계 업데이트
        update_performance_counts()
        
        logger.info("노래 저장 완료")
        return {"message": f"{len(new_performances)}곡이 성공적으로 저장되었습니다.", "performances": new_performances}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"노래 저장 중 예외 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"저장 중 오류가 발생했습니다: {str(e)}")

# === Helper Functions ===

def find_or_create_song_master_v2(song_name: str, artist_id: str) -> str:
    """새로운 구조로 곡 마스터 찾기/생성"""
    songs_master = data_manager.load_songs_master()
    
    # 기존 곡 찾기
    for song in songs_master:
        if (song.titles.get('original') == song_name and 
            hasattr(song, 'artist_id') and song.artist_id == artist_id):
            return song.id
    
    # 새 곡 생성
    song_id = generate_id('song', f"{song_name}|{artist_id}")
    current_time = datetime.now().isoformat()
    
    new_song = SongMaster(
        id=song_id,
        titles={'original': song_name, 'korean': '', 'english': '', 'romanized': ''},
        artist_id=artist_id,
        tags=[],
        performance_count=0,
        created_at=current_time,
        updated_at=current_time
    )
    
    songs_master.append(new_song)
    data_manager.save_songs_master(songs_master)
    
    logger.info(f"새 곡 마스터 생성: {song_name} (ID: {song_id})")
    return song_id

def update_performance_counts():
    """부른 횟수/곡 수 통계 업데이트"""
    try:
        performances = data_manager.load_performances()
        utaites = data_manager.load_utaites()
        songs_master = data_manager.load_songs_master()
        artists = data_manager.load_artists()
        
        # 우타이테별 부른 횟수
        utaite_counts = {}
        for perf in performances:
            utaite_counts[perf.utaite_id] = utaite_counts.get(perf.utaite_id, 0) + 1
        
        for utaite in utaites:
            utaite.performance_count = utaite_counts.get(utaite.id, 0)
        
        # 곡별 부른 횟수
        song_counts = {}
        for perf in performances:
            song_counts[perf.song_master_id] = song_counts.get(perf.song_master_id, 0) + 1
        
        for song in songs_master:
            song.performance_count = song_counts.get(song.id, 0)
        
        # 아티스트별 곡 수
        artist_counts = {}
        for song in songs_master:
            if hasattr(song, 'artist_id'):
                artist_counts[song.artist_id] = artist_counts.get(song.artist_id, 0) + 1
        
        for artist in artists:
            artist.song_count = artist_counts.get(artist.id, 0)
        
        # 저장
        data_manager.save_utaites(utaites)
        data_manager.save_songs_master(songs_master)
        data_manager.save_artists(artists)
        
        logger.info("통계 업데이트 완료")
        
    except Exception as e:
        logger.error(f"통계 업데이트 실패: {e}")

# 기존 함수들을 deprecated 파일에서 import
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'deprecated'))

from main_old import (
    parse_songs_from_comments, 
    get_video_info, 
    extract_singer_from_title_and_channel
)

# === Legacy Compatibility ===

@app.get("/videos")
def get_videos():
    """기존 호환성을 위한 비디오 엔드포인트"""
    return get_songs()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9030)