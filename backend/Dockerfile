FROM python:3.11-slim

WORKDIR /app

# backend 폴더에서 requirements.txt 복사
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 전체 프로젝트 복사 (구조 변경으로 인해)
COPY . .

# 작업 디렉토리를 backend로 변경
WORKDIR /app/backend

EXPOSE 9030

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9030", "--reload"]