# 10 天任务看板（每天 3 小时）

## 看板规则

状态：`TODO` / `IN_PROGRESS` / `BLOCKED` / `DONE`。**每天 30 分钟学习 + 120 分钟实现 + 30 分钟验收**。30 小时是目标预算；预留 6–12 小时缓冲，但不可擅自扩展范围。

| Day | 任务 | 核心学习 | 当日验收 | 状态 |
|---|---|---|---|---|
| 01 | Python 环境 + FastAPI | uv、Pydantic、async/await | /health、基本 DTO/API | DONE |
| 02 | MySQL + ORM | SQLAlchemy、AsyncSession、Alembic | 两张核心表 CRUD | DONE |
| 03 | 领域服务 | dataclass、Decimal、pytest | 草稿/明细/金额/提交事务 | TODO |
| 04 | LangChain Agent | Messages、Tools、create_agent | 自然语言创建草稿 | TODO |
| 05 | LangGraph | StateGraph、nodes、edges | 草稿流程图跑通 | TODO |
| 06 | HITL | interrupt、Command、checkpoint | 明确确认后提交 | TODO |
| 07 | Python A2A | Agent Card、Executor | 标准 Client 调用成功 | TODO |
| 08 | Java A2A | 协议适配、身份/超时 | Java 调 Python 创建草稿 | TODO |
| 09 | 端到端联调 | A2A 任务映射、幂等 | 主链路 + 核心测试 | TODO |
| 10 | Demo 与文档 | Docker、README、技术表达 | 5 分钟演示可复现 | TODO |

## 里程碑

- **M1 / Day 5**：单独运行 Python 服务，自然语言生成可查询的报销草稿。
- **M2 / Day 10**：正式确认与提交、标准 A2A Client 验收、优先完成 Java ↔ Python 联动。

## 阻塞升级原则

1. SDK API 不兼容超过当天预算：做最小验证并记录，不推倒已完成模块。
2. Java 接入阻塞：先以标准 A2A Client 达成协议验收，Java 集成标记 BLOCKED。
3. 数据库进度阻塞：可 Mock 业务 API 学 Agent，但不能将 Mock 称为最终持久化完成。
4. HITL 阻塞：至少保证用户确认受控提交；中断/恢复另行单独验收。
5. 绝不为按时结束而跳过提交授权、金额精度和副作用幂等。

## 使用方法

每天向编码 Agent 发送：`按照 AGENTS.md 执行 docs/tasks/DAY-01.md；只做 Day 01，完成后运行测试并总结差异。` 每天更换日期；验收通过后更新本看板状态。
