"""
새로운 정규화된 데이터 모델
PostgreSQL 이관을 고려한 구조
"""
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

# === Core Models (DB Tables) ===

class Utaite(BaseModel):
    """우타이테 마스터 테이블"""
    id: str  # utaite_xxxxx
    names: Dict[str, str]  # {"original": "憂涙といろ", "korean": "우루이토이로", "english": "Urui Toiro"}
    performance_count: int = 0
    first_appearance: Optional[str] = None
    latest_appearance: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Artist(BaseModel):
    """아티스트 마스터 테이블"""
    id: str  # artist_xxxxx
    names: Dict[str, str]  # {"original": "ランカ・リー", "korean": "란카 리", "english": "Ranka Lee"}
    song_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class SongMaster(BaseModel):
    """곡 마스터 테이블 (기존 호환성 유지)"""
    id: str  # song_xxxxx
    titles: Dict[str, str]  # {"original": "ホシキラ", "korean": "호시키라", "english": "Hoshikira"}
    artist: Dict[str, str]  # {"original": "ランカ・リー", "korean": "란카 리"} - 기존 호환성
    artist_id: Optional[str] = None  # reference to Artist (향후 확장용)
    tags: List[str] = []
    performance_count: int = 0
    album_art_url: Optional[str] = None  # 앨범아트 이미지 URL
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Video(BaseModel):
    """비디오 마스터 테이블"""
    id: str  # YouTube video ID
    title: str
    channel: str
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None  # seconds
    published_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Performance(BaseModel):
    """부른 기록 테이블 (기존 SongEntry)"""
    id: str  # performance_xxxxx
    song_master_id: str  # reference to SongMaster
    utaite_id: str  # reference to Utaite
    video_id: str  # reference to Video
    start_time: str  # "0:28:42" format
    start_time_seconds: Optional[int] = None  # for sorting
    date: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# === API Response Models ===

class PerformanceWithDetails(BaseModel):
    """조인된 부른 기록 (API 응답용)"""
    # Performance fields
    id: str
    start_time: str
    date: str
    
    # Song info (from SongMaster + Artist)
    song_id: str
    song_title: str  # from titles.original or preferred language
    song_artist: str  # from artist names.original or preferred language
    
    # Utaite info
    utaite_id: str
    utaite_name: str  # from names.original or preferred language
    
    # Video info
    video_id: str
    video_title: str
    video_channel: str
    thumbnail_url: str

class UtaiteWithStats(BaseModel):
    """통계가 포함된 우타이테 정보"""
    id: str
    name: str  # preferred language
    names: Dict[str, str]  # all languages
    performance_count: int
    unique_song_count: int
    unique_artist_count: int
    first_performance: Optional[str]
    latest_performance: Optional[str]
    latest_thumbnail: Optional[str]

class ArtistWithStats(BaseModel):
    """통계가 포함된 아티스트 정보"""
    id: str
    name: str  # preferred language
    names: Dict[str, str]  # all languages
    song_count: int
    total_performances: int
    latest_performance: Optional[Dict]
    first_performance: Optional[Dict]
    top_songs: List[Dict]

# === Request Models ===

class ParsedSong(BaseModel):
    """파싱된 곡 정보 (기존 유지)"""
    start_time: str
    song_name: str
    song_artist: str

class VideoInfo(BaseModel):
    """비디오 정보 (기존 유지)"""
    id: str
    title: str
    channel: str
    thumbnail: Optional[str] = None

class URLRequest(BaseModel):
    """URL 파싱 요청 (기존 유지)"""
    url: str
    parsing_mode: str = "auto"

class SaveSongsRequest(BaseModel):
    """곡 저장 요청 (기존 유지)"""
    video_info: VideoInfo
    video_url: str
    songs: List[ParsedSong]
    singer_override: Optional[str] = None

# === Utility Functions ===

def time_to_seconds(time_str: str) -> int:
    """시간 문자열을 초로 변환 (0:28:42 -> 1722)"""
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = map(int, parts)
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = map(int, parts)
        return m * 60 + s
    else:
        return int(parts[0])

def generate_id(prefix: str, source: str) -> str:
    """ID 생성 헬퍼"""
    import hashlib
    hash_part = hashlib.md5(source.encode('utf-8')).hexdigest()[:12]
    return f"{prefix}_{hash_part}"