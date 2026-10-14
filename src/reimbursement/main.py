"""FastAPI 应用入口。

启动开发服务器：
    uv run uvicorn reimbursement.main:app --reload

访问：
    健康检查  http://127.0.0.1:8000/health
    API 文档  http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from reimbursement.api.health import router as health_router


def create_app() -> FastAPI:
    """应用工厂：集中装配路由与配置，测试可复用同一构造逻辑。

    对照 Java：类似 Spring 的 @Configuration + Bean 装配，
    但这里是显式函数调用，没有类路径扫描和依赖注入容器。
    """
    app = FastAPI(
        title="fons4py-reimbursement-agent",
        version="0.1.0",
        description="Python 报销领域 Agent：自然语言创建报销草稿，经用户确认后提交。",
    )
    app.include_router(health_router)
    return app


app = create_app()
