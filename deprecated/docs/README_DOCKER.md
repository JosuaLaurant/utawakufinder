# Utawakufinder - Docker 실행 가이드

## 실행 방법

### 1. Docker Compose로 전체 서비스 실행

```bash
# 모든 서비스 실행 (백엔드 9030포트, 프론트엔드 3030포트)
docker-compose up --build

# 백그라운드에서 실행
docker-compose up -d --build

# 서비스 중지
docker-compose down
```

### 2. 개별 서비스 실행

#### 백엔드만 실행
```bash
docker-compose up backend --build
```

#### 프론트엔드만 실행 (백엔드가 실행 중일 때)
```bash
docker-compose up frontend --build
```

## 접속 주소

- **프론트엔드**: http://localhost:3030
- **백엔드 API**: http://localhost:9030
- **API 문서**: http://localhost:9030/docs

## 주요 기능

1. **메인 화면**: 등록된 노래방송 영상들을 유튜브 스타일로 표시
2. **등록 화면**: 유튜브 URL 입력 후 타임스탬프 자동 추출 및 확인
3. **사이드바 필터**: 부른 사람별로 영상 필터링
4. **검색 기능**: 제목, 가수, 부른 사람, 노래명으로 검색

## 데이터 저장

- 영상 데이터는 `./data/videos.json`에 저장됩니다
- 댓글 데이터는 `./test/` 디렉토리에 저장됩니다

## 문제 해결

### 포트 충돌 시
```bash
# 다른 포트로 변경하려면 docker-compose.yml 수정
# 예: 3030 → 3031, 9030 → 9031
```

### 권한 문제 시
```bash
# 데이터 디렉토리 권한 수정
sudo chown -R $USER:$USER ./data
```

### 컨테이너 재시작
```bash
# 특정 서비스 재시작
docker-compose restart backend
docker-compose restart frontend

# 전체 재시작
docker-compose restart
```