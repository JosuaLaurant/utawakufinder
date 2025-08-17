from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base schemas
class ArtistBase(BaseModel):
    name: str
    name_korean: Optional[str] = None
    name_english: Optional[str] = None
    name_romanized: Optional[str] = None

class UtaiteBase(BaseModel):
    name: str
    name_korean: Optional[str] = None
    name_english: Optional[str] = None
    name_romanized: Optional[str] = None

class SongMasterBase(BaseModel):
    title: str
    title_korean: Optional[str] = None
    title_english: Optional[str] = None
    title_romanized: Optional[str] = None
    artist_id: int
    album_art_url: Optional[str] = None
    tags: Optional[List[str]] = []

class VideoBase(BaseModel):
    video_id: str
    title: str
    channel: Optional[str] = None
    thumbnail_url: Optional[str] = None

class PerformanceBase(BaseModel):
    song_master_id: int
    utaite_id: int
    video_id: int
    start_time: str
    date: datetime

# Create schemas
class ArtistCreate(ArtistBase):
    pass

class UtaiteCreate(UtaiteBase):
    pass

class SongMasterCreate(SongMasterBase):
    pass

class VideoCreate(VideoBase):
    pass

class PerformanceCreate(PerformanceBase):
    pass

# Response schemas
class Artist(ArtistBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Utaite(UtaiteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SongMaster(SongMasterBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Video(VideoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Performance(PerformanceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Extended response schemas with relationships
class SongMasterWithArtist(SongMaster):
    artist: Artist

class PerformanceWithDetails(Performance):
    song_master: SongMasterWithArtist
    utaite: Utaite
    video: Video

# API response schemas (프론트엔드 호환용)
class PerformanceDetail(BaseModel):
    id: int
    start_time: str
    date: datetime
    song_id: int  # song_master_id의 별칭
    song_title: str
    song_artist: str
    utaite_id: int
    utaite_name: str
    video_id: str  # video.video_id (YouTube ID)
    video_title: str
    video_channel: Optional[str]
    thumbnail_url: Optional[str]
    
    class Config:
        from_attributes = True

class SongMasterDetail(BaseModel):
    id: int
    titles: dict  # {"original": title, "korean": title_korean, ...}
    artist: dict  # {"original": artist_name, "korean": artist_name_korean, ...}
    tags: List[str]
    performance_count: int
    album_art_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class ArtistWithStats(BaseModel):
    id: int
    name: str
    name_korean: Optional[str]
    name_english: Optional[str]
    name_romanized: Optional[str]
    song_count: int
    total_performances: int
    latest_performance: Optional[dict] = None
    first_performance: Optional[dict] = None
    top_songs: List[dict] = []
    
    class Config:
        from_attributes = True

class UtaiteWithStats(BaseModel):
    id: int
    name: str
    name_korean: Optional[str]
    name_english: Optional[str]
    name_romanized: Optional[str]
    total_performances: int
    unique_songs: int
    unique_artists: int
    latest_performance: Optional[dict] = None
    first_performance: Optional[dict] = None
    top_songs: List[dict] = []
    
    class Config:
        from_attributes = True