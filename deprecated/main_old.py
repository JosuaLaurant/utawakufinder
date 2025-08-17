from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import logging
from datetime import datetime
from crawler import extract_video_id, find_comment
import re
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Utawakufinder API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SongEntry(BaseModel):
    id: str  # unique performance ID
    song_master_id: str  # reference to songs_master
    start_time: str
    video_id: str
    video_title: str
    singer: str
    date: str
    thumbnail: Optional[str] = None

class SongMaster(BaseModel):
    id: str  # unique song ID
    titles: dict  # {"original": "ホシキラ", "korean": "호시키라"}
    artist: dict  # {"original": "ランカ・リー/中島愛"}
    tags: List[str]
    performance_count: int

class SongWithDetails(BaseModel):
    # SongEntry fields
    id: str
    song_master_id: str
    start_time: str
    video_id: str
    video_title: str
    singer: str
    date: str
    thumbnail: Optional[str] = None
    # SongMaster fields (joined)
    song_name: str  # from titles.original
    song_artist: str  # from artist.original
    video_url: str  # generated from video_id
    channel: str  # can be derived if needed

class VideoInfo(BaseModel):
    id: str
    title: str
    channel: str
    thumbnail: Optional[str] = None

class ParsedSong(BaseModel):
    start_time: str
    song_name: str
    song_artist: str

class URLRequest(BaseModel):
    url: str
    parsing_mode: str = "auto"  # auto, setlist, simple, description, numbered

class SaveSongsRequest(BaseModel):
    video_info: VideoInfo
    video_url: str
    songs: List[ParsedSong]
    singer_override: Optional[str] = None

