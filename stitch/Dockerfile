# 파이썬 경량 베이스 이미지 사용
FROM python:3.11-slim

# 표준 출력/에러 버퍼링 방지 (Cloud Logging에 즉각 표시)
ENV PYTHONUNBUFFERED True

# 작업 디렉터리 설정
WORKDIR /app

# 종속성 파일 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . ./

# Gunicorn WSGI 서버로 실행 (Cloud Run 표준: 0.0.0.0:$PORT)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
