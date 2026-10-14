"""健康检查路由。"""

from datetime import datetime, timezone

from fastapi import APIRouter

from reimbursement import __version__
from reimbursement.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """健康检查：确认服务存活并返回基本元信息。

    async def 对照 Java：类似返回 CompletableFuture 的非阻塞方法。
    Python 事件循环协作式调度——当前没有 I/O 等待，直接返回即可；
    后续接入数据库/LLM 后，await 的价值才会体现。
    """
    return HealthResponse(
        status="UP",
        app="fons4py-reimbursement-agent",
        version=__version__,
        timestamp=datetime.now(timezone.utc),
    )
