#!/usr/bin/env python3
"""
데이터 마이그레이션 스크립트
기존 JSON 구조를 새로운 정규화된 구조로 변환
"""
import json
import os
import shutil
from datetime import datetime
from collections import defaultdict
# 간단한 함수들만 포함
import hashlib

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
    hash_part = hashlib.md5(source.encode('utf-8')).hexdigest()[:12]
    return f"{prefix}_{hash_part}"

def backup_data():
    """기존 데이터 백업"""
    print("🔄 기존 데이터 백업 중...")
    backup_dir = f"data/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "data/songs.json",
        "data/songs_master.json", 
        "data/utaites_master.json"
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_dir)
            print(f"✅ {file_path} 백업 완료")
    
    return backup_dir

def load_old_data():
    """기존 데이터 로드"""
    print("📂 기존 데이터 로드 중...")
    
    # 기존 songs.json (부른 기록)
    with open("data/songs.json", "r", encoding="utf-8") as f:
        old_songs = json.load(f)
    
    # 기존 songs_master.json 
    with open("data/songs_master.json", "r", encoding="utf-8") as f:
        old_songs_master = json.load(f)
    
    # 기존 utaites_master.json
    utaites_master = []
    if os.path.exists("data/utaites_master.json"):
        with open("data/utaites_master.json", "r", encoding="utf-8") as f:
            utaites_master = json.load(f)
    
    print(f"📊 로드된 데이터:")
    print(f"  - 부른 기록: {len(old_songs)}곡")
    print(f"  - 곡 마스터: {len(old_songs_master)}곡")
    print(f"  - 우타이테: {len(utaites_master)}명")
    
    return old_songs, old_songs_master, utaites_master

