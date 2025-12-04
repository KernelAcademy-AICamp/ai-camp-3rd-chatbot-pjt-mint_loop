#!/bin/bash

# JSON stdin에서 데이터 읽기
JSON_INPUT=$(cat)

echo "🔥 PostToolUse 실행!" >&2

# 파일 경로 추출
if command -v jq &> /dev/null; then
    FILE_PATH=$(echo "$JSON_INPUT" | jq -r '.tool_input.file_path // .tool_input.path // .file_path // .path // empty')
    TOOL_NAME=$(echo "$JSON_INPUT" | jq -r '.tool_name // "Unknown"')
else
    FILE_PATH=$(echo "$JSON_INPUT" | grep -o '"file_path":"[^"]*' | sed 's/"file_path":"//' | head -1)
fi

echo "🔧 Tool: $TOOL_NAME" >&2
echo "📁 File: $FILE_PATH" >&2

# 파일이 존재하고 포맷팅 대상이면 실행
if [[ -n "$FILE_PATH" && -f "$FILE_PATH" && "$FILE_PATH" =~ \.(ts|js|tsx|jsx|json|css|md)$ ]]; then
    echo "📝 포맷팅 시작: $FILE_PATH" >&2
    
    # Prettier 실행 방법 우선순위 체크
    if command -v prettier &> /dev/null; then
        # 전역 설치된 prettier 사용
        prettier --write "$FILE_PATH" && echo "✅ $FILE_PATH 포맷팅 완료 (global)" >&2
    elif [ -f "./node_modules/.bin/prettier" ]; then
        # 로컬 설치된 prettier 직접 실행
        ./node_modules/.bin/prettier --write "$FILE_PATH" && echo "✅ $FILE_PATH 포맷팅 완료 (local)" >&2
    elif [ -f "package.json" ] && npm list prettier &> /dev/null; then
        # npx로 실행 (package.json에 prettier가 있는 경우)
        npx prettier --write "$FILE_PATH" && echo "✅ $FILE_PATH 포맷팅 완료 (npx)" >&2
    else
        echo "⚠️  Prettier를 찾을 수 없음" >&2
        echo "💡 현재 디렉토리: $(pwd)" >&2
        echo "💡 package.json 존재: $([ -f "package.json" ] && echo "Yes" || echo "No")" >&2
        echo "💡 node_modules/.bin/prettier 존재: $([ -f "./node_modules/.bin/prettier" ] && echo "Yes" || echo "No")" >&2
    fi
else
    echo "ℹ️  포맷팅 건너뜀: $FILE_PATH" >&2
fi

# 로그 기록
echo "$(date): PostToolUse - Tool: $TOOL_NAME, File: $FILE_PATH" >> /tmp/claude-hooks.log

echo '{"continue": true}'
exit 0