-- Utawakufinder PostgreSQL Schema
-- 정수 ID 사용으로 최적화된 스키마

-- 아티스트 테이블
CREATE TABLE artists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    name_korean VARCHAR(255),
    name_english VARCHAR(255), 
    name_romanized VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 우타이테 테이블  
CREATE TABLE utaites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    name_korean VARCHAR(255),
    name_english VARCHAR(255),
    name_romanized VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 곡 마스터 테이블
CREATE TABLE song_masters (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    title_korean VARCHAR(500),
    title_english VARCHAR(500),
    title_romanized VARCHAR(500),
    artist_id INTEGER NOT NULL REFERENCES artists(id),
    album_art_url TEXT,
    tags TEXT[], -- PostgreSQL 배열 타입 사용
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 비디오 테이블
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) NOT NULL UNIQUE, -- YouTube 비디오 ID
    title TEXT NOT NULL,
    channel VARCHAR(255),
    thumbnail_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 공연 기록 테이블
CREATE TABLE performances (
    id SERIAL PRIMARY KEY,
    song_master_id INTEGER NOT NULL REFERENCES song_masters(id),
    utaite_id INTEGER NOT NULL REFERENCES utaites(id),
    video_id INTEGER NOT NULL REFERENCES videos(id),
    start_time VARCHAR(20) NOT NULL, -- "HH:MM:SS" 형식
    date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX idx_song_masters_artist_id ON song_masters(artist_id);
CREATE INDEX idx_performances_song_master_id ON performances(song_master_id);
CREATE INDEX idx_performances_utaite_id ON performances(utaite_id);
CREATE INDEX idx_performances_video_id ON performances(video_id);
CREATE INDEX idx_performances_date ON performances(date);
CREATE INDEX idx_videos_video_id ON videos(video_id);

-- 외래 키 제약 조건 추가
ALTER TABLE song_masters ADD CONSTRAINT fk_song_masters_artist 
    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE;

ALTER TABLE performances ADD CONSTRAINT fk_performances_song_master 
    FOREIGN KEY (song_master_id) REFERENCES song_masters(id) ON DELETE CASCADE;

ALTER TABLE performances ADD CONSTRAINT fk_performances_utaite 
    FOREIGN KEY (utaite_id) REFERENCES utaites(id) ON DELETE CASCADE;

ALTER TABLE performances ADD CONSTRAINT fk_performances_video 
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE;

-- 트리거 함수: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_artists_updated_at BEFORE UPDATE ON artists 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_utaites_updated_at BEFORE UPDATE ON utaites 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_song_masters_updated_at BEFORE UPDATE ON song_masters 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_performances_updated_at BEFORE UPDATE ON performances 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 뷰 생성: 성능 기록과 관련 정보를 조인한 뷰
CREATE VIEW performance_details AS
SELECT 
    p.id,
    p.start_time,
    p.date,
    sm.id as song_master_id,
    sm.title as song_title,
    sm.title_korean as song_title_korean,
    sm.title_english as song_title_english,
    sm.title_romanized as song_title_romanized,
    a.id as artist_id,
    a.name as artist_name,
    a.name_korean as artist_name_korean,
    a.name_english as artist_name_english,
    a.name_romanized as artist_name_romanized,
    u.id as utaite_id,
    u.name as utaite_name,
    u.name_korean as utaite_name_korean,
    u.name_english as utaite_name_english,
    u.name_romanized as utaite_name_romanized,
    v.id as video_table_id,
    v.video_id,
    v.title as video_title,
    v.channel as video_channel,
    v.thumbnail_url,
    sm.album_art_url,
    sm.tags
FROM performances p
JOIN song_masters sm ON p.song_master_id = sm.id
JOIN artists a ON sm.artist_id = a.id
JOIN utaites u ON p.utaite_id = u.id
JOIN videos v ON p.video_id = v.id;

-- 아티스트 통계 뷰
CREATE VIEW artist_stats AS
SELECT 
    a.id,
    a.name,
    a.name_korean,
    a.name_english,
    a.name_romanized,
    COUNT(DISTINCT sm.id) as song_count,
    COUNT(p.id) as total_performances,
    MIN(p.date) as first_performance_date,
    MAX(p.date) as latest_performance_date
FROM artists a
LEFT JOIN song_masters sm ON a.id = sm.artist_id
LEFT JOIN performances p ON sm.id = p.song_master_id
GROUP BY a.id, a.name, a.name_korean, a.name_english, a.name_romanized;

-- 우타이테 통계 뷰
CREATE VIEW utaite_stats AS
SELECT 
    u.id,
    u.name,
    u.name_korean,
    u.name_english,
    u.name_romanized,
    COUNT(p.id) as total_performances,
    COUNT(DISTINCT p.song_master_id) as unique_songs,
    COUNT(DISTINCT sm.artist_id) as unique_artists,
    MIN(p.date) as first_performance_date,
    MAX(p.date) as latest_performance_date
FROM utaites u
LEFT JOIN performances p ON u.id = p.utaite_id
LEFT JOIN song_masters sm ON p.song_master_id = sm.id
GROUP BY u.id, u.name, u.name_korean, u.name_english, u.name_romanized;

-- 곡 통계 뷰
CREATE VIEW song_stats AS
SELECT 
    sm.id,
    sm.title,
    sm.title_korean,
    sm.title_english,
    sm.title_romanized,
    sm.artist_id,
    a.name as artist_name,
    sm.album_art_url,
    sm.tags,
    COUNT(p.id) as performance_count,
    MIN(p.date) as first_performance_date,
    MAX(p.date) as latest_performance_date
FROM song_masters sm
LEFT JOIN performances p ON sm.id = p.song_master_id
LEFT JOIN artists a ON sm.artist_id = a.id
GROUP BY sm.id, sm.title, sm.title_korean, sm.title_english, sm.title_romanized, 
         sm.artist_id, a.name, sm.album_art_url, sm.tags;