# Deprecated Files

이 폴더는 리팩토링 과정에서 더 이상 사용되지 않는 파일들을 보관합니다.

## 📁 폴더 구조

### `frontend/`
- `contexts/` - 제거된 PlayerContext (YouTube API 사용 방식 변경으로 인해)
- `GlobalPlayer.tsx` - 글로벌 YouTube 플레이어 (임베드 방식으로 변경)
- `error-suppression.js` - 콘솔 에러 억제 스크립트 (더 이상 필요 없음)
- `pages/` - 빈 pages 디렉토리
- `test-player/` - 테스트용 플레이어 페이지

### `data/`
- `songs_backup.json` - 리팩토링 이전 songs.json 백업
- `videos.json.backup` - 이전 videos.json 백업

### `docs/`
- `database_schema.md` - PostgreSQL 스키마 설계 문서
- `DEBUG_GUIDE.md` - 디버깅 가이드
- `README_DOCKER.md` - Docker 사용법

### Root Files
- `main_old.py` - 이전 버전의 FastAPI 애플리케이션
- `create_utaites_master.py` - 일회성 마이그레이션 스크립트

## 🔄 리팩토링 내용

### 1. 데이터 구조 정규화
- 우타이테, 아티스트, 곡 마스터 분리
- PostgreSQL 이관 준비된 구조
- 다국어 지원 추가

### 2. 프론트엔드 아키텍처 변경
- YouTube Player API → 직접 링크 방식
- 글로벌 상태 관리 제거
- 컴포넌트 단순화

### 3. API 구조 개선
- 새로운 정규화된 엔드포인트
- 기존 호환성 유지
- 다국어 검색 지원

## ⚠️ 주의사항

이 폴더의 파일들은 참고용으로만 보관되며, 실제 애플리케이션에서는 사용되지 않습니다.
필요시 git history를 통해 이전 버전을 확인할 수 있습니다.