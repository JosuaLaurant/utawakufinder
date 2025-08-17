# CLAUDE_KR.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소에서 작업할 때 참고할 수 있는 한국어 가이드입니다.

## 프로젝트 개요

Utawakufinder는 유튜브 노래방송의 댓글에서 각 노래별 타임스탬프를 추출하여 검색 가능한 인터페이스로 정리해주는 서비스입니다. 유튜브 영상 URL을 처리하여 댓글에서 노래 정보(제목, 가수, 타임스탬프)를 추출하고, 이를 유튜브와 유사한 인터페이스에서 필터링 기능과 함께 제공합니다.

## 기술 스택

- **백엔드**: FastAPI (Python)
- **프론트엔드**: Next.js + TailwindCSS (현재 저장소에는 미포함)
- **데이터 저장**: 노래 메타데이터를 위한 JSON 파일
- **외부 API**: YouTube Data API v3

## 개발 명령어

### FastAPI 서버 실행
```bash
# 의존성 설치
pip install -r test/requirements.txt

# FastAPI 개발 서버 실행
uvicorn main:app --reload
```

### 유튜브 데이터 추출 테스트
```bash
# 메인 크롤러 스크립트 실행
python crawler.py

# 채널 정보 추출 테스트
python crawler_channelInfo.py

# 간단한 테스트 스크립트
python test.py
```

## 코드 구조

### 핵심 컴포넌트

**crawler.py** - 메인 유튜브 데이터 추출 모듈:
- `extract_video_id()` - 유튜브 URL에서 영상 ID 추출
- `find_comment()` - 유튜브 API를 사용하여 페이지네이션으로 댓글 가져오기
- `save_comments()` - 댓글을 텍스트 파일로 저장
- `parse_song()` - 정규식 패턴 `(\d{1,2}:\d{2}:\d{2}).*?\|\s*(.*?)\s*\|\s*(.*)$`을 사용하여 댓글에서 타임스탬프 파싱
- `check_info()` - 영상 메타데이터(제목, 채널) 가져오기

**crawler_channelInfo.py** - 채널 정보 추출 (간단한 버전)

**main.py** - 기본 "Hello World" 엔드포인트가 있는 FastAPI 애플리케이션 진입점

### 데이터 흐름
1. 유튜브 URL 입력 → `extract_video_id()`
2. 영상 ID → `find_comment()` → 페이지네이션으로 모든 댓글 가져오기
3. 댓글 → `save_comments()` → `{video_id}.txt`로 저장
4. 텍스트 파일 → `parse_song()` → 구조화된 노래 데이터 추출
5. 노래 데이터 → 프론트엔드 사용을 위한 JSON 저장

### 댓글 파싱 형식
시스템은 다음 형식의 댓글을 예상합니다: `HH:MM:SS | 노래 제목 | 가수 이름`
- 제목과 가수 이름에서 괄호 안의 내용 제거
- 다중 페이지 댓글 가져오기 처리 (최대 20페이지, 페이지당 100개 댓글)

## 설정 참고사항

- 유튜브 API 키가 크롤러 파일에 하드코딩되어 있음 (환경 변수로 이동 필요)
- 테스트 데이터와 출력 파일은 `/test` 디렉토리에 저장됨
- 시스템은 한국어 텍스트 처리 (UTF-8 인코딩 필수)
- FastAPI 서버는 개발용 자동 리로드로 기본 포트에서 실행

## 의존성

`test/requirements.txt`의 주요 Python 패키지:
- `fastapi` - 웹 프레임워크
- `uvicorn` - ASGI 서버
- `requests` - 유튜브 API용 HTTP 클라이언트
- `pydantic` - 데이터 검증