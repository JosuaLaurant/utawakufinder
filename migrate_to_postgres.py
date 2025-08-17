#!/usr/bin/env python3
"""
기존 JSON 데이터를 PostgreSQL로 마이그레이션하는 스크립트
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Set
from sqlalchemy.orm import Session
from database import engine, get_db, Artist, Utaite, SongMaster, Video, Performance
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostgreSQLMigrator:
    def __init__(self):
        self.db = next(get_db())
        self.artist_map: Dict[str, int] = {}  # 아티스트 이름 -> ID 매핑
        self.utaite_map: Dict[str, int] = {}  # 우타이테 이름 -> ID 매핑
        self.song_map: Dict[str, int] = {}    # 곡 제목+아티스트 -> ID 매핑
        self.video_map: Dict[str, int] = {}   # 비디오 ID -> DB ID 매핑
        
    def load_json_data(self, file_path: str) -> List[dict]:
        """JSON 파일에서 데이터를 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"JSON 파일 로드 완료: {len(data)}개 항목")
                return data
        except FileNotFoundError:
            logger.error(f"파일을 찾을 수 없습니다: {file_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return []
    
    def get_or_create_artist(self, artist_name: str) -> int:
        """아티스트를 찾거나 생성하고 ID 반환"""
        if artist_name in self.artist_map:
            return self.artist_map[artist_name]
        
        # 기존 아티스트 확인
        existing = self.db.query(Artist).filter(Artist.name == artist_name).first()
        if existing:
            self.artist_map[artist_name] = existing.id
            return existing.id
        
        # 새 아티스트 생성
        new_artist = Artist(name=artist_name)
        self.db.add(new_artist)
        self.db.commit()
        self.db.refresh(new_artist)
        
        self.artist_map[artist_name] = new_artist.id
        logger.info(f"새 아티스트 생성: {artist_name} (ID: {new_artist.id})")
        return new_artist.id
    
    def get_or_create_utaite(self, utaite_name: str) -> int:
        """우타이테를 찾거나 생성하고 ID 반환"""
        if utaite_name in self.utaite_map:
            return self.utaite_map[utaite_name]
        
        # 기존 우타이테 확인
        existing = self.db.query(Utaite).filter(Utaite.name == utaite_name).first()
        if existing:
            self.utaite_map[utaite_name] = existing.id
            return existing.id
        
        # 새 우타이테 생성
        new_utaite = Utaite(name=utaite_name)
        self.db.add(new_utaite)
        self.db.commit()
        self.db.refresh(new_utaite)
        
        self.utaite_map[utaite_name] = new_utaite.id
        logger.info(f"새 우타이테 생성: {utaite_name} (ID: {new_utaite.id})")
        return new_utaite.id
    
    def get_or_create_song_master(self, title: str, artist_name: str, tags: List[str] = None, album_art_url: str = None) -> int:
        """곡 마스터를 찾거나 생성하고 ID 반환"""
        song_key = f"{title}|{artist_name}"
        if song_key in self.song_map:
            return self.song_map[song_key]
        
        artist_id = self.get_or_create_artist(artist_name)
        
        # 기존 곡 확인
        existing = self.db.query(SongMaster).filter(
            SongMaster.title == title,
            SongMaster.artist_id == artist_id
        ).first()
        
        if existing:
            self.song_map[song_key] = existing.id
            # 앨범 아트 URL 업데이트 (없었다면)
            if album_art_url and not existing.album_art_url:
                existing.album_art_url = album_art_url
                self.db.commit()
            return existing.id
        
        # 새 곡 생성
        new_song = SongMaster(
            title=title,
            artist_id=artist_id,
            tags=tags or [],
            album_art_url=album_art_url
        )
        self.db.add(new_song)
        self.db.commit()
        self.db.refresh(new_song)
        
        self.song_map[song_key] = new_song.id
        logger.info(f"새 곡 생성: {title} by {artist_name} (ID: {new_song.id})")
        return new_song.id
    
    def get_or_create_video(self, video_id: str, title: str, channel: str = None, thumbnail_url: str = None) -> int:
        """비디오를 찾거나 생성하고 ID 반환"""
        if video_id in self.video_map:
            return self.video_map[video_id]
        
        # 기존 비디오 확인
        existing = self.db.query(Video).filter(Video.video_id == video_id).first()
        if existing:
            self.video_map[video_id] = existing.id
            return existing.id
        
        # 새 비디오 생성
        new_video = Video(
            video_id=video_id,
            title=title,
            channel=channel,
            thumbnail_url=thumbnail_url
        )
        self.db.add(new_video)
        self.db.commit()
        self.db.refresh(new_video)
        
        self.video_map[video_id] = new_video.id
        logger.info(f"새 비디오 생성: {video_id} (ID: {new_video.id})")
        return new_video.id
    
    def migrate_performance_data(self, performances_data: List[dict]):
        """공연 데이터를 마이그레이션"""
        logger.info("공연 데이터 마이그레이션 시작...")
        
        # 필요한 마스터 데이터 로드
        songs_master = self.load_json_data("data/songs_master.json")
        utaites_master = self.load_json_data("data/utaites_master.json")
        artists_master = self.load_json_data("data/artists_master.json")
        videos_master = self.load_json_data("data/videos_master.json")
        
        # 마스터 데이터를 딕셔너리로 변환
        songs_dict = {s['id']: s for s in songs_master}
        utaites_dict = {u['id']: u for u in utaites_master}
        artists_dict = {a['id']: a for a in artists_master}
        videos_dict = {v['id']: v for v in videos_master}
        
        migrated_count = 0
        for perf in performances_data:
            try:
                # 필수 필드 확인
                required_fields = ['song_master_id', 'utaite_id', 'video_id', 'start_time', 'date']
                if not all(field in perf for field in required_fields):
                    logger.warning(f"필수 필드 누락: {perf}")
                    continue
                
                # 마스터 데이터에서 정보 조회
                song_master = songs_dict.get(perf['song_master_id'])
                utaite_master = utaites_dict.get(perf['utaite_id'])
                video_master = videos_dict.get(perf['video_id'])
                
                if not song_master or not utaite_master or not video_master:
                    logger.warning(f"마스터 데이터 누락: song={bool(song_master)}, utaite={bool(utaite_master)}, video={bool(video_master)}")
                    continue
                
                # 아티스트 정보 조회 (기존 구조에서)
                artist_name = song_master.get('artist', {}).get('original', '')
                if not artist_name:
                    logger.warning(f"아티스트 정보 누락: {song_master}")
                    continue
                
                # PostgreSQL에 데이터 생성/조회
                artist_id = self.get_or_create_artist(artist_name)
                
                song_db_id = self.get_or_create_song_master(
                    title=song_master.get('titles', {}).get('original', ''),
                    artist_name=artist_name,
                    tags=song_master.get('tags', []),
                    album_art_url=song_master.get('album_art_url')
                )
                
                utaite_db_id = self.get_or_create_utaite(
                    utaite_master.get('names', {}).get('original', '')
                )
                
                video_db_id = self.get_or_create_video(
                    video_id=perf['video_id'],
                    title=video_master.get('title', ''),
                    channel=video_master.get('channel', ''),
                    thumbnail_url=video_master.get('thumbnail_url', '')
                )
                
                # 날짜 파싱
                if isinstance(perf['date'], str):
                    try:
                        date = datetime.fromisoformat(perf['date'].replace('Z', '+00:00'))
                    except ValueError:
                        date = datetime.fromisoformat(perf['date'])
                else:
                    date = perf['date']
                
                # 기존 공연 기록 확인 (중복 방지)
                existing_performance = self.db.query(Performance).filter(
                    Performance.song_master_id == song_db_id,
                    Performance.utaite_id == utaite_db_id,
                    Performance.video_id == video_db_id,
                    Performance.start_time == perf['start_time']
                ).first()
                
                if existing_performance:
                    continue  # 이미 존재하는 기록
                
                # 새 공연 기록 생성
                new_performance = Performance(
                    song_master_id=song_db_id,
                    utaite_id=utaite_db_id,
                    video_id=video_db_id,
                    start_time=perf['start_time'],
                    date=date
                )
                
                self.db.add(new_performance)
                migrated_count += 1
                
                # 배치 커밋 (성능 향상)
                if migrated_count % 100 == 0:
                    self.db.commit()
                    logger.info(f"진행상황: {migrated_count}개 마이그레이션 완료")
                    
            except Exception as e:
                logger.error(f"항목 마이그레이션 실패: {perf}, 오류: {e}")
                continue
        
        # 최종 커밋
        self.db.commit()
        logger.info(f"공연 데이터 마이그레이션 완료: 총 {migrated_count}개 항목")
    
    def close(self):
        """데이터베이스 연결 종료"""
        self.db.close()

def main():
    """메인 마이그레이션 함수"""
    logger.info("PostgreSQL 마이그레이션 시작")
    
    # 성과 데이터 파일 경로
    performances_file = "data/songs.json"
    
    if not os.path.exists(performances_file):
        logger.error("마이그레이션할 performances 파일이 없습니다.")
        return
    
    migrator = PostgreSQLMigrator()
    
    try:
        # 성과 데이터 로드 및 마이그레이션
        logger.info(f"파일 처리 중: {performances_file}")
        performances_data = migrator.load_json_data(performances_file)
        
        if performances_data:
            migrator.migrate_performance_data(performances_data)
        
        logger.info("🎉 모든 마이그레이션이 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"마이그레이션 중 오류 발생: {e}")
        migrator.db.rollback()
    finally:
        migrator.close()

if __name__ == "__main__":
    main()