"""
새로운 정규화된 구조를 위한 데이터 매니저
PostgreSQL 이관을 고려한 설계
"""
import json
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from models import *

logger = logging.getLogger(__name__)

class DataManager:
    """데이터 파일 관리 클래스"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """데이터 디렉토리 생성"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    # === File Paths ===
    @property
    def utaites_file(self) -> str:
        return os.path.join(self.data_dir, "utaites_master.json")
    
    @property
    def artists_file(self) -> str:
        return os.path.join(self.data_dir, "artists_master.json")
    
    @property
    def songs_master_file(self) -> str:
        return os.path.join(self.data_dir, "songs_master.json")
    
    @property
    def videos_file(self) -> str:
        return os.path.join(self.data_dir, "videos_master.json")
    
    @property
    def performances_file(self) -> str:
        return os.path.join(self.data_dir, "songs.json")  # 기존 파일명 유지
    
    # === Load Methods ===
    def load_utaites(self) -> List[Utaite]:
        """우타이테 마스터 로드"""
        if not os.path.exists(self.utaites_file):
            return []
        try:
            with open(self.utaites_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Utaite(**item) for item in data]
        except Exception as e:
            logger.error(f"우타이테 로드 실패: {e}")
            return []
    
    def load_artists(self) -> List[Artist]:
        """아티스트 마스터 로드"""
        if not os.path.exists(self.artists_file):
            return []
        try:
            with open(self.artists_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Artist(**item) for item in data]
        except Exception as e:
            logger.error(f"아티스트 로드 실패: {e}")
            return []
    
    def load_songs_master(self) -> List[SongMaster]:
        """곡 마스터 로드"""
        if not os.path.exists(self.songs_master_file):
            return []
        try:
            with open(self.songs_master_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [SongMaster(**item) for item in data]
        except Exception as e:
            logger.error(f"곡 마스터 로드 실패: {e}")
            return []
    
    def load_videos(self) -> List[Video]:
        """비디오 마스터 로드"""
        if not os.path.exists(self.videos_file):
            return []
        try:
            with open(self.videos_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Video(**item) for item in data]
        except Exception as e:
            logger.error(f"비디오 로드 실패: {e}")
            return []
    
    def load_performances(self) -> List[Performance]:
        """부른 기록 로드"""
        if not os.path.exists(self.performances_file):
            return []
        try:
            with open(self.performances_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                performances = []
                for item in data:
                    # 기존 구조 호환성
                    perf_data = {
                        'id': item['id'],
                        'song_master_id': item['song_master_id'],
                        'utaite_id': item.get('utaite_id', ''),
                        'video_id': item['video_id'],
                        'start_time': item['start_time'],
                        'start_time_seconds': time_to_seconds(item['start_time']),
                        'date': item['date']
                    }
                    performances.append(Performance(**perf_data))
                return performances
        except Exception as e:
            logger.error(f"부른 기록 로드 실패: {e}")
            return []
    
    # === Save Methods ===
    def save_utaites(self, utaites: List[Utaite]):
        """우타이테 마스터 저장"""
        try:
            with open(self.utaites_file, 'w', encoding='utf-8') as f:
                data = [utaite.dict() for utaite in utaites]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"우타이테 저장 실패: {e}")
            raise
    
    def save_artists(self, artists: List[Artist]):
        """아티스트 마스터 저장"""
        try:
            with open(self.artists_file, 'w', encoding='utf-8') as f:
                data = [artist.dict() for artist in artists]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"아티스트 저장 실패: {e}")
            raise
    
    def save_songs_master(self, songs: List[SongMaster]):
        """곡 마스터 저장"""
        try:
            with open(self.songs_master_file, 'w', encoding='utf-8') as f:
                data = [song.dict() for song in songs]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"곡 마스터 저장 실패: {e}")
            raise
    
    def save_videos(self, videos: List[Video]):
        """비디오 마스터 저장"""
        try:
            with open(self.videos_file, 'w', encoding='utf-8') as f:
                data = [video.dict() for video in videos]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"비디오 저장 실패: {e}")
            raise
    
    def save_performances(self, performances: List[Performance]):
        """부른 기록 저장"""
        try:
            with open(self.performances_file, 'w', encoding='utf-8') as f:
                data = []
                for perf in performances:
                    # 기존 구조와 호환성 유지
                    item = {
                        'id': perf.id,
                        'song_master_id': perf.song_master_id,
                        'utaite_id': perf.utaite_id,
                        'video_id': perf.video_id,
                        'start_time': perf.start_time,
                        'date': perf.date
                    }
                    data.append(item)
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"부른 기록 저장 실패: {e}")
            raise
    
    # === Helper Methods ===
    def get_performances_with_details(self, language: str = "original") -> List[PerformanceWithDetails]:
        """조인된 상세 부른 기록 반환"""
        performances = self.load_performances()
        utaites = self.load_utaites()
        songs_master = self.load_songs_master()
        artists = self.load_artists()
        videos = self.load_videos()
        
        # 빠른 조회를 위한 딕셔너리 생성
        utaites_dict = {u.id: u for u in utaites}
        songs_dict = {s.id: s for s in songs_master}
        artists_dict = {a.id: a for a in artists}
        videos_dict = {v.id: v for v in videos}
        
        results = []
        for perf in performances:
            utaite = utaites_dict.get(perf.utaite_id)
            song = songs_dict.get(perf.song_master_id)
            
            if not utaite or not song:
                continue
                
            # 기존 구조 호환성 - artist 필드에서 직접 가져오기
            video = videos_dict.get(perf.video_id)
            
            # 언어별 이름 선택
            utaite_name = utaite.names.get(language) or utaite.names.get('original', '')
            song_title = song.titles.get(language) or song.titles.get('original', '')
            artist_name = song.artist.get(language) or song.artist.get('original', '') if song.artist else ''
            
            detail = PerformanceWithDetails(
                id=perf.id,
                start_time=perf.start_time,
                date=perf.date,
                song_id=song.id,
                song_title=song_title,
                song_artist=artist_name,
                utaite_id=utaite.id,
                utaite_name=utaite_name,
                video_id=perf.video_id,
                video_title=video.title if video else '',
                video_channel=video.channel if video else '',
                thumbnail_url=video.thumbnail_url if video else f"https://img.youtube.com/vi/{perf.video_id}/mqdefault.jpg"
            )
            results.append(detail)
        
        return results
    
    def find_or_create_utaite(self, name: str) -> str:
        """우타이테 찾기 또는 생성"""
        utaites = self.load_utaites()
        
        # 기존 우타이테 찾기
        for utaite in utaites:
            if utaite.names.get('original') == name:
                return utaite.id
        
        # 새 우타이테 생성
        new_id = generate_id('utaite', name)
        current_time = datetime.now().isoformat()
        
        new_utaite = Utaite(
            id=new_id,
            names={'original': name, 'korean': '', 'english': '', 'romanized': ''},
            performance_count=0,
            created_at=current_time,
            updated_at=current_time
        )
        
        utaites.append(new_utaite)
        self.save_utaites(utaites)
        
        logger.info(f"새 우타이테 생성: {name} (ID: {new_id})")
        return new_id
    
    def find_or_create_artist(self, name: str) -> str:
        """아티스트 찾기 또는 생성"""
        artists = self.load_artists()
        
        # 기존 아티스트 찾기
        for artist in artists:
            if artist.names.get('original') == name:
                return artist.id
        
        # 새 아티스트 생성
        new_id = generate_id('artist', name)
        current_time = datetime.now().isoformat()
        
        new_artist = Artist(
            id=new_id,
            names={'original': name, 'korean': '', 'english': '', 'romanized': ''},
            song_count=0,
            created_at=current_time,
            updated_at=current_time
        )
        
        artists.append(new_artist)
        self.save_artists(artists)
        
        logger.info(f"새 아티스트 생성: {name} (ID: {new_id})")
        return new_id

# 전역 데이터 매니저 인스턴스
data_manager = DataManager()