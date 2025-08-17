# Scripts

데이터베이스 마이그레이션 및 유틸리티 스크립트들입니다.

## 파일 설명

### 데이터베이스 관련
- `init.sql`: PostgreSQL 초기 스키마 생성
- `migrate_to_postgres.py`: JSON 데이터를 PostgreSQL로 마이그레이션
- `migrate_data.py`: 데이터 마이그레이션 헬퍼 함수들
- `run_migration.py`: 마이그레이션 실행 스크립트

### 유틸리티
- `main_json.py`: JSON 기반 백엔드 (레거시)

## 사용법

### PostgreSQL 마이그레이션

1. PostgreSQL 서버가 실행 중인지 확인
2. 환경 변수 설정 (.env 파일)
3. 마이그레이션 실행:

```bash
cd scripts
python run_migration.py
```

### 개별 스크립트 실행

```bash
# 데이터 마이그레이션
python migrate_to_postgres.py

# JSON 기반 서버 (테스트용)
python main_json.py
```

## 주의사항

- 마이그레이션 전에 기존 데이터를 백업하세요
- PostgreSQL 서버가 실행 중이고 연결 가능한지 확인하세요
- 환경 변수가 올바르게 설정되었는지 확인하세요