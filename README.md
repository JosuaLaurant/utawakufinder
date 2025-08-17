# Utawakufinder

유튜브 노래방송의 URL을 이용해 각 노래별 타임스탬프를 파싱하고, 정규화된 데이터베이스 구조로 관리하는 웹 서비스입니다. 우타이테별, 아티스트별, 곡별 상세 통계와 다국어 검색 기능을 제공합니다.

## 🚀 주요 기능

### 🎵 노래목록 (메인)
- 유튜브와 비슷한 디자인의 인터페이스
- 등록된 부른 기록들을 카드 형태로 표시
- 각 카드에 썸네일, 제목, 우타이테, 아티스트, 시작시간 표시
- 직접 유튜브 링크로 이동하는 플레이 버튼

### 📚 악곡 정보
- 곡 마스터 기반의 상세 정보 페이지
- 부른 횟수, 최근 부른 날짜 등 통계 정보
- 각 곡별 부른 기록 히스토리 제공
- 정렬 기능: 부른 횟수, 최근 날짜, 가나다순

### 🎤 우타이테 관리
- 정규화된 우타이테 마스터 데이터
- 우타이테별 통계: 총 부른 곡 수, 고유 곡 수, 아티스트 수
- 다국어 이름 지원 (원어/한글/영어/로마자)

### 🎼 아티스트 정보
- 아티스트별 곡 목록과 통계
- 원곡 아티스트 기반의 정규화된 데이터

### 🎯 스마트 사이드바
- 우타이테별 필터링 (곡 수 표시)
- 곡 수 기준 정렬
- 확장된 폭으로 가독성 향상

### 🔍 다국어 검색
- 곡 제목, 아티스트명, 우타이테명으로 통합 검색
- 원어/한글/영어/로마자 모든 언어에서 검색 가능
- 실시간 검색 결과 표시

### 📝 영상 등록
- 유튜브 URL 입력으로 영상 등록
- 댓글에서 타임스탬프 자동 추출 (다양한 형식 지원)
- 추출 형식: `시간 | 노래제목 | 가수` 외 다수
- 영상 정보 자동 수집 및 우타이테 자동 추출

## 🛠️ 기술 스택

- **프론트엔드**: Next.js 14 + TypeScript + TailwindCSS
- **백엔드**: FastAPI + Python (정규화된 아키텍처)
- **데이터 저장**: 정규화된 JSON 파일 (PostgreSQL 이관 준비)
- **외부 API**: YouTube Data API v3
- **컨테이너**: Docker + Docker Compose
- **아키텍처**: 마이크로서비스, 정규화된 데이터 모델

## 실행 방법

### Docker로 실행 (권장)

```bash
# 전체 서비스 실행
docker compose up --build

# 백그라운드 실행
docker compose up -d --build

# 서비스 중지
docker compose down
```

### 개발 환경에서 실행

#### 백엔드 실행
```bash
cd backend

# 의존성 설치
pip install -r requirements.txt

# 서버 실행 (포트 9030)
uvicorn main:app --reload --port 9030
```

#### 프론트엔드 실행
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행 (포트 3030)
npm run dev
```

## 접속 주소

- **웹 사이트**: http://localhost:3030
- **API 서버**: http://localhost:9030
- **API 문서**: http://localhost:9030/docs

## 📊 정규화된 데이터 구조

### 우타이테 마스터 (`utaites_master.json`)
```json
{
  "id": "utaite_xxxxx",
  "names": {
    "original": "憂涙といろ",
    "korean": "우루이토이로",
    "english": "Urui Toiro",
    "romanized": "urui_toiro"
  },
  "performance_count": 15,
  "first_appearance": "2025-01-01",
  "latest_appearance": "2025-08-17"
}
```

### 아티스트 마스터 (`artists_master.json`)
```json
{
  "id": "artist_xxxxx",
  "names": {
    "original": "ランカ・リー",
    "korean": "란카 리",
    "english": "Ranka Lee"
  },
  "song_count": 5
}
```

### 곡 마스터 (`songs_master.json`)
```json
{
  "id": "song_xxxxx",
  "titles": {
    "original": "ホシキラ",
    "korean": "호시키라",
    "english": "Hoshikira"
  },
  "artist_id": "artist_xxxxx",
  "performance_count": 3,
  "tags": ["anime", "ballad"]
}
```

### 부른 기록 (`songs.json`)
```json
{
  "id": "performance_xxxxx",
  "song_master_id": "song_xxxxx",
  "utaite_id": "utaite_xxxxx",
  "video_id": "YouTube_video_id",
  "start_time": "0:28:42",
  "date": "2025-08-17T02:26:41"
}
```

## 📁 프로젝트 구조

```
utawakufinder/
├── backend/              # FastAPI 백엔드 서버
│   ├── main.py          # FastAPI 메인 애플리케이션
│   ├── models.py        # SQLAlchemy 데이터 모델
│   ├── schemas.py       # Pydantic 스키마
│   ├── database.py      # 데이터베이스 연결
│   ├── crawler.py       # YouTube 크롤링
│   ├── data_manager.py  # 데이터 관리 유틸리티
│   └── Dockerfile       # 백엔드 Docker 설정
├── frontend/            # Next.js 프론트엔드
│   ├── app/            # App Router 페이지
│   │   ├── songs/      # 악곡 정보 페이지
│   │   ├── artists/    # 아티스트 페이지
│   │   ├── utaites/    # 우타이테 페이지
│   │   └── search/     # 검색 페이지
│   ├── components/     # 재사용 컴포넌트
│   └── types/         # TypeScript 타입 정의
├── scripts/            # 마이그레이션 및 유틸리티
│   ├── init.sql       # PostgreSQL 스키마
│   ├── migrate_to_postgres.py # DB 마이그레이션
│   └── run_migration.py # 마이그레이션 실행
├── data/               # 정규화된 JSON 데이터
│   ├── utaites_master.json # 우타이테 마스터
│   ├── songs_master.json   # 곡 마스터
│   └── songs.json         # 부른 기록
├── docs/               # 프로젝트 문서
├── docker-compose.yml  # Docker 설정
├── .env.example       # 환경변수 템플릿
└── README.md          # 프로젝트 설명
```

## 🔄 주요 변경사항 (v2.0)

### 데이터베이스 정규화
- 우타이테, 아티스트, 곡 마스터 분리
- 다국어 지원을 위한 names/titles 구조
- PostgreSQL 이관 준비된 스키마

### UI/UX 개선
- "영상목록" → "악곡 정보" 페이지로 변경
- 사이드바 폭 확대 및 곡 수 표시
- 곡별 상세 통계 및 히스토리 제공

### API 엔드포인트 확장
- `/utaites` - 우타이테 통계
- `/songs/master` - 곡 마스터 정보
- `/search` - 다국어 검색
- 기존 호환성 유지

### 성능 최적화
- 정규화로 중복 데이터 제거
- 효율적인 조인 연산
- 확장 가능한 아키텍처

