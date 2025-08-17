"""
새로운 정규화된 구조를 사용하는 FastAPI 애플리케이션
PostgreSQL 이관 준비된 버전
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
import time
import requests
import os
import asyncio
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
                if song and song.artist.get('original'):
                    unique_artists.add(song.artist.get('original'))
            
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

@app.get("/artists", response_model=List[ArtistWithStats])
def get_artists_with_stats():
    """아티스트 목록과 통계"""
    try:
        artists = data_manager.load_artists()
        performances = data_manager.load_performances()
        songs_master = data_manager.load_songs_master()
        
        # 아티스트별 통계 계산
        artist_stats = {}
        for artist in artists:
            # 이 아티스트의 곡들 찾기 (기존 구조 사용 - artist name으로 매칭)
            artist_name = artist.names.get('original', '')
            artist_songs = [s for s in songs_master if s.artist.get('original') == artist_name]
            
            # 이 아티스트 곡들의 부른 기록들 찾기
            artist_performances = []
            for song in artist_songs:
                song_perfs = [p for p in performances if p.song_master_id == song.id]
                artist_performances.extend(song_perfs)
            
            # 최신/최오래된 공연
            sorted_perfs = sorted(artist_performances, key=lambda x: x.date) if artist_performances else []
            latest_perf = None
            first_perf = None
            
            if sorted_perfs:
                latest_performance = sorted_perfs[-1]
                first_performance = sorted_perfs[0]
                
                # 최신 공연 정보
                latest_song = next((s for s in songs_master if s.id == latest_performance.song_master_id), None)
                latest_perf = {
                    "date": latest_performance.date,
                    "thumbnail": f"https://img.youtube.com/vi/{latest_performance.video_id}/mqdefault.jpg",
                    "song_title": latest_song.titles.get('original', '') if latest_song else ''
                }
                
                # 최오래된 공연 정보
                first_song = next((s for s in songs_master if s.id == first_performance.song_master_id), None)
                first_perf = {
                    "date": first_performance.date,
                    "thumbnail": f"https://img.youtube.com/vi/{first_performance.video_id}/mqdefault.jpg",
                    "song_title": first_song.titles.get('original', '') if first_song else ''
                }
            
            # 인기 곡들 (부른 횟수 기준)
            song_counts = {}
            for perf in artist_performances:
                song_counts[perf.song_master_id] = song_counts.get(perf.song_master_id, 0) + 1
            
            top_songs = []
            for song in artist_songs:
                count = song_counts.get(song.id, 0)
                if count > 0:
                    top_songs.append({
                        "id": song.id,
                        "title": song.titles.get('original', ''),
                        "performance_count": count
                    })
            
            # 부른 횟수순으로 정렬
            top_songs.sort(key=lambda x: x['performance_count'], reverse=True)
            
            artist_stats[artist.id] = ArtistWithStats(
                id=artist.id,
                name=artist.names.get('korean') or artist.names.get('original', ''),
                names=artist.names,
                song_count=len(artist_songs),
                total_performances=len(artist_performances),
                latest_performance=latest_perf,
                first_performance=first_perf,
                top_songs=top_songs
            )
        
        result = list(artist_stats.values())
        result.sort(key=lambda x: x.total_performances, reverse=True)
        
        logger.info(f"아티스트 통계 조회 성공: {len(result)}명")
        return result
        
    except Exception as e:
        logger.error(f"아티스트 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"아티스트 통계 조회 중 오류: {str(e)}")

@app.get("/artists/master", response_model=List[Artist])
def get_artists_master():
    """아티스트 마스터 정보 (기본)"""
    try:
        artists = data_manager.load_artists()
        logger.info(f"아티스트 마스터 조회 성공: {len(artists)}명")
        return artists
        
    except Exception as e:
        logger.error(f"아티스트 마스터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"아티스트 마스터 조회 중 오류: {str(e)}")

@app.get("/songs/by-master/{song_master_id}", response_model=List[PerformanceWithDetails])
def get_songs_by_master(song_master_id: str):
    """특정 곡의 모든 부른 기록"""
    try:
        all_performances = data_manager.get_performances_with_details()
        filtered = [p for p in all_performances if p.song_id == song_master_id]
        
        # 날짜순 정렬
        filtered.sort(key=lambda x: x.date, reverse=True)
        
        logger.info(f"곡별 부른 기록 조회 성공: {song_master_id} - {len(filtered)}곡")
        return filtered
        
    except Exception as e:
        logger.error(f"곡별 부른 기록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"곡별 부른 기록 조회 중 오류: {str(e)}")

@app.get("/artists/songs", response_model=List[PerformanceWithDetails])
def get_artist_songs(name: str):
    """특정 아티스트의 모든 곡"""
    try:
        all_performances = data_manager.get_performances_with_details()
        filtered = [p for p in all_performances if p.song_artist == name]
        
        # 날짜순 정렬
        filtered.sort(key=lambda x: x.date, reverse=True)
        
        logger.info(f"아티스트별 곡 조회 성공: {name} - {len(filtered)}곡")
        return filtered
        
    except Exception as e:
        logger.error(f"아티스트별 곡 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"아티스트별 곡 조회 중 오류: {str(e)}")

@app.get("/utaites/songs", response_model=List[PerformanceWithDetails])
def get_utaite_songs(name: str):
    """특정 우타이테의 모든 곡"""
    try:
        all_performances = data_manager.get_performances_with_details()
        filtered = [p for p in all_performances if p.utaite_name == name]
        
        # 날짜순 정렬
        filtered.sort(key=lambda x: x.date, reverse=True)
        
        logger.info(f"우타이테별 곡 조회 성공: {name} - {len(filtered)}곡")
        return filtered
        
    except Exception as e:
        logger.error(f"우타이테별 곡 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"우타이테별 곡 조회 중 오류: {str(e)}")

@app.post("/songs/update-album-art")
async def update_album_art(limit: int = 5):
    """곡의 앨범아트를 검색해서 업데이트 (기본 5곡씩)"""
    try:
        songs_master = data_manager.load_songs_master()
        updated_count = 0
        processed_count = 0
        
        for song in songs_master:
            # 제한 수에 도달하면 중단
            if processed_count >= limit:
                break
                
            # 이미 실제 앨범아트가 있는 경우 스킵 (placeholder가 아닌 경우)
            if song.album_art_url and not song.album_art_url.startswith('https://via.placeholder.com'):
                continue
                
            song_title = song.titles.get('original', '')
            artist_name = song.artist.get('original', '')
            
            if song_title and artist_name:
                logger.info(f"앨범아트 검색 ({processed_count + 1}/{limit}): {song_title} - {artist_name}")
                
                # 앨범아트 검색
                album_art_url = await search_album_art(song_title, artist_name)
                
                if album_art_url:
                    song.album_art_url = album_art_url
                    updated_count += 1
                    logger.info(f"✅ 앨범아트 찾음: {album_art_url}")
                else:
                    # 기본 이미지 설정
                    song.album_art_url = get_default_album_art()
                    logger.info(f"❌ 앨범아트 없음 - 기본 이미지 설정")
                
                processed_count += 1
                
                # API 호출 제한을 위해 잠시 대기
                await asyncio.sleep(1.0)  # MusicBrainz는 초당 1회 제한
        
        # 업데이트된 데이터 저장
        data_manager.save_songs_master(songs_master)
        
        logger.info(f"앨범아트 업데이트 완료: {processed_count}곡 처리, {updated_count}곡 성공")
        return {
            "message": f"앨범아트 업데이트 완료",
            "processed_count": processed_count,
            "updated_count": updated_count,
            "total_songs": len(songs_master)
        }
        
    except Exception as e:
        logger.error(f"앨범아트 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"앨범아트 업데이트 중 오류: {str(e)}")

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
            
            # 아티스트명 검색 (기존 구조 사용)
            if song.artist.get('original'):
                if q.lower() in song.artist.get('original', '').lower():
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

# === Image Search Functions ===

async def search_album_art_itunes(song_title: str, artist_name: str) -> Optional[str]:
    """iTunes Search API를 사용해서 앨범아트 이미지 검색"""
    try:
        # iTunes Search API로 음악 검색
        search_url = "https://itunes.apple.com/search"
        
        # 일본 스토어에서 우선 검색
        for country in ['JP', 'US']:  # 일본 -> 미국 순서로 검색
            params = {
                'term': f"{song_title} {artist_name}",
                'media': 'music',
                'entity': 'song',
                'country': country,
                'limit': 1
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('results') and len(data['results']) > 0:
                result = data['results'][0]
                
                # 앨범아트 URL 추출 (고해상도로 변환)
                if result.get('artworkUrl100'):
                    # 100x100을 600x600으로 변경
                    artwork_url = result['artworkUrl100'].replace('100x100', '600x600')
                    logger.info(f"iTunes 앨범아트 검색 성공 ({country}): {song_title} - {artwork_url}")
                    return artwork_url
        
        logger.info(f"iTunes 앨범아트 검색 결과 없음: {song_title}")
        return None
        
    except requests.RequestException as e:
        logger.error(f"iTunes API 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"iTunes 검색 중 예외: {e}")
        return None

async def search_album_art_google(song_title: str, artist_name: str) -> Optional[str]:
    """Google Custom Search API를 사용해서 앨범아트 이미지 검색"""
    
    # Google Custom Search API 설정 (환경변수에서 가져오기)
    api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    if not api_key or not search_engine_id:
        return None
    
    try:
        # 검색 쿼리 구성
        query = f"{song_title} {artist_name} album art cover"
        
        # Google Custom Search API 호출
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'searchType': 'image',
            'imgSize': 'medium',
            'imgType': 'photo',
            'num': 1,  # 첫 번째 결과만
            'safe': 'off'
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('items') and len(data['items']) > 0:
            image_url = data['items'][0]['link']
            logger.info(f"Google 앨범아트 검색 성공: {song_title} - {image_url}")
            return image_url
        else:
            return None
            
    except requests.RequestException as e:
        logger.error(f"Google 앨범아트 검색 API 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"Google 앨범아트 검색 중 예외: {e}")
        return None

async def search_album_art(song_title: str, artist_name: str) -> Optional[str]:
    """앨범아트 검색 (여러 소스 시도)"""
    
    # 1. iTunes Search API 시도 (일본 음악에 가장 적합)
    result = await search_album_art_itunes(song_title, artist_name)
    if result:
        return result
    
    # 2. Google Custom Search 시도 (API 키가 있는 경우)
    result = await search_album_art_google(song_title, artist_name)
    if result:
        return result
    
    return None

def get_default_album_art() -> str:
    """기본 앨범아트 이미지 URL"""
    return "https://via.placeholder.com/300x300/1a1a1a/666666?text=♪"

# === Helper Functions ===

def find_or_create_song_master_v2(song_name: str, artist_id: str) -> str:
    """새로운 구조로 곡 마스터 찾기/생성"""
    songs_master = data_manager.load_songs_master()
    
    # 기존 곡 찾기 (기존 구조 사용)
    for song in songs_master:
        if (song.titles.get('original') == song_name and 
            song.artist.get('original') == artist_id):
            return song.id
    
    # 새 곡 생성
    song_id = generate_id('song', f"{song_name}|{artist_id}")
    current_time = datetime.now().isoformat()
    
    new_song = SongMaster(
        id=song_id,
        titles={'original': song_name, 'korean': '', 'english': '', 'romanized': ''},
        artist={'original': artist_id, 'korean': '', 'english': ''},
        tags=[],
        performance_count=0
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
        
        # 아티스트별 곡 수 (기존 구조 사용)
        artist_counts = {}
        for song in songs_master:
            artist_name = song.artist.get('original')
            if artist_name:
                artist_counts[artist_name] = artist_counts.get(artist_name, 0) + 1
        
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