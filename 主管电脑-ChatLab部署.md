# 主管电脑部署任务

## 你的角色

你是这台电脑上的 AI 助手。请严格按下面步骤执行，每步完成后报告结果。

## 目标

在这台 Windows 电脑上安装 ChatLab，配置所有组员的 WeFlow 为远程数据源，实现自动拉取和分析工作微信聊天记录。

---

## 步骤 1：检查环境

```bash
node --version
ipconfig | findstr /i "ipv4"
```

报告 Node.js 版本和本机 IP。如果没装 Node.js，先安装 Node.js 20+。

---

## 步骤 2：安装 ChatLab

**方式 A — 桌面版（推荐）：**
用浏览器打开 https://github.com/ChatLab/ChatLab/releases，下载最新 .exe 安装包，双击安装。

**方式 B — CLI 版：**
```bash
npm install -g chatlab-cli
chatlab start
```

---

## 步骤 3：收集组员信息

你需要从每个组员那里拿到以下信息：

| 字段 | 格式示例 |
|---|---|
| 姓名 | 张三 |
| IP 地址 | 192.168.1.101 |
| 端口 | 5031 |
| Token | clb_xxxxxxxx |

先确认你已经拿到了几个组员的信息，然后继续。

---

## 步骤 4：测试组员连通性

对每个组员的地址做健康检查：
```bash
curl http://组员IP:5031/health
```

或 PowerShell：
```powershell
Invoke-WebRequest -Uri "http://组员IP:5031/health" -UseBasicParsing
```

如果返回 `{"status":"ok"}` 说明网络通。
如果超时或拒绝连接，检查：
- 组员电脑是否开机、微信是否运行、WeFlow API 是否开启
- 两台电脑是否在同一局域网（互相能 ping 通）
- 组员防火墙是否放行了 5031 端口

---

## 步骤 5：配置 ChatLab 远程数据源

1. 打开 ChatLab 桌面应用
2. 进入 Settings（设置）
3. 找到 "Data Sources" 或 "数据源" 或 "Remote Sources" 选项
4. 对每个组员，点击 "Add Data Source" 或 "添加数据源"，填写：
   - Name：组员姓名
   - URL / Base URL：`http://组员IP:端口`（如 `http://192.168.1.101:5031`）
   - Token：组员的 Token
   - Sync Interval / Pull Interval：10 分钟

如果 ChatLab 界面没有明显的"数据源"入口，尝试：
- 查看 ChatLab 安装目录下的文档
- 运行 `chatlab --help` 查看 CLI 选项
- 查看 ChatLab 官方文档：https://docs.chatlab.fun/cn/standard/chatlab-pull

---

## 步骤 6：发现并订阅会话

添加数据源后，ChatLab 会调用组员 WeFlow 的 `GET /api/v1/sessions` 接口，自动列出可用的聊天会话。

对每个组员的数据源：
1. 查看发现的会话列表
2. 勾选需要监控的会话（工作群、客户对话等）
3. ChatLab 会自动开始首次全量拉取

---

## 步骤 7：验证数据同步

检查 ChatLab 是否成功拉取数据：
```bash
# 如果用的 CLI 版
curl http://127.0.0.1:3110/api/v1/sessions -H "Authorization: Bearer 你的Token"

# 或直接查本地数据库
dir "%USERPROFILE%\.chatlab\"
```

确认能看到组员的会话和消息。

---

## 步骤 8：配置 ChatLab 自身 API（可选）

如果想让局域网内其他设备也能看分析面板：
```bash
chatlab start --host 0.0.0.0 --port 3110 --token 设置一个密码
```

然后其他电脑访问 `http://本机IP:3110`。

---

## 步骤 9：输出完成报告

```
=== 主管部署完成 ===
ChatLab 版本：[填版本号]
已添加数据源数量：[填数量]
同步间隔：10 分钟
Web 面板地址：http://localhost:3110
各数据源状态：
  - [组员名]：[连通/异常]
  - ...
```

---

## 跨网络场景

如果组员不在同一局域网，需要搭 frp 内网穿透。

### 前提条件
- 一台有公网 IP 的云服务器（阿里云/腾讯云，最低配置约 50元/月）
- 服务器的公网 IP 地址

### 在云服务器上安装 frp server
```bash
# SSH 登录服务器后
wget https://github.com/fatedier/frp/releases/download/v0.61.2/frp_0.61.2_linux_amd64.tar.gz
tar -xzf frp_0.61.2_linux_amd64.tar.gz
cd frp_0.61.2_linux_amd64

# 编辑 frps.toml
cat > frps.toml << 'EOF'
bindPort = 7000
auth.token = "设置一个强密码"
EOF

# 启动
./frps -c frps.toml
```

### 在每个组员电脑上安装 frp client
```bash
# 下载 Windows 版 frp
# https://github.com/fatedier/frp/releases
# 解压后编辑 frpc.toml
```

frpc.toml 内容（每个组员用不同 remotePort）：
```toml
serverAddr = "云服务器公网IP"
serverPort = 7000
auth.token = "设置的密码"

[[proxies]]
name = "weflow-api"
type = "tcp"
localIP = "127.0.0.1"
localPort = 5031
remotePort = 15031   # 组员1用15031，组员2用15032，以此类推
```

### 更新 ChatLab 数据源地址
组员1 原来的地址 `http://192.168.1.101:5031` 改为 `http://云服务器IP:15031`，其他组员类推。

---

## 故障排查

- **ChatLab 无法连接组员 WeFlow** → ping 组员 IP 看网络通不通；telnet 组员IP 5031 看端口通不通；检查组员防火墙
- **Pull 数据为空** → 检查组员 WeFlow 是否有聊天数据；检查 Token 是否正确；查看 ChatLab 日志
- **ChatLab 启动失败** → 检查 Node.js 版本 >= 20；尝试 `chatlab start --verbose` 看详细日志
- **下载慢** → 使用 GitHub 镜像或代理

遇到无法解决的问题，输出完整错误信息，附带 ChatLab 版本和操作系统信息。
