# ChatLab + WeFlow 团队微信聊天记录远程分析方案

## 背景

目标：组员电脑安装 WeFlow（解密微信 + 暴露 API），主管电脑安装 ChatLab（自动拉取 + 分析面板），主管实时/定时查看所有组员的工作微信聊天记录。

## 核心原理

ChatLab 内置了两套数据接入机制：

| 机制 | 方向 | 用途 |
|---|---|---|
| **Pull 远程数据源** | ChatLab 主动去拉 | 自动发现会话、定时增量同步 |
| **Push 导入协议** | 外部工具推给 ChatLab | 一次性导入、脚本批量导入 |

我们主要用 **Pull 协议**——主管的 ChatLab 自动从组员的 WeFlow 拉取数据，定时更新。

---

## 工具分工

| 工具 | 装在哪 | 角色 | 暴露的接口 |
|---|---|---|---|
| **WeFlow** | 每台组员电脑 | 解密微信，开放 HTTP API | `http://组员IP:5031` |
| **ChatLab** | 主管电脑 | 远程数据源管理、自动拉取、AI分析、Web面板 | `http://主管IP:3110` |

---

## 第一步：组员电脑安装 WeFlow

### 下载安装
- GitHub Releases：https://github.com/hicccc77/WeFlow/releases
- 官网：https://weflow.top
- 下载最新版 Windows exe，双击安装

### 配置 API 服务
1. 打开 WeFlow，确认微信已登录（必须是工作微信）
2. WeFlow 会自动加载微信聊天数据
3. 进入 **设置 → API 服务 → 开启 API 服务**
4. 默认端口 **5031**，记下 Token
5. **关键**：检查设置里能否把监听地址从 `127.0.0.1` 改成 `0.0.0.0`（允许局域网其他电脑访问）

### WeFlow API 关键端点（ChatLab Pull 协议兼容）

| 端点 | 用途 |
|---|---|
| `GET /api/v1/sessions` | 列出所有聊天会话 |
| `GET /api/v1/sessions/:id/messages` | 拉取指定会话的消息（ChatLab Pull 格式） |
| `GET /api/v1/health` | 健康检查 |

---

## 第二步：主管电脑安装 ChatLab

### 安装
- GitHub Releases：https://github.com/ChatLab/ChatLab/releases
- 官网：https://chatlab.fun/cn/
- 下载最新版 Windows 安装包，双击安装

或者用 CLI：
```bash
npm install -g chatlab-cli
chatlab start
```

### ChatLab 的关键能力

- **数据源管理**：在设置里添加远程 WeFlow 实例，ChatLab 自动发现上面的会话
- **Pull 引擎**：自动分页拉取全量历史 + 增量新消息
- **定时调度**：设置同步间隔（如每 10 分钟一次）
- **去重机制**：同一消息不会重复写入，断网重连不会丢数据
- **SSE 实时通知**（WeFlow 需支持）：新消息到达秒级触发拉取
- **Web 面板**：趋势图、时间分布、成员排行、词云
- **SQL 查询**：深度筛选数据（如"张三上周提到合同的次数"）
- **AI 分析**：24+ Function Calling 工具，自然语言提问
- **MCP Server**：接 Claude Code/Cursor/Codex 等 AI 助手

---

## 第三步：配置远程数据源（关键步骤）

### 同局域网场景（所有电脑在同一办公室）

主管在 ChatLab 设置里添加每个组员的 WeFlow：

```
数据源1：http://192.168.1.101:5031  Token: xxx
数据源2：http://192.168.1.102:5031  Token: xxx
...
数据源10：http://192.168.1.110:5031  Token: xxx
```

ChatLab 自动执行：
1. 调用每个数据源的 `GET /sessions` → 发现所有可用会话
2. 主管勾选要监控的会话 → ChatLab 开始全量拉取历史数据
3. 之后定时增量拉取新消息（如每 10 分钟）
4. 去重、增量、断点续传全部自动处理

### 跨网络场景（组员分散在不同地方）

原理相同，但需要让主管电脑能访问到组员的 WeFlow API。

**推荐方案：frp 内网穿透（国人开发，GitHub 9万星，不需要谷歌）**

```
架构：
┌─────────────────────────────────────┐
│   一台国内云服务器（阿里云/腾讯云）       │
│   安装 frp server（frps）             │
│   公网IP: 1.2.3.4                    │
└─────────────────────────────────────┘
         ↑                    ↑
    frp 隧道              frp 隧道
   ┌────┴────┐        ┌───┴────┐
   │ 组员1    │        │ 组员10  │
   │ frpc    │  ...   │ frpc   │
   │ WeFlow  │        │ WeFlow │
   │ :5031   │        │ :5031  │
   └─────────┘        └────────┘
         ↓                    ↓
   映射为：              映射为：
   1.2.3.4:15031        1.2.3.4:25031

主管 ChatLab 配置：
数据源1：http://1.2.3.4:15031  Token: xxx
...
数据源10：http://1.2.3.4:25031  Token: xxx
```

frp 免费开源，只需一台国内云服务器（最便宜配置约 50元/月），一次性配置。

另一个备选：**ZeroTier**（免费虚拟局域网，邮箱注册，无需谷歌），但国内偶有不稳定。

