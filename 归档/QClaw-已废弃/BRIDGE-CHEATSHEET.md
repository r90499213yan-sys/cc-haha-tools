# cc-haha ↔ QClaw 双向桥接 API 速查卡

> 最后更新: 2026-07-01

---

## 端口地图

```
cc-haha 内置服务器 : 3456  (Electron 桌面 App 启动即运行)
cc-gateway 桥接器  : 48763 (需手动/开机启动)
QClaw API          : 55821 (QClaw 进程启动即运行，可自动探测)
```

---

## cc-haha → QClaw (直接调 API)

```bash
curl -X POST http://127.0.0.1:55821/v1/chat/completions \
  -H "Authorization: Bearer 232b3217de879cfda96f2ae5f6ffdbcc018c7370d20bb696" \
  -H "Content-Type: application/json" \
  -d '{"model":"openclaw","messages":[{"role":"user","content":"你的任务"}]}'
```

## cc-haha → QClaw (流式同步 — 默认，实时看回复)

```bash
curl -X POST http://127.0.0.1:48763/api/tell-qclaw \
  -H "Authorization: Bearer cc-d956dc35a81d37ae2919c7e3698cd81c4dd245e95be43eef713211b7c26d0705" \
  -H "Content-Type: application/json" \
  -d '{"message":"你的任务"}'
# 返回 SSE 流式文本，QClaw 实时逐字输出
# 可选: "timeout": 60000 (60秒超时), "timeout": 0 (不限时，默认)
```

## cc-haha → QClaw (异步 fire-and-forget — 不等待结果)

```bash
curl -X POST http://127.0.0.1:48763/api/tell-qclaw \
  -H "Authorization: Bearer cc-d956dc35a81d37ae2919c7e3698cd81c4dd245e95be43eef713211b7c26d0705" \
  -H "Content-Type: application/json" \
  -d '{"message":"你的任务","async":true}'
# 立即返回 {ok:true}，不等 QClaw
```

## QClaw → cc-haha (通过 gateway)

```bash
curl -X POST http://127.0.0.1:48763/api/chat \
  -H "Authorization: Bearer cc-d956dc35a81d37ae2919c7e3698cd81c4dd245e95be43eef713211b7c26d0705" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"你的完整任务描述"}'
```

---

## 健康检查

```bash
curl http://127.0.0.1:48763/health         # cc-gateway
curl http://127.0.0.1:55821/health         # QClaw
curl http://127.0.0.1:3456/health          # cc-haha (桌面App运行时)
```

---

## 文件信箱（备用通道）

- QClaw → cc-haha: `D:\AI_Bridge\cc-inbox.md`
- cc-haha → QClaw: `D:\AI_Bridge\qclaw-inbox.md`

---

## 相关文件

| 文件 | 用途 |
|------|------|
| `D:\claude code项目文件\cc-gateway\ABILITY-MAP.md` | 能力分工清单（两边都读） |
| `D:\claude code项目文件\cc-gateway\QCLAW_COLLAB.md` | QClaw 协作章程（给 QClaw 看） |
| `D:\claude code项目文件\cc-gateway\start-gateway.bat` | 开机自启脚本 |
