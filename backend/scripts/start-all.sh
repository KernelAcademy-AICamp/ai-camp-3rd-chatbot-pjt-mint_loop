#!/bin/bash

# 이미지 생성 Agent 시스템 전체 시작 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로고 출력
echo -e "${BLUE}"
echo "=========================================="
echo "  Image Generation Agent System"
echo "  Starting All Services..."
echo "=========================================="
echo -e "${NC}"

# .env 파일 확인
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다. .env.example을 복사합니다...${NC}"
    cp .env.example .env
    echo -e "${RED}❌ .env 파일을 편집하여 API 키를 설정하세요!${NC}"
    echo -e "${YELLOW}   필수 항목: OPENAI_API_KEY, TAVILY_API_KEY${NC}"
    exit 1
fi

# API 키 확인
source .env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY가 설정되지 않았습니다!${NC}"
    echo -e "${YELLOW}   .env 파일에서 OPENAI_API_KEY를 설정하세요.${NC}"
    exit 1
fi

if [ -z "$TAVILY_API_KEY" ] || [ "$TAVILY_API_KEY" = "your_tavily_api_key_here" ]; then
    echo -e "${RED}❌ TAVILY_API_KEY가 설정되지 않았습니다!${NC}"
    echo -e "${YELLOW}   .env 파일에서 TAVILY_API_KEY를 설정하세요.${NC}"
    exit 1
fi

# 빌드 모드 확인
BUILD_MODE=${1:-""}

if [ "$BUILD_MODE" = "build" ]; then
    echo -e "${BLUE}🔨 Building Docker images...${NC}"
    docker-compose build --no-cache
else
    echo -e "${BLUE}🚀 Starting services (using existing images)...${NC}"
fi

# Docker Compose로 서비스 시작
echo -e "${GREEN}Starting Docker containers...${NC}"
docker-compose up -d

# 서비스 상태 확인
echo -e "${BLUE}Waiting for services to be healthy...${NC}"
sleep 5

# 서비스별 헬스체크
check_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1

    echo -n "Checking $service_name (port $port)... "

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:$port/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Healthy${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e "${RED}✗ Failed${NC}"
    return 1
}

# MCP 서버 헬스체크
check_service "Search MCP" 8050
check_service "Image MCP" 8051

# 최종 상태 확인
echo -e "\n${BLUE}=========================================="
echo "  Service Status"
echo "==========================================${NC}"
docker-compose ps

echo -e "\n${GREEN}✅ All services started successfully!${NC}"
echo -e "\n${BLUE}Available endpoints:${NC}"
echo -e "  - Search MCP Server:    ${GREEN}http://localhost:8050${NC}"
echo -e "  - Image MCP Server:     ${GREEN}http://localhost:8051${NC}"
echo -e "  - Image Agent (A2A):    ${GREEN}http://localhost:8080${NC}"

echo -e "\n${BLUE}Useful commands:${NC}"
echo -e "  - View logs:           ${YELLOW}docker-compose logs -f${NC}"
echo -e "  - View specific logs:  ${YELLOW}docker-compose logs -f search-mcp${NC}"
echo -e "  - Stop all services:   ${YELLOW}./scripts/stop-all.sh${NC}"
echo -e "  - Restart services:    ${YELLOW}docker-compose restart${NC}"

echo -e "\n${BLUE}To run examples:${NC}"
echo -e "  ${YELLOW}docker-compose exec image-agent python examples/basic_usage.py${NC}"

echo ""
