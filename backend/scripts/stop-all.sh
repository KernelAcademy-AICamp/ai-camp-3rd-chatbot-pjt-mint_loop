#!/bin/bash

# 이미지 생성 Agent 시스템 전체 중지 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=========================================="
echo "  Image Generation Agent System"
echo "  Stopping All Services..."
echo "=========================================="
echo -e "${NC}"

# 서비스 중지
echo -e "${YELLOW}Stopping Docker containers...${NC}"
docker-compose down

# 정리 옵션
CLEANUP=${1:-""}

if [ "$CLEANUP" = "clean" ]; then
    echo -e "${RED}🧹 Cleaning up volumes and images...${NC}"
    docker-compose down -v
    docker system prune -f
    echo -e "${GREEN}✅ Cleanup completed!${NC}"
else
    echo -e "${GREEN}✅ All services stopped!${NC}"
    echo -e "${YELLOW}To clean up volumes and images, run: ./scripts/stop-all.sh clean${NC}"
fi

echo ""
