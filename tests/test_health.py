"""Day 01 基础测试：/health 与 API 文档可访问性。

对照 Java：TestClient ≈ MockMvc / WebTestClient，不启动真实服务器即可发请求。
"""

from fastapi.testclient import TestClient

from reimbursement.main import app

client = TestClient(app)


def test_health_returns_200_and_payload() -> None:
    """T01 前置：服务存活，/health 返回 200 且负载结构完整。"""
    resp = client.get("/health")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "UP"
    assert body["app"] == "fons4py-reimbursement-agent"
    assert body["version"]  # 非空即视为有效
    assert body["timestamp"]  # Pydantic 自动把 datetime 序列化为 ISO 8601 字符串


def test_openapi_docs_available() -> None:
    """验收项：API 文档访问成功。/docs(Swagger UI) 的数据源是 /openapi.json。"""
    resp = client.get("/openapi.json")

    assert resp.status_code == 200
    assert "/health" in resp.json()["paths"]
