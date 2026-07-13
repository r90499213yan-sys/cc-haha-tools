# cc-haha ←→ QClaw 能力互认档案

> 最后更新: 2026-06-29
> 版本: v2.0 — 基于 token 优化 + 项目实战分工

---

## 核心原则：省 token、降成本

QClaw 的 token 成本远低于 cc-haha（Claude）。高 token 消耗的机械性任务 → 优先 QClaw；需要上下文深度、判断力、风格一致性的任务 → cc-haha。

---

## cc-haha 的能力

- **代码与架构**：写代码、debug、架构设计
- **版本控制**：Git 仓库管理、版本控制
- **本地文件系统**：文件编辑与项目管理
- **Shell 与环境**：Shell 命令执行、环境配置
- **内容创作工作流**：cheat-on-content（选题/打分/预测/复盘/rubric 升级）
- **视频脚本**：视频脚本分析与迭代优化（依据 audience.md / script_patterns.md / rubric_notes.md）
- **桥接通信**：本地 AI Bridge + QClaw 桥接通信

## cc-haha 不擅长的领域

- 网页搜索、社交媒体抓取、外网 API 调用、YouTube 内容获取

---

## QClaw 的能力

### 信息获取
- **网页搜索**：多引擎网页搜索（Google CSE, Wikipedia, Reddit 等）
- **网页抓取**：任意 URL 内容提取与阅读
- **Twitter/X 抓取**：推文搜索、AI KOL 动态监控、社交数据分析
- **YouTube**：视频搜索、字幕提取、频道浏览、视频内容总结
- **金融数据**：股票/基金/指数/财报/研报自然语言查询

### 文档处理
- **PDF**：读取、合并、拆分、加密、OCR、表单填写
- **Word (.docx)**：创建、编辑、格式化、批注、查找替换
- **Excel (.xlsx/.csv)**：创建、编辑、公式、图表、数据清洗
- **腾讯文档**：在线智能文档/表格/思维导图/流程图/知识库管理

### 生产与创作
- **长文写作**：书籍/手册/白皮书全流程写作
- **合同处理**：合同起草、审查、对比、法条检索（腾讯电子签）
- **PPT 生成**：本地生成 .pptx 文件

### 通信与自动化
- **邮件**：IMAP/SMTP 邮箱收发
- **浏览器自动化**：真实 Chrome/Edge 操控，登录态复用
- **定时任务**：cron 提醒、周期执行、闹钟
- **云上传备份**：腾讯云 SMH 文件上传备份

### 平台集成
- **企业微信 SCRM**：客户管理、标签、群发（微盛企微管家）
- **美团旅行**：酒店/机票/门票/度假查询与预订

---

## 小林颈腰椎康复-抖音项目·实战分工

### 选题阶段

| 步骤 | 谁做 | 原因 |
|------|------|------|
| 搜当日热点、对标账号新视频 | **QClaw** | 纯搜索，token 量大，QClaw 强项 |
| brainstorm 选题建议 | **cc-haha** | 需要 audience.md + 历史 context + 风格判断 |
| 选题草稿 scoring | **cc-haha** | rubric 绑定本地校准池，QClaw 没上下文 |

### 脚本阶段

| 步骤 | 谁做 | 原因 |
|------|------|------|
| 脚本写作 | **cc-haha** | 需 audience.md / script_patterns.md / 对标风格 |
| rubric 打分 | **cc-haha** | 本地 rubric_notes.md + 盲预测约束 |
| 预测日志 | **cc-haha** | immutable 预测，hook 保护 |

### 发布后

| 步骤 | 谁做 | 原因 |
|------|------|------|
| 视频字幕转录 | **QClaw** | YouTube 字幕 API，token 消耗极高 |
| 抖音后台数据抓取 | **QClaw** | 浏览器自动化，打开后台截数据 |
| 定量数据整理 | **QClaw** | 播放/点赞/评论/转发 → 结构化表格 |
| 复盘定性分析 | **cc-haha** | 需 rubric 偏差分析 + pattern 识别 |
| 复盘报告 writing | **cc-haha** | 风格一致性 + rubric-memo 更新 |

### 通用/其他

| 步骤 | 谁做 | 原因 |
|------|------|------|
| 对标账号数据导入 | **QClaw 为主** | 网页抓取视频列表、播放数据 |
| 对标数据解读 | **cc-haha** | 需 rubric 框架 + 竞品策略分析 |
| rubric 升级 | **cc-haha** | 全量重打分 + 跨模型审 |
| 话题趋势监控 | **QClaw** | 定时搜索 + RSS |
| 外部资讯简报 | **QClaw** | 已部署定时任务（新闻资讯项目） |

---

## 不可交给 QClaw 的任务（硬边界）

1. **脚本正文写作** — QClaw 没有 audience.md / script_patterns.md 上下文，产出风格不对
2. **rubric 评分与预测** — 校准池、盲预测约束绑定本地，不能外移
3. **复盘定性分析** — 需要理解 rubric 偏差模式，QClaw 做不到
4. **rubric 升级** — 全量重打 + 跨模型独立审，必须 cc-haha 执行
5. **Git 操作** — 代码版本管理

---

## 协作流程

```
cc-haha 需要外网信息
  → POST /api/tell-qclaw（cc-gateway:48763 → QClaw:55821）
  → QClaw 搜索/抓取 → 结果写共享文件
  → cc-haha 读结果继续

QClaw 需要 cc-haha 能力（罕见）
  → 写 cc-inbox.md
  → cc-haha 处理 → 结果写文件
```

---

## 互认签名

- **cc-haha**: 已确认 v2.0 分工
- **QClaw**: 见 cc-inbox.md PENDING（待确认 v2.0）

> 能力变更或分工调整需双方确认后更新此档案。
