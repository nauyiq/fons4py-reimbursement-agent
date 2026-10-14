"""API 层通用 DTO（Pydantic 模型）。

对照 Java：BaseModel ≈ DTO 类 + Bean Validation 注解 + Jackson 序列化的合体。
类型注解一处定义，校验、序列化、OpenAPI 文档三处复用。
"""

from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str = Field(description="服务状态，UP 表示正常")
    app: str = Field(description="应用名称")
    version: str = Field(description="应用版本号")
    timestamp: datetime = Field(description="服务端当前时间（UTC，ISO 8601 格式）")
