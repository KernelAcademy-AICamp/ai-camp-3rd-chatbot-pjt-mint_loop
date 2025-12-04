#!/bin/bash

# Claude로부터 받은 JSON 입력 파싱
# stdin으로부터 입력을 읽어 파일 경로를 찾습니다.
INPUT=$(cat)

# 파일 경로 추출 (tool_input에서 file_path 찾기)
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path":"[^"]*' | sed 's/"file_path":"//')

# FILE_PATH가 없으면 환경변수에서 가져오기
if [ -z "$FILE_PATH" ]; then
    FILE_PATH="$CLAUDE_FILE_PATHS"
fi

# 파일 경로가 없으면 통과
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

PATTERNS=(
    "password"
    "api_key" 
    "secret"
    "AWS[A-Z0-9]{16}"
)

for pattern in "${PATTERNS[@]}"; do
    # 파일 내용($CLAUDE_TOOL_INPUT)에서 패턴 검사
    if echo "$CLAUDE_TOOL_INPUT" | grep -i -E -q "$pattern"; then
        echo "⚠️ 보안 경고: 민감 정보($pattern)가 코드에 포함되려 합니다! 작업을 차단합니다." >&2
        exit 2 # 2번 코드로 종료하여 Claude 작업을 차단
    fi
    
    # CLAUDE_TOOL_INPUT이 비어있으면 INPUT에서도 검사
    if echo "$INPUT" | grep -i -E -q "$pattern"; then
        echo "⚠️ 보안 경고: 민감 정보($pattern)가 코드에 포함되려 합니다! 작업을 차단합니다." >&2
        exit 2
    fi
done

exit 0 # 문제가 없으면 0번 코드로 통과