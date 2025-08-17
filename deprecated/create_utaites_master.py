#!/usr/bin/env python3
"""
기존 songs.json에서 우타이테 마스터 파일 생성
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

def generate_utaite_id(name: str) -> str:
    """우타이테 ID 생성"""
    hash_part = hashlib.md5(name.encode('utf-8')).hexdigest()[:12]
    return f"utaite_{hash_part}"

def extract_utaites_from_songs():
    """songs.json에서 우타이테 정보 추출"""
    
    # 기존 데이터 로드
    with open('data/songs.json', 'r', encoding='utf-8') as f:
        songs = json.load(f)
    
    # 우타이테별 통계 계산
    utaite_stats = defaultdict(lambda: {
        'performances': [],
        'first_date': None,
        'latest_date': None
    })
    
    for song in songs:
        singer = song['singer']
        date = song['date']
        
        utaite_stats[singer]['performances'].append(song)
        
        if utaite_stats[singer]['first_date'] is None or date < utaite_stats[singer]['first_date']:
            utaite_stats[singer]['first_date'] = date
            
        if utaite_stats[singer]['latest_date'] is None or date > utaite_stats[singer]['latest_date']:
            utaite_stats[singer]['latest_date'] = date
    
    # 우타이테 마스터 생성
    utaites_master = []
    current_time = datetime.now().isoformat()
    
    for singer_name, stats in utaite_stats.items():
        utaite = {
            "id": generate_utaite_id(singer_name),
            "names": {
                "original": singer_name,
                "korean": "",  # 추후 수동/자동 번역
                "english": "",
                "romanized": ""
            },
            "performance_count": len(stats['performances']),
            "first_appearance": stats['first_date'],
            "latest_appearance": stats['latest_date'],
            "created_at": current_time,
            "updated_at": current_time
        }
        utaites_master.append(utaite)
    
    # 부른 횟수 순으로 정렬
    utaites_master.sort(key=lambda x: x['performance_count'], reverse=True)
    
    # 파일 저장
    with open('data/utaites_master.json', 'w', encoding='utf-8') as f:
        json.dump(utaites_master, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 우타이테 마스터 파일 생성 완료: {len(utaites_master)}명")
    
    # 상위 10명 출력
    print("\n상위 10명 우타이테:")
    for i, utaite in enumerate(utaites_master[:10], 1):
        print(f"{i:2d}. {utaite['names']['original']} ({utaite['performance_count']}곡)")
    
    return utaites_master

def update_songs_with_utaite_ids():
    """songs.json에 utaite_id 추가"""
    
    # 우타이테 마스터 로드
    with open('data/utaites_master.json', 'r', encoding='utf-8') as f:
        utaites = json.load(f)
    
    # 이름 -> ID 매핑 생성
    name_to_id = {utaite['names']['original']: utaite['id'] for utaite in utaites}
    
    # songs.json 업데이트
    with open('data/songs.json', 'r', encoding='utf-8') as f:
        songs = json.load(f)
    
    updated_songs = []
    for song in songs:
        singer_name = song['singer']
        utaite_id = name_to_id.get(singer_name)
        
        if utaite_id:
            song['utaite_id'] = utaite_id
        else:
            print(f"⚠️ 우타이테 ID를 찾을 수 없음: {singer_name}")
            
        updated_songs.append(song)
    
    # 백업 생성
    with open('data/songs_backup.json', 'w', encoding='utf-8') as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)
    
    # 업데이트된 파일 저장
    with open('data/songs.json', 'w', encoding='utf-8') as f:
        json.dump(updated_songs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ songs.json 업데이트 완료 (백업: songs_backup.json)")

if __name__ == "__main__":
    print("🎤 우타이테 마스터 파일 생성 중...")
    
    # 1. 우타이테 마스터 생성
    utaites_master = extract_utaites_from_songs()
    
    # 2. songs.json에 utaite_id 추가
    update_songs_with_utaite_ids()
    
    print("\n✨ 완료!")