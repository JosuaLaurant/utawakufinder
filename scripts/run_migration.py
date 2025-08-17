#!/usr/bin/env python3
"""
컨테이너 내에서 마이그레이션을 실행하는 스크립트
"""

import subprocess
import sys
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """Docker 컨테이너 내에서 마이그레이션 실행"""
    logger.info("🚀 PostgreSQL 마이그레이션 시작")
    
    try:
        # 먼저 빈 백엔드 컨테이너 시작해서 마이그레이션 실행
        logger.info("백엔드 컨테이너로 마이그레이션 실행...")
        
        # Docker 컨테이너 빌드
        build_cmd = ["docker", "compose", "build", "backend"]
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Docker 빌드 실패: {result.stderr}")
            return False
        
        # 마이그레이션 실행
        migration_cmd = [
            "docker", "compose", "run", "--rm", "backend", 
            "python", "migrate_to_postgres.py"
        ]
        
        result = subprocess.run(migration_cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            logger.info("✅ 마이그레이션 완료!")
            return True
        else:
            logger.error(f"❌ 마이그레이션 실패: return code {result.returncode}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 마이그레이션 중 오류: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)