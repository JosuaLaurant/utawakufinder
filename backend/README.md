# Backend

Utawakufinder의 백엔드 API 서버입니다.

## 구조

```
backend/
├── main.py              # FastAPI 메인 애플리케이션
├── models.py            # SQLAlchemy 데이터베이스 모델
├── schemas.py           # Pydantic 스키마
├── database.py          # 데이터베이스 연결 설정
├── crawler.py           # YouTube 데이터 크롤링
├── data_manager.py      # 데이터 관리 유틸리티
├── requirements.txt     # Python 의존성
└── Dockerfile          # Docker 빌드 파일
```

## 실행 방법

### 로컬 개발
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 9030
```

### Docker
```bash
# 루트 디렉토리에서
docker-compose up backend
```

## 환경 변수

`.env` 파일에 다음 변수들을 설정해야 합니다:

```
YOUTUBE_API_KEY=your_youtube_api_key_here
DATABASE_URL=postgresql://utawaku:utawakupass123@localhost:5433/utawakufinder
```

## API 엔드포인트

- `GET /`: 서버 상태 확인
- `POST /parse-video`: YouTube 영상 파싱
- `GET /songs`: 곡 목록 조회
- `GET /artists`: 아티스트 목록 조회
- `GET /utaites`: 우타이테 목록 조회