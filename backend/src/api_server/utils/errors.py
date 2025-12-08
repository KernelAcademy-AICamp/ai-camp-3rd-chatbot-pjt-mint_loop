"""Error handling utilities."""

ERROR_MAPPINGS = {
    ("429", "resource_exhausted", "quota"): "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.",
    ("safety", "content_policy", "blocked"): "요청하신 이미지를 생성할 수 없습니다. 다른 내용으로 시도해 주세요.",
    ("401", "unauthorized", "invalid"): "서비스 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.",
    ("connection", "timeout", "network"): "서버 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.",
}

DEFAULT_ERROR = "이미지 생성 중 오류가 발생했습니다. 다시 시도해 주세요."


def convert_to_user_error(error_msg: str) -> str:
    """Convert technical error message to user-friendly message."""
    error_lower = error_msg.lower()

    for keywords, message in ERROR_MAPPINGS.items():
        if any(kw in error_lower or kw in error_msg for kw in keywords):
            return message

    if "결과가 비어있습니다" in error_msg or "empty" in error_lower:
        return "요청하신 이미지를 생성할 수 없습니다. 다른 내용으로 시도해 주세요."

    return DEFAULT_ERROR