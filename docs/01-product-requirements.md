# 产品需求 PRD — MVP V1

## 目标用户与使用方式

员工通过聊天表达报销需求。M1 直接访问 Python API；M2 由 Java fons4ai-trip 主 Agent 通过 A2A 委派。Python 报销系统独立保存报销单；无须差旅单也可创建日常报销。

## 核心场景

1. 日常：`报销办公用品 200 元，昨天购买` → Agent 创建 DRAFT → 展示草稿 → 用户明确确认 → SUBMITTED。
2. 差旅：`关联差旅单 T001，报销高铁票 560 元和住宿 800 元` → 差旅单查询（MVP 可 Mock）→ DRAFT → 确认提交。
3. 信息不全：`报销交通费` → 追问金额/日期等必填信息，不杜撰。
4. 用户修改：`住宿费改成 750 元` → 修改草稿并重新计算 → 原确认信息失效。
5. 重试：A2A/HTTP 重放同一个操作，不得创建重复单据或提交两次。

## 需求清单

| ID | 要求 | 优先级 | 截止 |
|---|---|---|---|
| F01 | TRAVEL / DAILY 类型 | P0 | M1 |
| F02 | 差旅单可选引用（MVP Mock 读取） | P0 | M1 |
| F03 | 草稿创建、查询、添加/修改费用 | P0 | M1 |
| F04 | Decimal 金额汇总与基本校验 | P0 | M1 |
| F05 | Agent 自然语言创建草稿 | P0 | M1 |
| F06 | 正式提交必须用户确认 | P0 | M2 |
| F07 | LangGraph 暂停与恢复 | P0 | M2（本地） |
| F08 | Python A2A Server | P0 | M2 |
| F09 | Java A2A Client 联调 | P0 | M2（若 Java 兼容） |
| F10 | 基础幂等与测试 | P0 | M2 |
| F11 | Docker 启动与 README 演示 | P1 | M2 |

## 业务边界

- 报销单属于 Python；差旅单属于 Java。只保存 trip_source/trip_id/trip_no 引用，不复制完整差旅域。
- 默认人民币 CNY，金额精度 2 位；不做多币种转换。
- 费用类型：TRANSPORT、HOTEL、MEAL、LOCAL_TRANSPORT、OFFICE_SUPPLIES、ENTERTAINMENT、COMMUNICATION、OTHER。
- V1 不做真实附件上传、OCR、验真、税务处理、预算、审批、财务打款、报销重复票据识别。
- 提交意味着「进入已提交状态」，不等于审批通过或支付完成。

## 未决细节（开发默认值）

- 用户身份：MVP 使用受控开发环境的固定测试身份；生产必须接入鉴权，严禁让模型决定用户 ID。
- 差旅查询：先 Mock；联调 Java 侧有现成受控 API 才替换。
- 时间：数据库保存 UTC 时间，API 按明确时区展示；不以宿主机本地时区作为隐式业务规则。
- 规则：只验证正金额、费用类型合法、草稿至少一条费用；公司报销制度留扩展接口。

## 验收

完成 `docs/06-testing-and-demo.md` 的核心测试；在未确认时不能提交，确认后可提交；从 Java 主 Agent 可以调用 Python A2A Agent 完成至少一次报销草稿任务。
