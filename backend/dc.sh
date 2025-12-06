#!/bin/bash
# Docker Compose wrapper script
# .env 파일을 자동으로 찾아서 --env-file 옵션으로 전달

# .env 파일 경로 찾기
if [ -f ".env" ]; then
    ENV_FILE=".env"
elif [ -f "../.env" ]; then
    ENV_FILE="../.env"
else
    echo "Error: .env file not found in current or parent directory"
    exit 1
fi

echo "Using env file: $ENV_FILE"

# docker-compose 실행
docker-compose --env-file "$ENV_FILE" "$@"
