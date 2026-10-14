# fons4py-reimbursement-agent

> Python 报销领域 Agent：用自然语言创建报销草稿，经用户确认后提交；通过 A2A 协议接受 Java 主 Agent（fons4ai-trip）的任务委派。

技术底座：Python 3.11 · FastAPI · Pydantic v2 · SQLAlchemy 2.x · MySQL 8 · LangChain · LangGraph · 官方 A2A SDK。

## 1. 项目背景与目标

本项目服务两个目标：

1. **学习**：通过真实开发从 0 到 1 掌握 Python 与 Agent 技术栈，逐日推进、按天验收。
2. **交付**：一个可在 AI Agent 面试中演示的跨语言协作 MVP——Java 主编排 + Python 领域 Agent。

开发预算：10 个开发日 × 3 小时 = 30 小时，另留 6–12 小时风险缓冲；面试准备优先，开发日可顺延。

| 里程碑 | 范围 | 验收 |
|---|---|---|
| **M1（Day 1–5）** | FastAPI + MySQL + 领域服务 + LangChain + 基础 LangGraph | 自然语言创建并查询报销草稿 |
| **M2（Day 6–10）** | HITL 确认提交 + A2A Server + Java 联调 + 演示 | 确认后提交；A2A 调用验收；5 分钟演示可复现 |

## 2. 业务设计

> 需求细节见 [docs/01-product-requirements.md](docs/01-product-requirements.md)，领域与数据模型见 [docs/03-domain-and-data.md](docs/03-domain-and-data.md)。

### 2.1 一句话业务

员工用自然语言提出报销 → 系统创建**草稿** → 展示摘要 → **用户明确确认** → 提交，返回单号。

### 2.2 核心业务场景

| 场景 | 示例 | 系统行为 |
|---|---|---|
| 日常报销 | “报销办公用品 200 元，昨天购买” | 创建 DRAFT → 展示草稿 → 用户确认 → SUBMITTED |
| 差旅报销 | “关联差旅单 T001，报销高铁票 560 和住宿 800” | 差旅单查询（MVP Mock）→ DRAFT → 确认提交 |
| 信息不全 | “报销交通费” | 追问金额/日期等必填信息，**不杜撰** |
| 修改草稿 | “住宿费改成 750 元” | 修改并重算总额，**原确认信息失效** |
| 重试 | A2A/HTTP 重放同一操作 | 幂等处理，不重复建单、不重复提交 |

### 2.3 领域模型与状态机

报销单是一个聚合，费用明细不能脱离报销单单独存在；每次变更后聚合内重算总额、版本号 +1（版本号是确认失效机制的基础）。

```text
ReimbursementOrder（报销单 · 聚合根）
├── order_no 单号(唯一) / applicant_id 申请人 / type(TRAVEL|DAILY)
├── title 标题 / currency(CNY) / total_amount 总金额 / version 版本号
├── trip_source / trip_id / trip_no   ← 差旅单引用（可空，只存引用，不复制差旅数据）
└── ExpenseItem[]（费用明细）
    └── expense_type(8 种) / expense_date / amount / description
```

```text
DRAFT(草稿, 可增删改费用) ──用户确认+校验通过──▶ SUBMITTED(已提交, 终态)
DRAFT ──取消──▶ CANCELLED(终态)
```

说明：`PENDING_CONFIRMATION` **不是**业务状态——“等待确认”是 Agent 任务状态，不落业务库；业务真相只有三个状态，简单即可审计。

### 2.4 核心业务规则

| 规则 | 内容 |
|---|---|
| 金额精度 | `Decimal` 计算，CNY、2 位小数、必须为正；**禁止 float** |
| 提交前置校验 | 至少一条费用明细、费用类型合法、同币种 |
| 确认凭证 | 服务端签发，绑定 `order_id + 申请人 + version + 总金额 + 过期时间`，**一次性消费** |
| 确认失效 | 草稿被修改（版本变化）后，旧确认凭证立即作废 |
| 幂等 | 创建/提交带幂等键，重试不产生重复单据、不重复提交 |
| 授权 | 申请人身份来自认证上下文，**不由 LLM 决定** |

