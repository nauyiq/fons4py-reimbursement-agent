# 验收测试与 Demo 脚本

## 核心自动化测试（至少 5 条）

- [ ] T01：日常报销 200 元，无差旅单，草稿成功创建，状态 DRAFT。
- [ ] T02：差旅报销交通 560 + 住宿 800，总金额 Decimal('1360.00')。
- [ ] T03：缺金额/日期时 Agent 询问，不虚构数据、不写入错误草稿。
- [ ] T04：用户未确认或版本变动时，提交失败，订单仍为 DRAFT。
- [ ] T05：同一幂等键重试创建/提交，只产生一次业务效果。
- [ ] T06：SUBMITTED/CANCELLED 单据拒绝费用编辑。
- [ ] T07：LangGraph 单进程 interrupt/resume 成功；中断恢复不重复创建。
- [ ] T08：标准 A2A Client 可请求 Python Agent。
- [ ] T09：Java fons4ai-trip 可调用 Python Agent（若 Java SDK 兼容）。

## 5 分钟面试演示

1. 展示两个仓库与架构图：Java 主编排 + Python 报销领域 Agent。
2. 启动 MySQL、FastAPI/A2A Server，展示 `/health`。
3. 提问：`帮我报销昨天买的办公用品 200 元`；返回 DRAFT。
4. 展示 MySQL 报销单/费用明细数据。
5. 让用户确认；演示提交后状态 SUBMITTED；尝试重复提交或篡改金额被拒绝。
6. 用 Java fons4ai-trip 进行 A2A 请求并展示 Python 结果；若 Java 集成还未完成，则展示标准 A2A Client 联调，同时注明限制。

## 每日完成定义 DoD

- 代码能启动/导入；关键路径测试通过。
- 文档与实现一致；没有真实密钥、业务敏感数据。
- 每天可解释 1 个 Python 知识点和 1 个 Agent 面试知识点。
- 若未完成，明确记录阻塞原因，先缩小范围而不突破 3 小时上限。

## 范围之外

发票 OCR、影像上传、MinIO、Redis、审批、支付、分布式运行、生产级认证与观测不作为本版验收要求。
