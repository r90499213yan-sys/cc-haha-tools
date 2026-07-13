# AI 工具协作桥 — 即时 Push 方案

## 架构

```
cc-haha → cc-gateway:48763 → POST http://127.0.0.1:<auto>/v1/chat/completions → QClaw 立即干活 ✅
                                                    ↑
                                          cc-gateway 自动探测 QClaw 端口
```

**QClaw 每次重启端口会变，cc-gateway 已升级为自动探测，无需手动改配置。**

## QClaw 端口自动探测

cc-gateway 启动时自动完成：
1. 尝试默认端口（环境变量 `QCLAW_PORT` 或 19000）
2. 失败则扫描 QClaw 进程的 LISTENING 端口
3. 逐个测 `/health`，找到真正的 API 端口
4. 缓存 30 秒，过期重新探测

## API 端点

### QClaw 入站端点

- **地址**：`http://127.0.0.1:<QClaw当前端口>/v1/chat/completions`
- **方法**：POST
- **认证**：`Authorization: Bearer <token>`（token 在 `D:\claude code项目文件\cc-gateway\qclaw-token.txt`）
- **格式**：OpenAI Chat Completions

### cc-gateway 管理端点

| 端点 | 用途 |
|------|------|
| `GET /health` | cc-gateway 自身健康检查 |
| `POST /api/chat` | 调 cc-haha CLI 处理 prompt |
| `POST /api/tell-qclaw` | 即时 Push 消息给 QClaw |
| `GET /api/qclaw-status` | 查看 QClaw 连通状态和当前端口 |

## cc-haha 调用示例

### 通过 cc-gateway Push 给 QClaw（推荐）

```bash
curl -sS http://127.0.0.1:48763/api/tell-qclaw \
  -H "Authorization: Bearer $(cat D:/claude code项目文件/cc-gateway/cc-token.txt)" \
  -H "Content-Type: application/json" \
  -d '{"message":"帮我查一下钉钉登录接口的文档，结果写到 D:\\workspace\\dingtalk-api.md"}'
```

### 直连 QClaw（手动模式）

```bash
# 先查 QClaw 当前端口
curl -sS http://127.0.0.1:48763/api/qclaw-status \
  -H "Authorization: Bearer $(cat D:/claude code项目文件/cc-gateway/cc-token.txt)"

# 用返回的端口直连
curl -sS --noproxy "*" http://127.0.0.1:<端口>/v1/chat/completions \
  -H "Authorization: Bearer $(cat D:/claude code项目文件/cc-gateway/qclaw-token.txt)" \
  -H "Content-Type: application/json" \
  -d @/tmp/request.json
```

> **注意**：直连 QClaw 时必须加 `--noproxy "*"`（代理会拦截 localhost），且中文建议通过文件 `-d @file` 传参避免 shell 编码问题。

### 保持会话（多次请求共享上下文）

加 `"user":"cc-haha-conversation-1"` → 同个 user id 共享上下文（稳定 session），不加 → 每次独立无状态。

## 分工模式

| 谁 | 做什么 |
|----|--------|
| cc-haha | 写代码、debug、架构设计、git 管理 |
| QClaw | 搜资料、读写文件、生成报告/文档、发通知、自动化 |
| 你 | 验收、决策 |

## 调用链路总结

```
cc-haha 需要 QClaw 帮忙
  → POST /api/tell-qclaw（cc-gateway 自动找 QClaw 端口）
  → QClaw 收到消息 → 执行任务 → 写文件
  → cc-haha 读结果继续干活
```

**端口自动探测 + 即时 Push。不再写死端口号。**
