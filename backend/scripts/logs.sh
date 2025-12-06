#!/bin/bash

# 로그 조회 스크립트

set -e

# 색상 정의
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVICE=${1:-""}

if [ -z "$SERVICE" ]; then
    echo -e "${BLUE}All services logs (press Ctrl+C to exit):${NC}"
    docker-compose logs -f
else
    echo -e "${BLUE}Logs for $SERVICE (press Ctrl+C to exit):${NC}"
    docker-compose logs -f "$SERVICE"
fi