---

## 第四步：使用 ChatLab 分析

### Web 面板
打开 `http://localhost:3110`（或主管电脑IP:3110），可以看到：
- 所有组员的聊天会话列表
- 数据可视化：活跃趋势、时间分布、成员排行
- 全局搜索：跨所有会话搜索关键词

### SQL 深度分析
```sql
-- 查某个人发了多少消息
SELECT sender_id, COUNT(*) as count 
FROM message 
GROUP BY sender_id 
ORDER BY count DESC

-- 查看数据库结构
SELECT * FROM sqlite_master WHERE type='table'
```

### MCP Server（接 AI 助手）
```bash
npx -y chatlab-mcp
```

Claude Code 配置（`.mcp.json`）：
```json
{
  "mcpServers": {
    "chatlab": {
      "command": "npx",
      "args": ["-y", "chatlab-mcp"]
    }
  }
}
```

---

## 第五步：定时同步配置

ChatLab Pull 协议支持的同步策略：

| 模式 | 说明 |
|---|---|
| **全量同步** | 首次拉取，`since=0`，ChatLab 自动分页拉完所有历史 |
| **增量同步** | 之后每次只拉 `since=上次时间戳` 之后的新消息 |
| **定时拉取** | 在 ChatLab 设置同步间隔（建议 5-10 分钟） |
| **SSE 实时推送** | 如果 WeFlow 支持 SSE，新消息到达秒级通知 ChatLab |

增量同步的去重由 ChatLab 自动处理，同一消息不会重复写入。

---

## WeFlow 导出格式支持（补充方案）

ChatLab 代码里内置了以下 WeChat 相关工具的解析器：

| 解析器文件 | 支持的工具 |
|---|---|
| `weflow.ts` | WeFlow 导出格式 |
| `ycccccccy-echotrace.ts` | echotrace 导出格式 |

如果 Pull 协议用不了，可以用文件模式兜底：
1. WeFlow 导出聊天记录 → 得到 WeFlow 格式文件
2. 拖入 ChatLab → 自动识别并导入
3. 适合一次性批量导入历史数据

---

## 支持的平台标识

ChatLab Format 的 `platform` 字段支持：`wechat`、`qq`、`telegram`、`discord`、`whatsapp`、`line`、`slack`。WeFlow 导出的微信数据会被 ChatLab 的 WeFlow 解析器自动映射为正确的 ChatLab 格式。

---

## 注意事项

1. **法律合规**：必须先获得组员知情同意，只监控工作微信，不碰个人微信
2. **数据安全**：如涉及跨公网传输，务必启用 Token 鉴权 + frp 加密隧道
3. **微信版本**：WeFlow 支持微信 4.0 及以上版本
4. **ChatLab 的微信支持是隐式的**：官方为规避风险不写"支持微信"，但代码里内置了 WeFlow 和 echotrace 解析器
5. **WeFlow API 监听地址**：默认 `127.0.0.1`（仅本机），需要在设置里改为 `0.0.0.0` 才能被其他电脑访问

---

## 如果遇到问题

- WeFlow 文档：https://github.com/hicccc77/WeFlow 的 docs/ 目录
- ChatLab 文档：https://docs.chatlab.fun/cn/
- ChatLab API 文档：https://docs.chatlab.fun/cn/standard/chatlab-api
- ChatLab Pull 协议：https://docs.chatlab.fun/cn/standard/chatlab-pull
- ChatLab 导入协议：https://docs.chatlab.fun/cn/standard/chatlab-import

---

## 给公司电脑 AI 的执行指令

> 你现在是一台公司电脑的技术助手。请按以下步骤执行：
>
> **第一步：判断角色**
> - 如果这台电脑是组员用的 → 执行「组员部署」
> - 如果这台电脑是主管用的 → 执行「主管部署」
> - 如果不确定，先问我
>
> **组员部署：**
> 1. 从 https://github.com/hicccc77/WeFlow/releases 下载最新 Windows 安装包
> 2. 安装 WeFlow
> 3. 打开 WeFlow，确认微信已登录
> 4. 进入设置 → API 服务 → 开启，记下端口（默认5031）和 Token
> 5. 尝试把 API 监听地址从 127.0.0.1 改为 0.0.0.0（让局域网其他电脑能访问）
> 6. 告诉我这台电脑的局域网 IP 地址（用 ipconfig 查看）
> 7. 把 IP、端口、Token 发给主管
>
> **主管部署：**
> 1. 从 https://github.com/ChatLab/ChatLab/releases 下载最新 Windows 安装包
> 2. 安装 ChatLab
> 3. 打开 ChatLab，进入设置 → 找到"远程数据源"或"数据源管理"
> 4. 添加组员的 WeFlow 地址作为数据源（格式：http://组员IP:5031，Token 填组员给的）
> 5. 设置同步间隔（建议 10 分钟）
> 6. ChatLab 自动发现组员 WeFlow 上的会话，勾选要监控的会话
> 7. 等待首次全量同步完成
> 8. 打开 Web 面板查看分析结果（http://localhost:3110）
>
> **每完成一步，告诉我结果。遇到任何问题，把错误信息发给我。**
