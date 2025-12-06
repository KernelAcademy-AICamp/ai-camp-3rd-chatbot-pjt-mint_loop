#!/bin/bash

# 예제 실행 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

EXAMPLE=${1:-"basic"}

echo -e "${BLUE}Running $EXAMPLE example...${NC}\n"

case $EXAMPLE in
    basic)
        docker-compose exec image-agent python examples/basic_usage.py
        ;;
    advanced)
        docker-compose exec image-agent python examples/advanced_usage.py
        ;;
    a2a)
        echo -e "${YELLOW}A2A example is already running as a service${NC}"
        echo -e "${YELLOW}Check logs with: ./scripts/logs.sh image-agent${NC}"
        ;;
    *)
        echo -e "${YELLOW}Unknown example: $EXAMPLE${NC}"
        echo -e "${BLUE}Available examples:${NC}"
        echo -e "  - basic:    Basic usage example"
        echo -e "  - advanced: Advanced features example"
        echo -e "  - a2a:      A2A integration (running as service)"
        ;;
esac

echo ""
