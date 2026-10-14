# AGENTS.md — AI 编码 Agent 工作契约

> 本文档是给 AI 编码 Agent 的开发契约：项目目标、红线约束、开发规划入口与执行规程。
> 项目业务与系统设计概览见 [README.md](README.md)；细节文档见 [docs/](docs/)。

## 1. 项目目标与成功标准

按 `docs/05-development-board.md` 和 `docs/tasks/DAY-XX.md` 实施一个**最小可演示的 Python 报销 Agent**。

- **开发目标**：10 个开发日交付 M1（自然语言创建报销草稿）+ M2（确认提交 + A2A 接入 Java fons4ai-trip）。
- **学习目标**：开发者从 0 学习 Python 与 Agent 技术栈；每天可解释 1 个 Python 知识点和 1 个 Agent 面试知识点（见各日任务单"面试复盘"）。
- **验收标准**：`docs/06-testing-and-demo.md` 的核心测试矩阵（T01–T09）与 5 分钟演示脚本。

## 2. 必读文档与顺序

1. `README.md` —— 建立业务与系统全貌
2. `docs/05-development-board.md` —— 开发看板、里程碑、阻塞升级原则
3. 当日任务单 `docs/tasks/DAY-XX.md` —— 唯一执行范围

`docs/01`–`04` 为需求/架构/领域/工作流细节，涉及时按需查阅；不要一次性全量重读。

## 3. 开发规划入口

- 规划本体在 `docs/05-development-board.md`（10 天看板、M1/M2 里程碑、阻塞升级原则）。
- **每次只执行用户指定的 Day / Issue，不自动开始下一天。**
- 每日时间盒：30 分钟学习 + 120 分钟开发 + 30 分钟验收复盘；超时缩小范围并如实记录，不顺延红线。
- 开发节奏：从业务服务到 Agent，再到 A2A；严禁第一天就做完整生产体系。
- 验收通过后更新看板当日状态。

## 4. 严格约束（红线）

- 若需要增加范围、库或表，先说明原因，不要擅自扩展；变更需求先修改文档再改代码。
- 技术栈锁定：Python、FastAPI、Pydantic v2、SQLAlchemy 2.x、Alembic、MySQL 8、LangChain、LangGraph、官方 A2A SDK；依赖版本通过本次环境验证锁定（以 `uv.lock` 为准）。
- 一期只有 `reimbursement_order` 和 `reimbursement_expense` 两张核心业务表；为确认授权、幂等可引入最小额外表或唯一约束，但要先在设计文档解释。
- Money 用 `Decimal`；禁止 float。数据库业务变更必须走 application 服务并使用事务。
- `DRAFT` 可修改；`SUBMITTED` 和 `CANCELLED` 不可修改；正式提交需真实用户确认，不接受由 LLM 自己设置的 `confirmed=true`。
- 对创建、提交等副作用做幂等；LangGraph 中断节点重放时不得重复写库。
- 对外部差旅单查询可以先 Mock。不要改动 Java 业务数据库；A2A 负责 Agent 任务委派，不代替普通业务 API。
- 仅为理解和流程调用使用 LLM；规则判断和金额计算写确定性业务代码。
- 不添加 OCR、MinIO、Redis、Kafka、审批工作流、真实支付、复杂角色管理、前端页面、微服务拆分等未列入 MVP 的内容。

## 5. 代码分层约定

`api/`（FastAPI DTO）→ `application/`（Use Case）→ `domain/`（纯业务）→ `infrastructure/`（ORM/数据库）；`agents/`、`graph/` 和 `a2a/` 调用 application，不直接读写数据库。

REST API、A2A 适配与 Agent 工具共享同一套 application use cases；任何入口都不允许直接操作 ORM。

## 6. 工程原则

- **先理解，再执行**：需求不清楚先澄清；不盲目相信用户的技术判断。
- **借鉴 SDD，而非强制 SDD**：需求分析、方案设计、任务规划是思考步骤，不一定产出文档。
- **按复杂度决定流程**：简单任务直接处理；复杂任务先设计后实现；长线任务分阶段交付。
- **尊重现有工程体系**：优先复用项目已有的框架、组件、抽象、异常体系和编码约定，不另起炉灶。
- **代码为人而写**：可读性、合理抽象、业务注释和长期可维护性都是代码质量的一部分。
- **结果必须可验证**：实现后验证行为符合需求，而不只是代码能运行。

## 7. 每日执行规程

1. 读取当日任务与 DoD，给出不超过 5 条实现步骤。
2. 在有限范围内实现代码、单测和配置；修改文档中有关假设。
3. 运行相关测试和格式检查；如环境不完整则明确列出未验证项。
4. 输出：**完成内容 / 运行命令 / 测试结果 / 文件变更 / 阻塞项 / 次日建议**。
5. 不宣称未运行的测试已通过；不得提交或记录真实密钥。

## 8. 技术注意事项

- `async def` 不得调用阻塞 I/O，SQLAlchemy AsyncSession 生命周期按请求/任务管理。
- 长事务不要跨 LLM 调用或 A2A 等待。
- Checkpointer State 与 MySQL 业务状态相互独立，`thread_id`、`task_id`、`order_id` 应能够关联但不强制相等。
- 业务 API 的调用者身份来自认证上下文，而非信任模型生成的 applicant_id。
- 如集成 SDK 变化，先查看官方示例并用最小独立示例验证接口，不大量猜测 API。

## 9. 风险与升级

- Java 仓库 fons4ai-trip 的 A2A API 未核验：Day 8 必须先检查兼容性；不兼容时不推倒已完成模块，按看板"阻塞升级原则"以标准 A2A Client 完成协议验收兜底。
- SDK API 与教程不一致：以官方示例 + 最小独立验证为准，不猜测。
- 任一红线（提交授权、金额精度、副作用幂等）与进度冲突时，**进度让位**。
