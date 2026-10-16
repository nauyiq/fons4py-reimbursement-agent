"""数据库连接配置与会话工厂。

对照 Java：
- create_engine()      ≈ DataSource（内置连接池，对照 HikariCP）
- async_sessionmaker   ≈ EntityManagerFactory
- AsyncSession         ≈ EntityManager（事务边界归调用方管理，本模块不开启事务）

凭证来源：项目根 .env（已被 .gitignore 忽略，真实密钥绝不进 Git）。
"""

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "reimbursement")


def build_mysql_url() -> str:
    """构造 asyncmy 异步连接串。

    密码必须 URL 编码：含 @ : / 等字符时未编码会解析错位。
    """
    password = quote_plus(DB_PASSWORD)
    return (
        f"mysql+asyncmy://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )


def create_engine() -> AsyncEngine:
    """创建异步引擎。

    pool_pre_ping=True：取连接前先探活，避免用到被服务端断开的连接
    （对照 HikariCP 的 connectionTestQuery）。
    """
    return create_async_engine(build_mysql_url(), pool_pre_ping=True, echo=False)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """会话工厂。

    expire_on_commit=False：提交后对象不过期。异步会话下若提交后再访问
    属性会触发隐式 lazy load，直接抛 MissingGreenlet 错误——这是 async ORM
    与 Java/JPA 最大的行为差异之一，务必记住。
    """
    return async_sessionmaker(engine, expire_on_commit=False)
