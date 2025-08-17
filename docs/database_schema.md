# Database Schema Design

## Tables

### 1. utaites (우타이테 마스터)
```sql
CREATE TABLE utaites (
    id VARCHAR(50) PRIMARY KEY,
    name_original VARCHAR(255) NOT NULL,
    name_korean VARCHAR(255),
    name_english VARCHAR(255),
    name_romanized VARCHAR(255),
    performance_count INTEGER DEFAULT 0,
    first_appearance TIMESTAMP,
    latest_appearance TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. artists (아티스트 마스터)
```sql
CREATE TABLE artists (
    id VARCHAR(50) PRIMARY KEY,
    name_original VARCHAR(255) NOT NULL,
    name_korean VARCHAR(255),
    name_english VARCHAR(255),
    name_romanized VARCHAR(255),
    song_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3. songs_master (곡 마스터)
```sql
CREATE TABLE songs_master (
    id VARCHAR(50) PRIMARY KEY,
    title_original VARCHAR(255) NOT NULL,
    title_korean VARCHAR(255),
    title_english VARCHAR(255),
    title_romanized VARCHAR(255),
    artist_id VARCHAR(50) REFERENCES artists(id),
    tags TEXT[], -- PostgreSQL array
    performance_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4. videos (비디오 마스터)
```sql
CREATE TABLE videos (
    id VARCHAR(50) PRIMARY KEY, -- YouTube video ID
    title VARCHAR(500) NOT NULL,
    channel VARCHAR(255),
    thumbnail_url VARCHAR(500),
    duration INTEGER, -- seconds
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 5. performances (부른 기록)
```sql
CREATE TABLE performances (
    id VARCHAR(50) PRIMARY KEY,
    song_master_id VARCHAR(50) REFERENCES songs_master(id),
    utaite_id VARCHAR(50) REFERENCES utaites(id),
    video_id VARCHAR(50) REFERENCES videos(id),
    start_time VARCHAR(20) NOT NULL, -- "0:28:42" format
    start_time_seconds INTEGER, -- for sorting/filtering
    date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Indexes
```sql
CREATE INDEX idx_performances_song_master ON performances(song_master_id);
CREATE INDEX idx_performances_utaite ON performances(utaite_id);
CREATE INDEX idx_performances_video ON performances(video_id);
CREATE INDEX idx_performances_date ON performances(date);
CREATE INDEX idx_songs_master_artist ON songs_master(artist_id);
```

## Migration Benefits
1. **정규화**: 중복 데이터 제거
2. **외래키**: 데이터 무결성 보장
3. **인덱스**: 빠른 검색/조인
4. **확장성**: 새로운 필드 추가 용이
5. **다국어 검색**: 모든 언어 필드에서 검색 가능