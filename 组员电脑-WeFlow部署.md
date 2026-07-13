# 组员电脑部署任务

## 你的角色

你是这台电脑上的 AI 助手。请严格按下面步骤执行，每步完成后报告结果。

## 目标

在这台 Windows 电脑上安装 WeFlow，开启 HTTP API，让主管电脑能远程访问本机工作微信聊天数据。

---

## 步骤 1：检查环境

执行以下检查：
```bash
# 检查 Node.js 是否已安装
node --version

# 检查微信是否正在运行
tasklist | findstr /i "wechat"

# 获取本机局域网 IP
ipconfig | findstr /i "ipv4"
```

报告：
- Node.js 版本（如果没装需要先装）
- 微信是否在运行
- 本机 IP 地址

---

## 步骤 2：安装 WeFlow

```bash
# 方法1：从 GitHub 下载安装包
# 用浏览器打开 https://github.com/hicccc77/WeFlow/releases
# 下载最新的 .exe 安装包

# 方法2：如果电脑有 winget
winget install WeFlow
```

如果安装包下载慢，尝试用镜像或检查代理设置。

---

## 步骤 3：配置 WeFlow API

1. 启动 WeFlow 桌面应用
2. 确认微信已登录且 WeFlow 能读取到聊天数据
3. 进入 WeFlow 的设置界面
4. 找到"API 服务"选项，开启
5. 记录端口号（默认 5031）和 Token
6. 查找是否有"监听地址"或"绑定地址"配置项，如果有，从 `127.0.0.1` 改为 `0.0.0.0`

如果不确定怎么操作设置界面，查看：
- WeFlow 目录下的 `docs/` 文件夹
- 或运行 `dir "C:\Program Files\WeFlow\docs"` 查看本地文档

---

## 步骤 4：验证 API 可用

在本机测试 API 是否正常：
```bash
curl http://127.0.0.1:5031/health
```

或者用 PowerShell：
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5031/health" -UseBasicParsing
```

如果返回 `{"status":"ok"}` 则成功。

---

## 步骤 5：输出最终信息

完成以上步骤后，输出以下信息（发给主管）：

```
=== 组员部署完成 ===
姓名：[填组员姓名]
IP 地址：[填步骤1获取的IPv4地址]
端口：5031
Token：[填步骤3获取的Token]
状态：API 已验证可用
```

---

## 故障排查

- WeFlow 启动报错 → 检查微信版本是否 >= 4.0，检查 Node.js 版本
- API 无法访问 → 检查防火墙是否拦截了 5031 端口，运行 `netsh advfirewall firewall add rule name="WeFlow API" dir=in action=allow protocol=TCP localport=5031`
- 下载慢 → 尝试使用 GitHub 镜像或代理

遇到无法解决的问题，输出完整错误信息。
