"""A2A 프로토콜 통합 예제

이 예제는 이미지 생성 Agent를 A2A 프로토콜과 통합하여
외부 Agent나 시스템과 통신할 수 있도록 하는 방법을 보여줍니다.
"""
import asyncio
import os
from datetime import datetime
from typing import Any

import pytz
import structlog
from dotenv import load_dotenv

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore, TaskManager, TaskUpdater
from a2a.types import (
    DataPart,
    Message,
    Part,
    Task,
    TaskState,
    TaskStatus,
    TextPart,
)
from a2a.utils import new_agent_parts_message, new_agent_text_message
from langchain_core.messages import HumanMessage

# 환경변수 로드
load_dotenv()

logger = structlog.get_logger(__name__)


class ImageGenerationA2AExecutor(AgentExecutor):
    """A2A 프로토콜을 지원하는 이미지 생성 Agent Executor

    이 Executor는 A2A 프로토콜을 사용하여 다른 Agent나 시스템과
    통신할 수 있도록 이미지 생성 Agent를 래핑합니다.
    """

    def __init__(self, agent, enable_streaming: bool = False):
        """
        Args:
            agent: ImageGenerationAgent 인스턴스
            enable_streaming: 스트리밍 모드 활성화 여부
        """
        self.agent = agent
        self.enable_streaming = enable_streaming
        self.task_store = InMemoryTaskStore()

        logger.info("ImageGenerationA2AExecutor initialized")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue
    ) -> None:
        """A2A 요청 실행

        Args:
            context: A2A 요청 컨텍스트
            event_queue: 이벤트 큐
        """
        try:
            logger.info(f"Starting A2A execution for task: {context.task_id}")

            # 사용자 입력 추출
            user_input = context.get_user_input()
            task_id = str(context.task_id)
            context_id = str(getattr(context, "context_id", task_id))

            # TaskUpdater 생성
            updater = TaskUpdater(
                event_queue=event_queue,
                task_id=task_id,
                context_id=context_id
            )

            # 작업 시작 알림
            await updater.update_status(
                TaskState.working,
                new_agent_text_message("이미지 생성을 시작합니다...")
            )

            # Agent 실행
            result = await self.agent.generate(
                user_prompt=user_input,
                thread_id=context_id
            )

            # 결과 처리
            if result["status"] == "completed":
                # 성공적으로 이미지 생성됨
                parts = []

                # 텍스트 파트: 결과 요약
                summary = f"""이미지 생성 완료!

추출된 키워드: {', '.join(result['extracted_keywords'])}
최적화된 프롬프트: {result['optimized_prompt']}
"""
                parts.append(Part(root=TextPart(text=summary)))

                # 데이터 파트: 구조화된 결과
                data_content = {
                    "image_url": result["generated_image_url"],
                    "metadata": result["image_metadata"],
                    "keywords": result["extracted_keywords"],
                    "optimized_prompt": result["optimized_prompt"],
                    "timestamp": datetime.now(tz=pytz.timezone("Asia/Seoul")).isoformat()
                }
                parts.append(Part(root=DataPart(data=data_content)))

                # 최종 메시지 전송
                final_message = new_agent_parts_message(parts)
                await updater.update_status(
                    TaskState.completed,
                    final_message,
                    final=True
                )

                logger.info(f"Task {task_id} completed successfully")

            else:
                # 에러 발생
                error_message = new_agent_text_message(
                    f"이미지 생성 실패: {result.get('error', 'Unknown error')}"
                )
                await updater.update_status(
                    TaskState.failed,
                    error_message,
                    final=True
                )

                logger.error(f"Task {task_id} failed: {result.get('error')}")

        except Exception as e:
            logger.error(f"A2A execution failed: {e}")

            # 에러 상태 업데이트
            try:
                updater = TaskUpdater(
                    event_queue=event_queue,
                    task_id=str(context.task_id),
                    context_id=str(getattr(context, "context_id", context.task_id))
                )
                await updater.update_status(
                    TaskState.failed,
                    new_agent_text_message(f"작업 중 오류 발생: {str(e)}"),
                    final=True
                )
            except Exception as update_error:
                logger.error(f"Failed to update error status: {update_error}")

            raise

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue
    ) -> None:
        """진행 중인 작업 취소

        Args:
            context: 요청 컨텍스트
            event_queue: 이벤트 큐
        """
        logger.info(f"Cancelling task: {context.task_id}")

        if context.current_task:
            updater = TaskUpdater(
                event_queue=event_queue,
                task_id=context.current_task.id,
                context_id=str(context.context_id)
            )
            await updater.cancel()
            logger.info(f"Task {context.task_id} cancelled")


async def main():
    """A2A 통합 예제 실행"""

    print("=== A2A 프로토콜 통합 예제 ===\n")

    # 1. MCP 서버에서 도구 로드
    from langchain_mcp_adapters.client import MultiServerMCPClient

    mcp_servers = {
        "search": {
            "transport": "streamable_http",
            "url": "http://localhost:8050/mcp"
        },
        "image": {
            "transport": "streamable_http",
            "url": "http://localhost:8051/mcp"
        }
    }

    print("1. MCP 서버 연결 중...")
    mcp_client = MultiServerMCPClient(mcp_servers)
    tools = await mcp_client.get_tools()

    search_tools = [t for t in tools if "search" in t.name or "keyword" in t.name]
    image_tools = [t for t in tools if "image" in t.name or "prompt" in t.name]

    print(f"   ✓ {len(search_tools)} 검색 도구 로드됨")
    print(f"   ✓ {len(image_tools)} 이미지 도구 로드됨\n")

    # 2. Agent 생성
    from src.image_agent.agent import ImageGenerationAgent

    agent = ImageGenerationAgent(
        search_tools=search_tools,
        image_tools=image_tools
    )

    print("2. 이미지 생성 Agent 초기화 완료\n")

    # 3. A2A Executor 생성
    executor = ImageGenerationA2AExecutor(agent=agent)

    print("3. A2A Executor 초기화 완료\n")

    # 4. A2A 서버로 등록
    from a2a.server import A2AServer

    server = A2AServer(
        agent_name=os.getenv("A2A_AGENT_NAME", "ImageGenerationAgent"),
        executor=executor,
        host=os.getenv("A2A_AGENT_HOST", "0.0.0.0"),
        port=int(os.getenv("A2A_AGENT_PORT", 8080))
    )

    print(f"4. A2A 서버 시작: {server.host}:{server.port}\n")
    print("서버가 실행 중입니다. Ctrl+C로 종료하세요.\n")

    # 5. 서버 실행
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n서버를 종료합니다...")
