# Day 02 — MySQL 持久化

**时间盒：180 分钟**（30 分钟学习、120 分钟编码、30 分钟验收）。**状态：TODO**。关联任务看板：`docs/05-development-board.md`。

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

- [ ] 能迁移和回滚 schema；写入和查询业务表。
- [ ] 代码能启动，相关测试实际运行并记录结果。
- [ ] 没有真实密钥、没有擅自扩展 MVP 范围。
- [ ] 在 `docs/05-development-board.md` 更新当日状态。

## 面试复盘

**主题：ORM 的事务边界**。回答：为什么采用当前方案？与熟悉的 Java 技术如何对比？有什么限制？

## 给编码 Agent 的执行指令

> 只执行 `docs/tasks/DAY-02.md`。遵循 `AGENTS.md`；先给最多五条实施步骤，再编码并运行测试。不要开始后续 Day。结束时报告完成内容、文件变更、运行命令、测试结果、阻塞项及面试总结。