def extract_unique_data(old_songs, old_songs_master):
    """고유 데이터 추출"""
    print("🔍 고유 데이터 추출 중...")
    
    # 우타이테 추출
    utaites = {}
    for song in old_songs:
        singer = song.get("singer", "미상")
        if singer and singer != "미상":
            utaite_id = generate_id("utaite", singer)
            utaites[utaite_id] = {
                "id": utaite_id,
                "names": {
                    "original": singer,
                    "korean": "",
                    "english": "",
                    "romanized": ""
                },
                "performance_count": 0,
                "first_appearance": None,
                "latest_appearance": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
    
    # 아티스트 추출 (songs_master에서)
    artists = {}
    for song in old_songs_master:
        artist_name = song.get("artist", {}).get("original", "미상")
        if artist_name and artist_name != "미상":
            artist_id = generate_id("artist", artist_name)
            artists[artist_id] = {
                "id": artist_id,
                "names": {
                    "original": artist_name,
                    "korean": "",
                    "english": "",
                    "romanized": ""
                },
                "song_count": 0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
    
    # 비디오 추출
    videos = {}
    for song in old_songs:
        video_id = song.get("video_id")
        if video_id and video_id not in videos:
            videos[video_id] = {
                "id": video_id,
                "title": song.get("video_title", ""),
                "channel": song.get("video_channel", ""),
                "thumbnail_url": song.get("thumbnail", f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"),
                "duration": None,
                "published_at": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
    
    print(f"📈 추출된 고유 데이터:")
    print(f"  - 우타이테: {len(utaites)}명")
    print(f"  - 아티스트: {len(artists)}명")
    print(f"  - 비디오: {len(videos)}개")
    
    return list(utaites.values()), list(artists.values()), list(videos.values())

def migrate_songs_master(old_songs_master, artists):
    """곡 마스터 마이그레이션"""
    print("🎵 곡 마스터 마이그레이션 중...")
    
    # 아티스트 이름으로 ID 찾기 위한 매핑
    artist_name_to_id = {}
    for artist in artists:
        artist_name_to_id[artist["names"]["original"]] = artist["id"]
    
    new_songs_master = []
    for song in old_songs_master:
        artist_name = song.get("artist", {}).get("original", "미상")
        artist_id = artist_name_to_id.get(artist_name)
        
        new_song = {
            "id": song["id"],
            "titles": song.get("titles", {"original": "미상"}),
            "artist": song.get("artist", {"original": "미상"}),  # 기존 구조 유지
            "artist_id": artist_id,  # 새로운 참조 추가
            "tags": song.get("tags", []),
            "performance_count": song.get("performance_count", 0),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        new_songs_master.append(new_song)
    
    print(f"✅ {len(new_songs_master)}곡 마이그레이션 완료")
    return new_songs_master

def migrate_performances(old_songs, utaites, songs_master):
    """부른 기록 마이그레이션"""
    print("🎤 부른 기록 마이그레이션 중...")
    
    # 우타이테 이름으로 ID 찾기 위한 매핑
    utaite_name_to_id = {}
    for utaite in utaites:
        utaite_name_to_id[utaite["names"]["original"]] = utaite["id"]
    
    # 곡 ID 존재 여부 확인을 위한 세트
    song_ids = {song["id"] for song in songs_master}
    
    new_performances = []
    for song in old_songs:
        singer = song.get("singer", "미상")
        utaite_id = utaite_name_to_id.get(singer, "unknown")
        
        # song_master_id 검증
        song_master_id = song.get("song_master_id")
        if song_master_id not in song_ids:
            print(f"⚠️  존재하지 않는 song_master_id: {song_master_id}")
            continue
        
        new_performance = {
            "id": song["id"],
            "song_master_id": song_master_id,
            "utaite_id": utaite_id,
            "video_id": song["video_id"],
            "start_time": song["start_time"],
            "start_time_seconds": time_to_seconds(song["start_time"]),
            "date": song["date"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        new_performances.append(new_performance)
    
    print(f"✅ {len(new_performances)}개 부른 기록 마이그레이션 완료")
    return new_performances

def update_statistics(utaites, artists, songs_master, performances):
    """통계 정보 업데이트"""
    print("📊 통계 정보 업데이트 중...")
    
    # 우타이테별 부른 횟수 및 날짜
    utaite_stats = defaultdict(lambda: {"count": 0, "dates": []})
    for perf in performances:
        utaite_id = perf["utaite_id"]
        utaite_stats[utaite_id]["count"] += 1
        utaite_stats[utaite_id]["dates"].append(perf["date"])
    
    for utaite in utaites:
        stats = utaite_stats[utaite["id"]]
        utaite["performance_count"] = stats["count"]
        if stats["dates"]:
            sorted_dates = sorted(stats["dates"])
            utaite["first_appearance"] = sorted_dates[0]
            utaite["latest_appearance"] = sorted_dates[-1]
    
    # 곡별 부른 횟수
    song_counts = defaultdict(int)
    for perf in performances:
        song_counts[perf["song_master_id"]] += 1
    
    for song in songs_master:
        song["performance_count"] = song_counts[song["id"]]
    
    # 아티스트별 곡 수
    artist_counts = defaultdict(int)
    for song in songs_master:
        if song.get("artist_id"):
            artist_counts[song["artist_id"]] += 1
    
    for artist in artists:
        artist["song_count"] = artist_counts[artist["id"]]
    
    print("✅ 통계 정보 업데이트 완료")

def save_migrated_data(utaites, artists, songs_master, videos, performances):
    """마이그레이션된 데이터 저장"""
    print("💾 마이그레이션된 데이터 저장 중...")
    
    # 우타이테 마스터
    with open("data/utaites_master.json", "w", encoding="utf-8") as f:
        json.dump(utaites, f, ensure_ascii=False, indent=2)
    print(f"✅ 우타이테 마스터 저장: {len(utaites)}명")
    
    # 아티스트 마스터
    with open("data/artists_master.json", "w", encoding="utf-8") as f:
        json.dump(artists, f, ensure_ascii=False, indent=2)
    print(f"✅ 아티스트 마스터 저장: {len(artists)}명")
    
    # 곡 마스터 (새 구조로 덮어쓰기)
    with open("data/songs_master.json", "w", encoding="utf-8") as f:
        json.dump(songs_master, f, ensure_ascii=False, indent=2)
    print(f"✅ 곡 마스터 저장: {len(songs_master)}곡")
    
    # 비디오 마스터
    with open("data/videos_master.json", "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"✅ 비디오 마스터 저장: {len(videos)}개")
    
    # 부른 기록 (새 구조로 덮어쓰기)
    with open("data/songs.json", "w", encoding="utf-8") as f:
        json.dump(performances, f, ensure_ascii=False, indent=2)
    print(f"✅ 부른 기록 저장: {len(performances)}개")

def main():
    """메인 마이그레이션 실행"""
    print("🚀 데이터 마이그레이션 시작")
    print("=" * 50)
    
    # 1. 백업 (스킵)
    print("⚠️  백업 단계 스킵 (권한 문제)")
    print("-" * 50)
    
    # 2. 기존 데이터 로드
    old_songs, old_songs_master, existing_utaites = load_old_data()
    print("-" * 50)
    
    # 3. 고유 데이터 추출
    utaites, artists, videos = extract_unique_data(old_songs, old_songs_master)
    
    # 기존 우타이테 정보 병합
    if existing_utaites:
        existing_utaite_names = {u["names"]["original"] for u in existing_utaites}
        new_utaites = [u for u in utaites if u["names"]["original"] not in existing_utaite_names]
        utaites = existing_utaites + new_utaites
        print(f"🔄 기존 우타이테 {len(existing_utaites)}명과 새 우타이테 {len(new_utaites)}명 병합")
    
    print("-" * 50)
    
    # 4. 곡 마스터 마이그레이션
    songs_master = migrate_songs_master(old_songs_master, artists)
    print("-" * 50)
    
    # 5. 부른 기록 마이그레이션
    performances = migrate_performances(old_songs, utaites, songs_master)
    print("-" * 50)
    
    # 6. 통계 업데이트
    update_statistics(utaites, artists, songs_master, performances)
    print("-" * 50)
    
    # 7. 저장
    save_migrated_data(utaites, artists, songs_master, videos, performances)
    print("-" * 50)
    
    print("🎉 마이그레이션 완료!")
    print(f"📈 최종 결과:")
    print(f"  - 우타이테: {len(utaites)}명")
    print(f"  - 아티스트: {len(artists)}명") 
    print(f"  - 곡 마스터: {len(songs_master)}곡")
    print(f"  - 비디오: {len(videos)}개")
    print(f"  - 부른 기록: {len(performances)}개")
    print("✅ 마이그레이션 완료")

if __name__ == "__main__":
    main()