**确认凭证是本项目最重要的安全设计**，防的是“给用户看 200 元摘要、实际提交 500 元单据”：用户确认的是具体版本 + 具体金额，草稿一动确认作废，必须重新确认。

### 2.5 LLM 与确定性代码的边界

本项目的设计原则：**LLM 只负责理解与表达，规则与金额永远由确定性代码裁决**。

| LLM 负责 | 确定性代码负责 |
|---|---|
| 理解自然语言、提取字段 | 金额计算（Decimal） |
| 信息不全时追问（不杜撰） | 规则校验、状态转换 |
| 生成人话摘要 | 确认凭证签发/校验、提交 |
| 决定调用哪个工具 | 幂等、事务、授权 |

`submit` 不是 LLM 可无条件调用的工具——只有持有有效确认凭证的应用服务才能执行提交。

## 3. 系统设计

> 架构细节见 [docs/02-architecture.md](docs/02-architecture.md)，Agent 工作流与 A2A 映射见 [docs/04-agent-workflow.md](docs/04-agent-workflow.md)。

### 3.1 架构总览

```text
用户 / Java 主 Agent
 │  HTTP（M1 独立调试入口，不依赖 Java） / A2A 协议（M2 任务委派）
 ▼
uvicorn → FastAPI（Web 层）→ Pydantic（DTO 校验）
 │
 ├─ Agent 层：LangGraph（工作流状态机）⇄ LangChain（LLM + Tool Calling）
 │             └─ interrupt 中断等待用户确认（HITL）
 │
 ├─ 业务层：application（用例 / 事务 / 授权）→ domain（规则 + Decimal 计算）
 │
 └─ 数据层：SQLAlchemy（ORM）→ Alembic（迁移）→ MySQL 8
```

分层职责（Agent 只能经 application 用例访问业务，不直接读写数据库）：

| 层 | 目录 | 职责 |
|---|---|---|
| API | `api/` | FastAPI 路由、Pydantic DTO |
| Agent | `agents/` `graph/` `a2a/` | LangChain 工具、LangGraph 工作流、A2A 适配 |
| 应用 | `application/` | 用例编排、事务边界、业务授权 |
| 领域 | `domain/` | 纯业务规则、状态机、金额计算（零框架依赖） |
| 基础设施 | `infrastructure/` | ORM、仓储、Trip Mock、Checkpointer |

### 3.2 技术栈与选型理由（Java 对照）

| 技术 | 解决什么问题 | Java 世界对照 |
|---|---|---|
| Python 3.11 | 语言运行时；重点是类型注解与 async/await | Java 17+ |
| uv | 项目与依赖管理（`pyproject.toml` ≈ pom.xml，`uv.lock` 锁版本，`.venv` 隔离环境） | Maven/Gradle |
| FastAPI | Web 框架：路由、依赖注入、自动 API 文档 | Spring MVC + Spring Boot |
| Pydantic v2 | DTO 定义 + 校验 + 序列化，一处类型注解多处复用 | Bean Validation + Jackson 合体 |
| uvicorn | ASGI 异步服务器 | 内嵌 Tomcat / Netty |
| SQLAlchemy 2.x | ORM；AsyncSession 异步会话 | Hibernate / JPA（async 模式 ≈ R2DBC） |
| Alembic | 数据库结构版本化迁移 | Flyway / Liquibase |
| python-dotenv | `.env` 配置加载，密钥不进 Git | application.properties + 环境变量 |
| pytest | 单元/集成测试 | JUnit 5 + AssertJ |
| Decimal | 十进制精确金额 | BigDecimal（同一理由：二进制浮点误差） |
| LangChain | LLM 框架：统一模型接口、消息抽象、Tool Calling | LangChain4j / Spring AI |
| LangGraph | 有状态工作流引擎：节点/边/分支/中断/恢复 | AgentScope Workflow |
| A2A SDK | Agent 互操作：Agent Card 能力发现、Task 生命周期 | 无直接对照，HTTP 语义的跨语言协议 |

