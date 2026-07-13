═══════════════════════════════════════════
  Claude Code HTTP Gateway 使用说明
═══════════════════════════════════════════

## 文件清单

  cc-gateway.js         ← 主程序（Node.js，纯内置模块，零依赖）
  cc-token.txt          ← Bearer Token（自动生成，可手动改）
  cc-gateway-readme.txt ← 本说明

## 启动方式

  node cc-gateway.js

  启动后输出：
    Port:    48763
    Token:   cc-d956dc...  ← 前 12 位
    Claude:  available     ← CLI 连通状态
    URL:     http://127.0.0.1:48763

## 环境变量

  CC_PORT   = 端口号（默认 48763）
  CC_TOKEN  = 自定义 Token（不设则从 cc-token.txt 读取或自动生成）
  CC_TIMEOUT= 超时毫秒（默认 300000 = 5 分钟）
  CC_DEBUG  = 设为 1 打印 spawn 命令（调试用）

## 接口

### GET /health
  无需 Token，查看服务状态
  返回：{"status":"ok","claude":"available","timestamp":"..."}

### POST /api/chat
  需要 Bearer Token
  Header: Authorization: Bearer <token>
  Header: Content-Type: application/json
  Body:   {"prompt":"你的问题"}

  返回：{"response":"Claude Code 的回复"}


## 开机自启

  Windows:
    1. 创建 cc-gateway.vbs，内容：
       CreateObject("WScript.Shell").Run "node D:\claude code项目文件\cc-gateway\cc-gateway.js", 0, False
    2. Win+R → shell:startup → 把 .vbs 放进去
    3. 下次开机自动以最小化方式启动

  命令行方式：
    start /min node D:\claude code项目文件\cc-gateway\cc-gateway.js
    加入 shell:startup 目录

## 架构说明

        ↑ 纯文本 HTTP           ↑ Node.js 中转        ↑ 直接调 sidecar.exe
                                                           无状态，每次新进程

## 安全提示

  - 默认绑定 127.0.0.1，仅本机可访问
  - Bearer Token 认证所有 /api/chat 请求
  - 如需跨机器访问，配合 Tailscale/ZeroTier 组网 + 防火墙规则
  - 不建议直接暴露到公网