DATA_DIR = "data"
SONGS_FILE = os.path.join(DATA_DIR, "songs.json")
SONGS_MASTER_FILE = os.path.join(DATA_DIR, "songs_master.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def load_songs() -> List[SongEntry]:
    if os.path.exists(SONGS_FILE):
        try:
            with open(SONGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [SongEntry(**song) for song in data]
        except:
            return []
    return []

def load_songs_master() -> List[SongMaster]:
    if os.path.exists(SONGS_MASTER_FILE):
        try:
            with open(SONGS_MASTER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [SongMaster(**song) for song in data]
        except:
            return []
    return []

def save_songs(songs: List[SongEntry]):
    with open(SONGS_FILE, 'w', encoding='utf-8') as f:
        json.dump([song.dict() for song in songs], f, ensure_ascii=False, indent=2)

def save_songs_master(songs_master: List[SongMaster]):
    with open(SONGS_MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump([song.dict() for song in songs_master], f, ensure_ascii=False, indent=2)

def get_songs_with_details() -> List[SongWithDetails]:
    """곡 정보와 부른 기록을 조인해서 반환"""
    songs = load_songs()
    songs_master = load_songs_master()
    
    # master를 딕셔너리로 변환 (빠른 조회용)
    master_dict = {master.id: master for master in songs_master}
    
    songs_with_details = []
    for song in songs:
        master = master_dict.get(song.song_master_id)
        if master:
            song_with_details = SongWithDetails(
                # SongEntry fields
                id=song.id,
                song_master_id=song.song_master_id,
                start_time=song.start_time,
                video_id=song.video_id,
                video_title=song.video_title,
                singer=song.singer,
                date=song.date,
                thumbnail=song.thumbnail,
                # SongMaster fields (joined)
                song_name=master.titles.get('original', ''),
                song_artist=master.artist.get('original', ''),
                video_url=f"https://www.youtube.com/watch?v={song.video_id}",
                channel=""  # 필요시 추가
            )
            songs_with_details.append(song_with_details)
    
    return songs_with_details

def find_or_create_song_master(song_name: str, song_artist: str) -> str:
    """곡 마스터에서 찾거나 새로 생성해서 song_master_id 반환"""
    import hashlib
    
    # 기존 마스터 로드
    songs_master = load_songs_master()
    
    # 기존 곡 찾기
    for master in songs_master:
        if (master.titles.get('original') == song_name and 
            master.artist.get('original') == song_artist):
            return master.id
    
    # 새 곡 마스터 생성
    key = f"{song_name}|{song_artist}"
    song_master_id = 'song_' + hashlib.md5(key.encode('utf-8')).hexdigest()[:12]
    
    new_master = SongMaster(
        id=song_master_id,
        titles={"original": song_name},
        artist={"original": song_artist},
        tags=[],
        performance_count=1
    )
    
    songs_master.append(new_master)
    save_songs_master(songs_master)
    
    logger.info(f"새로운 곡 마스터 생성: {song_name} - {song_artist} (ID: {song_master_id})")
    return song_master_id

def update_performance_count():
    """모든 곡의 performance_count 업데이트"""
    songs = load_songs()
    songs_master = load_songs_master()
    
    # 곡별 부른 횟수 계산
    performance_counts = {}
    for song in songs:
        performance_counts[song.song_master_id] = performance_counts.get(song.song_master_id, 0) + 1
    
    # 마스터 정보 업데이트
    for master in songs_master:
        master.performance_count = performance_counts.get(master.id, 0)
    
    save_songs_master(songs_master)

def extract_singer_from_title_and_channel(title: str, channel: str) -> str:
    """제목과 채널명에서 가수명 추출"""
    
    # 1. 채널명에서 가수명 추출 시도 (우선순위)
    channel_patterns = [
        r'^([^/]+)',  # "/" 앞의 첫 번째 부분
        r'^([^・]+)',  # "・" 앞의 첫 번째 부분  
        r'^([^\s]+)',  # 첫 번째 단어
    ]
    
    for pattern in channel_patterns:
        match = re.search(pattern, channel.strip())
        if match:
            singer = match.group(1).strip()
            # 일반적인 채널 키워드가 아닌 경우만 반환
            if singer and not any(keyword in singer.lower() for keyword in ['channel', 'official', 'music', 'vtuber']):
                return singer
    
    # 2. 제목에서 가수명 추출 시도 (fallback)
    title_patterns = [
        r'【([^#].+?)】',  # 【】 안에서 #으로 시작하지 않는 것
        r'\[([^#].+?)\]',  # [] 안에서 #으로 시작하지 않는 것
        r'〔([^#].+?)〕',
        r'《([^#].+?)》',
        r'「([^#].+?)」',
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, title)
        if match:
            singer = match.group(1).strip()
            # 태그나 일반적인 키워드가 아닌 경우만 반환
            if singer and not any(keyword in singer for keyword in ['歌枠', 'karaoke', 'sing', '노래', '부른', '커버']):
                return singer
    
    return ""

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"요청 시작: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"요청 완료: {request.method} {request.url} - 상태코드: {response.status_code} - 처리시간: {process_time:.2f}초")
    
    return response

@app.get("/")
def root():
    logger.info("루트 엔드포인트 호출")
    return {"message": "Utawakufinder API", "version": "1.0.0"}

@app.get("/songs", response_model=List[SongWithDetails])
def get_songs():
    """곡 정보와 조인된 완전한 데이터 반환 (기존 호환성 유지)"""
    logger.info("노래 목록 조회 시작")
    try:
        songs = get_songs_with_details()
        logger.info(f"노래 목록 조회 성공: {len(songs)}곡")
        return songs
    except Exception as e:
        logger.error(f"노래 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"노래 목록 조회 중 오류: {str(e)}")

@app.get("/songs/minimal", response_model=List[SongEntry])
def get_songs_minimal():
    """부른 기록만 반환 (최적화된 데이터)"""
    logger.info("노래 목록 (최소) 조회 시작")
    try:
        songs = load_songs()
        logger.info(f"노래 목록 (최소) 조회 성공: {len(songs)}곡")
        return songs
    except Exception as e:
        logger.error(f"노래 목록 (최소) 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"노래 목록 조회 중 오류: {str(e)}")

@app.get("/songs/master", response_model=List[SongMaster])
def get_songs_master():
    """곡 마스터 정보만 반환"""
    logger.info("곡 마스터 정보 조회 시작")
    try:
        songs_master = load_songs_master()
        logger.info(f"곡 마스터 정보 조회 성공: {len(songs_master)}곡")
        return songs_master
    except Exception as e:
        logger.error(f"곡 마스터 정보 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"곡 마스터 정보 조회 중 오류: {str(e)}")

@app.get("/songs/by-master/{song_master_id}", response_model=List[SongWithDetails])
def get_songs_by_master(song_master_id: str):
    """특정 곡을 부른 모든 기록 반환"""
    logger.info(f"곡별 부른 기록 조회 시작: {song_master_id}")
    try:
        all_songs = get_songs_with_details()
        filtered_songs = [song for song in all_songs if song.song_master_id == song_master_id]
        logger.info(f"곡별 부른 기록 조회 성공: {len(filtered_songs)}개 기록")
        return filtered_songs
    except Exception as e:
        logger.error(f"곡별 부른 기록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"곡별 부른 기록 조회 중 오류: {str(e)}")

@app.get("/artists")
def get_artists():
    """전체 아티스트 목록과 통계 반환"""
    logger.info("아티스트 목록 조회 시작")
    try:
        # songs_master에서 아티스트 정보 가져오기
        songs_master = load_songs_master()
        all_songs = get_songs_with_details()
        
        # 아티스트별 통계 계산
        artist_stats = {}
        
        for master_song in songs_master:
            artist_name = master_song.artist.get("original", "Unknown Artist")
            if artist_name not in artist_stats:
                artist_stats[artist_name] = {
                    "name": artist_name,
                    "song_count": 0,
                    "total_performances": 0,
                    "songs": [],
                    "latest_performance": None,
                    "first_performance": None
                }
            
            artist_stats[artist_name]["song_count"] += 1
            artist_stats[artist_name]["total_performances"] += master_song.performance_count
            artist_stats[artist_name]["songs"].append({
                "id": master_song.id,
                "title": master_song.titles.get("original", "Unknown Title"),
                "performance_count": master_song.performance_count
            })
            
            # 해당 곡의 공연 중 가장 최신/최오래된 것 찾기
            song_performances = [s for s in all_songs if s.song_master_id == master_song.id]
            for perf in song_performances:
                if (artist_stats[artist_name]["latest_performance"] is None or 
                    perf.date > artist_stats[artist_name]["latest_performance"]["date"]):
                    artist_stats[artist_name]["latest_performance"] = {
                        "date": perf.date,
                        "thumbnail": perf.thumbnail,
                        "song_title": perf.song_name
                    }
                
                if (artist_stats[artist_name]["first_performance"] is None or 
                    perf.date < artist_stats[artist_name]["first_performance"]["date"]):
                    artist_stats[artist_name]["first_performance"] = {
                        "date": perf.date,
                        "thumbnail": perf.thumbnail,
                        "song_title": perf.song_name
                    }
        
        # 결과 정리
        result = []
        for artist, stats in artist_stats.items():
            result.append({
                "name": artist,
                "song_count": stats["song_count"],
                "total_performances": stats["total_performances"],
                "latest_performance": stats["latest_performance"],
                "first_performance": stats["first_performance"],
                "top_songs": sorted(stats["songs"], key=lambda x: x["performance_count"], reverse=True)[:5]
            })
        
        # 총 공연 횟수 순으로 정렬
        result.sort(key=lambda x: x["total_performances"], reverse=True)
        
        logger.info(f"아티스트 목록 조회 성공: {len(result)}명")
        return result
    except Exception as e:
        logger.error(f"아티스트 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"아티스트 목록 조회 중 오류: {str(e)}")

@app.get("/artists/songs")
def get_songs_by_artist(name: str):
    """특정 아티스트의 모든 곡과 공연 기록 반환 (쿼리 파라미터 사용)"""
    artist_name = name
    logger.info(f"아티스트별 곡 조회 시작: {artist_name}")
    try:
        # songs_master에서 해당 아티스트의 곡들 찾기
        songs_master = load_songs_master()
        artist_songs = [song for song in songs_master if song.artist.get("original") == artist_name]
        
        # 각 곡의 공연 기록 가져오기
        all_performances = get_songs_with_details()
        result = []
        
        for master_song in artist_songs:
            performances = [p for p in all_performances if p.song_master_id == master_song.id]
            result.append({
                "song_master": master_song,
                "performances": performances
            })
        
        # 공연 횟수 순으로 정렬
        result.sort(key=lambda x: len(x["performances"]), reverse=True)
        
        logger.info(f"아티스트별 곡 조회 성공: {len(result)}곡")
        return result
    except Exception as e:
        logger.error(f"아티스트별 곡 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"아티스트별 곡 조회 중 오류: {str(e)}")

@app.get("/utaites")
def get_utaites():
    """전체 우타이테 목록과 통계 반환"""
    logger.info("우타이테 목록 조회 시작")
    try:
        songs = get_songs_with_details()  # song_artist 포함된 데이터 사용
        # 우타이테별 통계 계산
        utaite_stats = {}
        for song in songs:
            singer = song.singer
            if singer not in utaite_stats:
                utaite_stats[singer] = {
                    "name": singer,
                    "song_count": 0,
                    "unique_songs": set(),
                    "unique_artists": set(),
                    "first_date": song.date,
                    "latest_date": song.date,
                    "latest_thumbnail": song.thumbnail
                }
            
            utaite_stats[singer]["song_count"] += 1
            utaite_stats[singer]["unique_songs"].add(song.song_master_id)
            utaite_stats[singer]["unique_artists"].add(song.song_artist)
            
            # 날짜 비교 (최신, 최오래된)
            if song.date > utaite_stats[singer]["latest_date"]:
                utaite_stats[singer]["latest_date"] = song.date
                utaite_stats[singer]["latest_thumbnail"] = song.thumbnail
            if song.date < utaite_stats[singer]["first_date"]:
                utaite_stats[singer]["first_date"] = song.date
        
        # 결과 정리
        result = []
        for singer, stats in utaite_stats.items():
            result.append({
                "name": singer,
                "song_count": stats["song_count"],
                "unique_song_count": len(stats["unique_songs"]),
                "unique_artist_count": len(stats["unique_artists"]),
                "first_date": stats["first_date"],
                "latest_date": stats["latest_date"],
                "latest_thumbnail": stats["latest_thumbnail"]
            })
        
        # 노래 개수 순으로 정렬
        result.sort(key=lambda x: x["song_count"], reverse=True)
        
        logger.info(f"우타이테 목록 조회 성공: {len(result)}명")
        return result
    except Exception as e:
        logger.error(f"우타이테 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"우타이테 목록 조회 중 오류: {str(e)}")

@app.get("/utaites/songs", response_model=List[SongWithDetails])
def get_songs_by_utaite(name: str):
    """특정 우타이테가 부른 모든 노래 반환 (쿼리 파라미터 사용)"""
    utaite_name = name
    logger.info(f"우타이테별 노래 조회 시작: {utaite_name}")
    try:
        all_songs = get_songs_with_details()
        filtered_songs = [song for song in all_songs if song.singer == utaite_name]
        logger.info(f"우타이테별 노래 조회 성공: {len(filtered_songs)}곡")
        return filtered_songs
    except Exception as e:
        logger.error(f"우타이테별 노래 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"우타이테별 노래 조회 중 오류: {str(e)}")

@app.get("/videos")
def get_videos():
    """호환성을 위한 레거시 엔드포인트 - 영상 단위로 그룹화해서 반환"""
    logger.info("영상 목록 조회 시작 (레거시)")
    try:
        songs = load_songs()
        # 영상별로 그룹화
        videos_dict = {}
        for song in songs:
            if song.video_id not in videos_dict:
                videos_dict[song.video_id] = {
                    "id": song.video_id,
                    "title": song.video_title,
                    "channel": song.channel,
                    "singer": song.singer,
                    "date": song.date,
                    "thumbnail": song.thumbnail,
                    "songs": []
                }
            videos_dict[song.video_id]["songs"].append({
                "start_time": song.start_time,
                "song_name": song.song_name,
                "song_artist": song.song_artist
            })
        
        videos = list(videos_dict.values())
        logger.info(f"영상 목록 조회 성공: {len(videos)}개 영상")
        return videos
    except Exception as e:
        logger.error(f"영상 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"영상 목록 조회 중 오류: {str(e)}")

@app.post("/debug-comments")
def debug_comments(request: URLRequest):
    """댓글 내용을 확인하기 위한 디버그 엔드포인트"""
    logger.info(f"댓글 디버깅 시작: URL={request.url}")
    
    try:
        video_id = extract_video_id(request.url)
        if not video_id:
            raise HTTPException(status_code=400, detail="유효하지 않은 유튜브 URL입니다.")
        
        comments = find_comment(video_id)
        logger.info(f"댓글 {len(comments)}개 가져옴")
        
        # 처음 10개 댓글만 반환 (너무 길 수 있으므로)
        return {
            "video_id": video_id,
            "total_comments": len(comments),
            "sample_comments": comments[:10]
        }
    except Exception as e:
        logger.error(f"댓글 디버깅 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse-video")
def parse_video(request: URLRequest):
    logger.info(f"비디오 파싱 시작: URL={request.url}")
    
    try:
        # 1단계: 비디오 ID 추출
        logger.info("1단계: 비디오 ID 추출 중...")
        video_id = extract_video_id(request.url)
        if not video_id:
            logger.error(f"유효하지 않은 URL: {request.url}")
            raise HTTPException(status_code=400, detail="유효하지 않은 유튜브 URL입니다.")
        logger.info(f"비디오 ID 추출 성공: {video_id}")
        
        # 2단계: 비디오 정보 가져오기
        logger.info("2단계: 비디오 정보 가져오는 중...")
        video_info = get_video_info(video_id)
        if not video_info:
            logger.error(f"비디오 정보 가져오기 실패: {video_id}")
            raise HTTPException(status_code=404, detail="비디오 정보를 가져올 수 없습니다.")
        logger.info(f"비디오 정보 가져오기 성공: {video_info.title}")
        
        # 3단계: 댓글 가져오기
        logger.info("3단계: 댓글 가져오는 중...")
        comments = find_comment(video_id)
        logger.info(f"댓글 가져오기 성공: {len(comments)}개 댓글")
        
        # 디버깅: 처음 3개 댓글 내용 출력
        for i, comment in enumerate(comments[:3]):
            logger.info(f"댓글 {i+1}: {comment[:200]}...")
        
        # 디버깅: 타임스탬프가 포함된 댓글 찾기
        timestamp_comments = []
        for comment in comments:
            if any(pattern in comment for pattern in [':', '00', '01', '02', '03', '04', '05']):
                timestamp_comments.append(comment)
        logger.info(f"타임스탬프 패턴 포함 댓글: {len(timestamp_comments)}개")
        
        # 처음 3개 타임스탬프 댓글 출력
        for i, comment in enumerate(timestamp_comments[:3]):
            logger.info(f"타임스탬프 댓글 {i+1}: {comment[:200]}...")
        
        # 4단계: 댓글에서 직접 타임스탬프 파싱 (파일 저장 없이)
        logger.info(f"4단계: 댓글에서 직접 타임스탬프 파싱 중... (모드: {request.parsing_mode})")
        songs = parse_songs_from_comments(comments, request.parsing_mode)
        if not songs:
            logger.warning("파싱된 노래가 없습니다")
            songs = []
        else:
            logger.info(f"타임스탬프 파싱 성공: {len(songs)}곡")
        
        # 5단계: ParsedSong 객체로 변환
        logger.info("5단계: ParsedSong 객체 변환 중...")
        song_objects = [ParsedSong(**song) for song in songs]
        logger.info("ParsedSong 객체 변환 완료")
        
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
    logger.info(f"노래 저장 시작: Video ID={request.video_info.id}, 곡 수={len(request.songs)}")
    
    try:
        # 1단계: 기존 노래 목록 로드
        logger.info("1단계: 기존 노래 목록 로드 중...")
        existing_songs = load_songs()
        logger.info(f"기존 노래 {len(existing_songs)}곡 로드됨")
        
        # 2단계: 중복 확인 (같은 비디오의 같은 시간대 노래)
        logger.info("2단계: 중복 노래 확인 중...")
        existing_video_songs = [s for s in existing_songs if s.video_id == request.video_info.id]
        if existing_video_songs:
            logger.warning(f"중복 영상 발견: {request.video_info.id}")
            raise HTTPException(status_code=400, detail="이미 등록된 영상입니다.")
        logger.info("중복 노래 없음")
        
        # 3단계: 부른 사람 결정 (사용자 입력 우선, 없으면 자동 추출)
        logger.info("3단계: 부른 사람 결정 중...")
        if request.singer_override:
            singer = request.singer_override.strip()
            logger.info(f"사용자 지정 부른 사람: '{singer}'")
        else:
            singer = extract_singer_from_title_and_channel(request.video_info.title, request.video_info.channel)
            logger.info(f"자동 추출 부른 사람: '{singer}' (제목: '{request.video_info.title}', 채널: '{request.video_info.channel}')")
        
        # 4단계: 각 노래를 개별 SongEntry로 변환 (새로운 구조)
        logger.info("4단계: 노래별 SongEntry 객체 생성 중...")
        new_songs = []
        current_date = datetime.now().isoformat()
        
        for i, song in enumerate(request.songs):
            # song_master_id 찾거나 생성
            song_master_id = find_or_create_song_master(song.song_name, song.song_artist)
            
            song_id = f"{request.video_info.id}_{i}_{song.start_time.replace(':', '')}"
            song_entry = SongEntry(
                id=song_id,
                song_master_id=song_master_id,
                start_time=song.start_time,
                video_id=request.video_info.id,
                video_title=request.video_info.title,
                singer=singer,
                date=current_date,
                thumbnail=f"https://img.youtube.com/vi/{request.video_info.id}/mqdefault.jpg"
            )
            new_songs.append(song_entry)
        
        logger.info(f"새 노래 객체 생성 완료: {len(new_songs)}곡")
        
        # 5단계: 노래 목록에 추가
        logger.info("5단계: 노래 목록에 추가 중...")
        all_songs = existing_songs + new_songs
        
        # 6단계: 저장
        logger.info("6단계: 파일에 저장 중...")
        save_songs(all_songs)
        
        # 7단계: performance_count 업데이트
        logger.info("7단계: 곡별 부른 횟수 업데이트 중...")
        update_performance_count()
        
        logger.info("노래 저장 완료")
        
        return {"message": f"{len(new_songs)}곡이 성공적으로 저장되었습니다.", "songs": new_songs}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"노래 저장 중 예외 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"저장 중 오류가 발생했습니다: {str(e)}")

# 호환성을 위한 레거시 엔드포인트
@app.post("/save-video")
def save_video_legacy(request: SaveSongsRequest):
    logger.info("레거시 save-video 엔드포인트 호출 - save-songs로 리다이렉트")
    return save_songs_endpoint(request)

def parse_songs_from_comments(comments: List[str], parsing_mode: str = "auto") -> List[dict]:
    """댓글 리스트에서 직접 타임스탬프를 파싱"""
    songs = []
    parentheses_pattern = re.compile(r'\([^)]*\)')
    
    if parsing_mode == "setlist":
        songs.extend(parse_setlist_format(comments, parentheses_pattern))
    elif parsing_mode == "simple":
        songs.extend(parse_simple_format(comments, parentheses_pattern))
    elif parsing_mode == "description":
        songs.extend(parse_description_format(comments, parentheses_pattern))
    elif parsing_mode == "numbered":
        songs.extend(parse_numbered_tracks(comments, parentheses_pattern))
    else:  # auto mode
        # 번호 패턴 먼저 시도 (01|, 02|, ...)
        numbered_songs = parse_numbered_tracks(comments, parentheses_pattern)
        if numbered_songs:
            songs.extend(numbered_songs)
        else:
            # SET LIST 형식 시도
            setlist_songs = parse_setlist_format(comments, parentheses_pattern)
            if setlist_songs:
                songs.extend(setlist_songs)
            else:
                # 일반적인 형식들 시도
                songs.extend(parse_simple_format(comments, parentheses_pattern))
                if not songs:
                    songs.extend(parse_description_format(comments, parentheses_pattern))
    
    logger.info(f"댓글에서 {len(songs)}곡 추출됨 (모드: {parsing_mode})")
    return songs

def parse_setlist_format(comments: List[str], parentheses_pattern) -> List[dict]:
    """SET LIST 형식 파싱"""
    songs = []
    time_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2})')
    
    for comment in comments:
        if "SET LIST" in comment:
            logger.info(f"SET LIST 댓글 발견: {comment[:100]}...")
            
            setlist_content = comment.split("SET LIST", 1)[1] if "SET LIST" in comment else comment
            parts = time_pattern.split(setlist_content)
            
            current_time = None
            for i, part in enumerate(parts):
                if time_pattern.match(part):
                    current_time = part
                elif current_time and part.strip():
                    if ' / ' in part:
                        title_artist = part.strip()
                        if title_artist.startswith(' '):
                            title_artist = title_artist[1:]
                        
                        title_parts = title_artist.split(' / ', 1)
                        if len(title_parts) == 2:
                            title = title_parts[0].strip()
                            artist = title_parts[1].strip()
                            
                            next_time_match = time_pattern.search(artist)
                            if next_time_match:
                                artist = artist[:next_time_match.start()].strip()
                            
                            cleaned_title = parentheses_pattern.sub('', title).strip()
                            cleaned_artist = parentheses_pattern.sub('', artist).strip()
                            
                            songs.append({
                                'start_time': current_time,
                                'song_name': cleaned_title,
                                'song_artist': cleaned_artist
                            })
    return songs

def parse_simple_format(comments: List[str], parentheses_pattern) -> List[dict]:
    """간단한 타임스탬프 형식 파싱"""
    songs = []
    patterns = [
        # "시간 | 제목 | 아티스트"
        re.compile(r"^\s*(\d{1,2}:\d{2}:\d{2}).*?\|\s*(.*?)\s*\|\s*(.*)$"),
        # "시간 제목 / 아티스트"  
        re.compile(r"^\s*(\d{1,2}:\d{2}:\d{2})\s+([^/]+?)\s*/\s*(.+)$"),
        # "시간 제목 - 아티스트"
        re.compile(r"^\s*(\d{1,2}:\d{2}:\d{2})\s+(.+?)\s*-\s*(.+)$"),
        # "시간 제목"
        re.compile(r"^\s*(\d{1,2}:\d{2}:\d{2})\s+(.+)$")
    ]
    
    for comment in comments:
        for pattern in patterns:
            match = pattern.search(comment)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    start_time, title, artist = groups
                elif len(groups) == 2:
                    start_time, title = groups
                    artist = "Unknown"
                else:
                    continue
                    
                cleaned_title = parentheses_pattern.sub('', title).strip()
                cleaned_artist = parentheses_pattern.sub('', artist).strip()
                
                songs.append({
                    'start_time': start_time.strip(),
                    'song_name': cleaned_title,
                    'song_artist': cleaned_artist
                })
                break
    return songs

def parse_numbered_tracks(comments: List[str], parentheses_pattern) -> List[dict]:
    """01|, 02|, 03| 형식의 번호가 있는 트랙 추출 (개수 제한 없음)"""
    songs = []
    # 더 유연한 번호 패턴들
    patterns = [
        # "0:02:36 ~ 0:06:02 01| Tasting my love! | 苺咲べりぃ(Maisaki Berry)"
        re.compile(r"^(\d{1,2}:\d{2}:\d{2})\s*~\s*\d{1,2}:\d{2}:\d{2}\s*(\d{1,2})\|\s*([^|]+?)\s*\|\s*(.+)$"),
        # "01| Title | Artist" (시간 없는 형식)
        re.compile(r"^(\d{1,2})\|\s*([^|]+?)\s*\|\s*(.+)$"),
        # "1. 00:00 Title - Artist" 
        re.compile(r"^(\d{1,2})\.\s*(\d{1,2}:\d{2}:\d{2})\s+(.+?)\s*[-–—]\s*(.+)$"),
        # "1. 00:00 Title"
        re.compile(r"^(\d{1,2})\.\s*(\d{1,2}:\d{2}:\d{2})\s+(.+)$"),
    ]
    
    for comment in comments:
        lines = comment.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in patterns:
                match = pattern.search(line)
                if match:
                    groups = match.groups()
                    
                    if len(groups) == 4:
                        if ":" in groups[0]:  # 시간이 첫 번째인 경우
                            start_time, track_num, title, artist = groups
                        else:  # 번호가 첫 번째인 경우
                            track_num, start_time, title, artist = groups
                    elif len(groups) == 3:
                        if ":" in groups[1]:  # 번호, 시간, 제목 순서
                            track_num, start_time, title = groups
                            artist = "Unknown"
                        else:  # 번호, 제목, 아티스트 순서 (시간 없음)
                            track_num, title, artist = groups
                            start_time = "0:00:00"  # 기본값
                    else:
                        continue
                    
                    try:
                        track_number = int(track_num)
                        # 합리적인 트랙 번호 범위 (1~99)
                        if 1 <= track_number <= 99:
                            cleaned_title = parentheses_pattern.sub('', title).strip()
                            cleaned_artist = parentheses_pattern.sub('', artist).strip()
                            
                            # 시간 형식 정규화
                            if len(start_time.split(':')) == 2:
                                start_time = "0:" + start_time
                            
                            songs.append({
                                'start_time': start_time.strip(),
                                'song_name': cleaned_title,
                                'song_artist': cleaned_artist,
                                'track_number': track_number
                            })
                            break  # 패턴 매칭되면 다음 패턴 시도하지 않음
                    except ValueError:
                        continue
    
    # 트랙 번호순으로 정렬
    songs.sort(key=lambda x: x.get('track_number', 999))
    
    # track_number 필드 제거 (응답에는 포함하지 않음)
    for song in songs:
        if 'track_number' in song:
            del song['track_number']
    
    return songs

def parse_description_format(comments: List[str], parentheses_pattern) -> List[dict]:
    """설명란이나 다른 형식 파싱"""
    songs = []
    seen_songs = set()  # 중복 제거용
    # 더 유연한 패턴들
    patterns = [
        # "0:02:36 ~ 0:06:02 01| Tasting my love! | 苺咲べりぃ(Maisaki Berry)" - 정확한 순서 매칭
        re.compile(r"^(\d{1,2}:\d{2}:\d{2})\s*~\s*\d{1,2}:\d{2}:\d{2}\s*(\d{2})\|\s*([^|]+?)\s*\|\s*(.+)$"),
        # "02:36【Tasting my love!】"
        re.compile(r"^(\d{1,2}:\d{2})【([^】]+)】"),
        # "1:19:37 　夢が見える夢を見た"
        re.compile(r"^\s*(\d{1,2}:\d{2}:\d{2})\s*[　\s]+(.+)$"),
        # "00:00 제목 - 아티스트"
        re.compile(r"^\s*(\d{1,2}:\d{2}:\d{2})\s+(.+?)\s*[-–—]\s*(.+)$"),
        # "00:00 제목 - 아티스트" (MM:SS 형식)
        re.compile(r"^\s*(\d{1,2}:\d{2})\s+(.+?)\s*[-–—]\s*(.+)$"),
        # "00:00 제목"
        re.compile(r"^\s*(\d{1,2}:\d{2}:\d{2})\s+(.+)$"),
        # "00:00 제목" (MM:SS 형식)
        re.compile(r"^\s*(\d{1,2}:\d{2})\s+(.+)$"),
        # 숫자. 시간 제목
        re.compile(r"^\s*\d+\.\s*(\d{1,2}:\d{2}:\d{2})\s+(.+)$"),
        re.compile(r"^\s*\d+\.\s*(\d{1,2}:\d{2})\s+(.+)$"),
    ]
    
    for comment in comments:
        # 여러 줄 댓글에서 각 줄 처리
        lines = comment.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in patterns:
                match = pattern.search(line)
                if match:
                    groups = match.groups()
                    if len(groups) == 4:  # "0:02:36 ~ 0:06:02 01| Tasting my love! | 苺咲べりぃ(Maisaki Berry)"
                        start_time, track_num, title, artist = groups
                    elif len(groups) == 3:
                        start_time, title, artist = groups
                    elif len(groups) == 2:
                        start_time, title = groups
                        artist = "Unknown"
                    else:
                        continue
                    
                    # 시간 형식 정규화 (MM:SS -> 0:MM:SS)
                    if len(start_time.split(':')) == 2:
                        start_time = "0:" + start_time
                        
                    cleaned_title = parentheses_pattern.sub('', title).strip()
                    cleaned_artist = parentheses_pattern.sub('', artist).strip()
                    
                    # 제목 필터링 개선
                    skip_keywords = ['ありがとう', 'おめでとう', '最高', '感動', 'ドキドキ', '楽しそう', 
                                   '衣装チェンジ', '可愛すぎる', '魔法で', 'からの', 'ダンス', 'チェンジ']
                    
                    # track_num이 있는 경우 (01|, 02|, ... 패턴) 우선 처리
                    if 'track_num' in locals() and track_num:
                        try:
                            track_number = int(track_num)
                            if 1 <= track_number <= 99:  # 합리적인 범위
                                is_valid_title = True
                            else:
                                is_valid_title = False
                        except ValueError:
                            is_valid_title = False
                    else:
                        # 일반적인 필터링 강화
                        is_valid_title = (len(cleaned_title) > 2 and 
                                        not cleaned_title.isdigit() and 
                                        not any(keyword in cleaned_title for keyword in skip_keywords) and
                                        not cleaned_title.startswith('【') and
                                        not cleaned_title.endswith('】') and
                                        '!' not in cleaned_title[-3:] and
                                        len(cleaned_title) < 30)  # 너무 긴 제목 제외
                        
                        # 특별 허용 패턴 (유명한 곡명들)
                        allowed_patterns = ['love', 'music', 'dream', 'star', 'night', 'heart']
                        if (any(pattern in cleaned_title.lower() for pattern in allowed_patterns) and 
                            len(cleaned_title) < 20):
                            is_valid_title = True
                            
                    if is_valid_title:
                        # 중복 체크
                        song_key = f"{cleaned_title}_{start_time}"
                        if song_key not in seen_songs:
                            seen_songs.add(song_key)
                            songs.append({
                                'start_time': start_time.strip(),
                                'song_name': cleaned_title,
                                'song_artist': cleaned_artist
                            })
                    break
    return songs

def get_video_info(video_id: str) -> Optional[VideoInfo]:
    try:
        import requests
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
        
        if not YOUTUBE_API_KEY:
            logger.error("YOUTUBE_API_KEY가 환경변수에 설정되지 않았습니다.")
            return None
        
        base_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "id": video_id,
            "key": YOUTUBE_API_KEY,
        }
        
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("items"):
                item = data["items"][0]["snippet"]
                return VideoInfo(
                    id=video_id,
                    title=item["title"],
                    channel=item["channelTitle"],
                    thumbnail=f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                )
        return None
    except:
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9030)
