# Day 02 — MySQL 持久化

**时间盒：180 分钟**（30 分钟学习、120 分钟编码、30 分钟验收）。**状态：DONE（2026-10-15）**。关联任务看板：`docs/05-development-board.md`。

> 环境调整（2026-10-15）：任务单原定"Docker MySQL 8 测试环境"，经确认改为**现成 MySQL 8 实例**；数据库凭证通过 `.env` 注入（密码不经过对话、不进 Git，见根目录 `.gitignore` 与 `.env.example`）。其余目标不变。

## 今日唯一目标

Docker MySQL 8 测试环境；SQLAlchemy async + asyncmy；Alembic 初始迁移；Order/Expense ORM、仓储。

## 学习要点（30 分钟）

SQLAlchemy 2、async session、ORM mapping、迁移。只学习当日任务需要的知识，不独立展开 Python 语法课程。

## 执行步骤（120 分钟）

1. 阅读 `AGENTS.md` 和相关需求/架构章节，确认任务边界。
2. 实现：Docker MySQL 8 测试环境；SQLAlchemy async + asyncmy；Alembic 初始迁移；Order/Expense ORM、仓储。
3. 为核心行为添加至少一个必要测试或可重复验证脚本。
4. 更新必要的 README、配置示例、测试命令。

## 验收（30 分钟）

- [x] 能迁移和回滚 schema；写入和查询业务表。（downgrade base → upgrade head 完整验证；2 个集成测试通过）
- [x] 代码能启动，相关测试实际运行并记录结果。（`uv run pytest`：4 passed in 2.92s）
- [x] 没有真实密钥、没有擅自扩展 MVP 范围。（密码仅存于本地 .env，未经过对话与 Git）
- [x] 在 `docs/05-development-board.md` 更新当日状态。

## 面试复盘

**主题：ORM 的事务边界**。回答：为什么采用当前方案？与熟悉的 Java 技术如何对比？有什么限制？

## 给编码 Agent 的执行指令

> 只执行 `docs/tasks/DAY-02.md`。遵循 `AGENTS.md`；先给最多五条实施步骤，再编码并运行测试。不要开始后续 Day。结束时报告完成内容、文件变更、运行命令、测试结果、阻塞项及面试总结。
