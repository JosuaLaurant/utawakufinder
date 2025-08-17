# 🔍 Utawakufinder 디버깅 가이드

## 📋 로그 확인 방법

### 1. Docker Compose 로그 실시간 확인
```bash
# 모든 서비스 로그 확인
docker compose logs -f

# 백엔드만 확인
docker compose logs -f backend

# 프론트엔드만 확인
docker compose logs -f frontend

# 최근 100줄만 확인
docker compose logs --tail=100 -f
```

### 2. 개별 컨테이너 로그 확인
```bash
# 컨테이너 목록 확인
docker compose ps

# 백엔드 로그
docker logs utawakufinder-backend-1 -f

# 프론트엔드 로그
docker logs utawakufinder-frontend-1 -f
```

## 🔧 백엔드 디버깅

### API 요청 추적
백엔드에 다음과 같은 상세 로그가 추가되어 있습니다:

```
2025-08-17 02:13:39,020 - main - INFO - 비디오 파싱 시작: URL=https://www.youtube.com/watch?v=bNs6T9RL2zI
2025-08-17 02:13:39,020 - main - INFO - 1단계: 비디오 ID 추출 중...
2025-08-17 02:13:39,020 - main - INFO - 비디오 ID 추출 성공: bNs6T9RL2zI
2025-08-17 02:13:39,021 - main - INFO - 2단계: 비디오 정보 가져오는 중...
2025-08-17 02:13:39,207 - main - INFO - 비디오 정보 가져오기 성공: 【#歌枠】初見さんコメントで필ず1曲歌唱🎶...
2025-08-17 02:13:39,207 - main - INFO - 3단계: 댓글 가져오는 중...
2025-08-17 02:13:39,474 - main - INFO - 댓글 가져오기 성공: 5개 댓글
2025-08-17 02:13:39,474 - main - INFO - 4단계: 댓글 저장 중...
2025-08-17 02:13:39,477 - main - INFO - 댓글 저장 완료
2025-08-17 02:13:39,477 - main - INFO - 5단계: 타임스탬프 파싱 중...
2025-08-17 02:13:39,478 - main - INFO - 타임스탬프 파싱 성공: 9곡
2025-08-17 02:13:39,478 - main - INFO - 6단계: Song 객체 변환 중...
2025-08-17 02:13:39,478 - main - INFO - Song 객체 변환 완료
2025-08-17 02:13:39,478 - main - INFO - 비디오 파싱 완료: 9곡 추출됨
2025-08-17 02:13:39,479 - main - INFO - 요청 완료: POST http://localhost:9050/parse-video - 상태코드: 200 - 처리시간: 0.46초
```

### 수동 API 테스트
```bash
# 기본 헬스체크
curl http://localhost:9050/

# 비디오 목록 조회
curl http://localhost:9050/videos

# 유튜브 URL 파싱 테스트
curl -X POST "http://localhost:9050/parse-video" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=bNs6T9RL2zI"}'
```

## 🌐 프론트엔드 디버깅

### 브라우저 개발자 도구 사용
1. **브라우저에서 F12 누르기**
2. **Console 탭에서 로그 확인**

프론트엔드에 다음과 같은 상세 로그가 추가되어 있습니다:

```javascript
🎬 비디오 목록 가져오기 시작
백엔드 URL: http://localhost:9050
📡 요청 URL: http://localhost:9050/videos
📨 응답 상태: 200 OK
📋 받은 데이터: []
📊 비디오 개수: 0
✅ 비디오 목록 설정 완료
```

### URL 등록 시 로그
```javascript
🚀 URL 등록 시작: https://www.youtube.com/watch?v=bNs6T9RL2zI
📡 요청 URL: http://localhost:9050/parse-video
📤 요청 데이터: {url: "https://www.youtube.com/watch?v=bNs6T9RL2zI"}
📨 응답 상태: 200 OK
📋 파싱 결과: {video_info: {...}, songs: [...]}
🎵 추출된 곡 수: 9
✅ 모달 표시 완료
```

## 🔍 일반적인 문제 해결

### 1. 포트 충돌 문제
```bash
# 포트 사용 확인
sudo netstat -tlnp | grep :9050
sudo netstat -tlnp | grep :3030

# 프로세스 종료
sudo kill -9 <PID>
```

### 2. Docker 네트워크 문제
```bash
# 컨테이너 재시작
docker compose restart

# 완전 재빌드
docker compose down
docker compose up --build
```

### 3. 환경 변수 확인
```bash
# 프론트엔드 컨테이너에서 환경변수 확인
docker exec utawakufinder-frontend-1 env | grep BACKEND
```

### 4. 백엔드 연결 테스트
```bash
# 백엔드 컨테이너에서 내부 테스트
docker exec utawakufinder-backend-1 curl http://localhost:9050/

# 프론트엔드에서 백엔드 연결 테스트
docker exec utawakufinder-frontend-1 curl http://backend:9050/
```

## 📊 현재 상태 확인

### 정상 작동 시 예상 출력
```bash
# 컨테이너 상태
$ docker compose ps
NAME                       IMAGE                    COMMAND                  SERVICE    CREATED         STATUS         PORTS
utawakufinder-backend-1    utawakufinder-backend    "uvicorn main:app --…"   backend    5 seconds ago   Up 5 seconds   0.0.0.0:9050->9050/tcp
utawakufinder-frontend-1   utawakufinder-frontend   "docker-entrypoint.s…"   frontend   5 seconds ago   Up 5 seconds   0.0.0.0:3030->3030/tcp

# API 테스트
$ curl http://localhost:9050/
{"message":"Utawakufinder API","version":"1.0.0"}

# 프론트엔드 접속
$ curl -I http://localhost:3030/
HTTP/1.1 200 OK
```

## 🎯 성공적인 파싱 예시
유튜브 URL: `https://www.youtube.com/watch?v=bNs6T9RL2zI`
- ✅ 비디오 ID 추출: `bNs6T9RL2zI`
- ✅ 비디오 정보: 일본어 제목 및 채널명
- ✅ 댓글 가져오기: 5개 댓글
- ✅ 타임스탬프 파싱: **9곡 성공**

## 📞 추가 도움
문제가 지속되면 다음 정보를 함께 제공해주세요:
1. `docker compose logs` 전체 출력
2. 브라우저 개발자 도구 Console 로그
3. 사용한 유튜브 URL
4. 오류 발생 단계