### 3.3 关键技术决策

**为什么 LangChain 之外还要 LangGraph？**
LangChain Agent 是“模型自主循环”，适合一问一答；但报销流程有不能交给 LLM 自由发挥的卡点——提交前必须等真实用户确认。LangGraph 用显式状态图编排（收集 → 校验 → 草稿 → interrupt 等确认 → 提交）：`interrupt()` 暂停、`Command(resume=...)` 恢复、Checkpointer 存状态。**可控性是 HITL 安全的根基**。两者关系：LangGraph 做流程编排，LangChain 做其中“理解自然语言、提取字段”的节点能力。

**为什么领域层与基础设施隔离？**
`domain/` 零框架依赖，是唯一可信的业务真相层；LLM 只能通过 Tool 间接调用 application 用例，永远接触不到 ORM 和 SQL——这是“AI 不直接改库”的安全边界。

**为什么必须 Decimal？**
`0.1 + 0.2 != 0.3` 在二进制浮点下成立，金额会算错；和 Java 用 BigDecimal 同一理由。

### 3.4 与 Java 系统的集成边界

| 关注点 | 约定 |
|---|---|
| 职责划分 | 报销单数据归 Python；差旅单数据归 Java（fons4ai-trip） |
| 引用方式 | 报销单只存 trip_source/trip_id/trip_no 引用，不复制差旅域 |
| 通信协议 | A2A：Python 发布 Agent Card，Java 主 Agent 委派任务 |
| 身份传递 | 调用者身份来自认证上下文，跨协议传播需受控可信通道 |
| 任务状态映射 | working=执行中 / input-required=等待用户输入 / completed=完成 / failed=失败 |

## 4. 文档导航

| 文档 | 用途 |
|---|---|
| [AGENTS.md](AGENTS.md) | AI 编码 Agent 工作契约（目标 / 红线 / 规程） |
| [docs/01-product-requirements.md](docs/01-product-requirements.md) | 需求细节：场景、需求清单 F01–F11、边界、验收 |
| [docs/02-architecture.md](docs/02-architecture.md) | 架构细节：模块职责、目录结构、接口建议 |
| [docs/03-domain-and-data.md](docs/03-domain-and-data.md) | 领域模型、状态机、MySQL 建表设计、一致性方案 |
| [docs/04-agent-workflow.md](docs/04-agent-workflow.md) | LangGraph 工作流、HITL、A2A 映射 |
| [docs/05-development-board.md](docs/05-development-board.md) | 10 天开发看板、里程碑、阻塞升级原则 |
| [docs/06-testing-and-demo.md](docs/06-testing-and-demo.md) | 测试矩阵 T01–T09、演示脚本、每日 DoD |
| [docs/tasks/](docs/tasks/) | 逐日任务单 DAY-01 ~ DAY-10 |

## 5. 快速开始

环境要求：

- Python 3.11（仓库 `.python-version` 锁定）
- 包管理：[uv](https://docs.astral.sh/uv/)
- MySQL 8（Day 2 起需要）
- LLM API Key（OpenAI 兼容端点，Day 4 起需要，通过 `.env` 配置，不进 Git）

```bash
# 安装依赖（含 dev 测试依赖）
uv sync --all-groups

# 运行测试
uv run pytest

# 启动开发服务器
uv run uvicorn reimbursement.main:app --reload
```

启动后访问：

- 健康检查：<http://127.0.0.1:8000/health>
- API 文档（Swagger UI）：<http://127.0.0.1:8000/docs>

Docker 一键启动在 Day 10 提供。

## 6. 外部依赖与风险声明

- Java 主编排仓库：[nauyiq/fons4ai-trip](https://github.com/nauyiq/fons4ai-trip)。其 A2A API **尚未核验**，Day 8 必须先做兼容性检查；若不兼容，按看板阻塞升级原则以标准 A2A Client 完成协议验收兜底。
- 依赖版本以开发当天的官方文档及 `uv.lock` 为准，不复制旧版 LangChain/LangGraph 教程。
