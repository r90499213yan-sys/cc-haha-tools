# QClaw 抖音数据抓取 — 操作指南

> 更新：2026-07-01 | 三次实测优化

---

## cc-haha 执行清单（每次照做）

### 场景A：抓账号主页 + 10个视频数据

```
1. 用户给短链接（如 https://v.douyin.com/xxxxx/）
2. curl 解析短链，提取 sec_uid
3. 拼主页URL: https://www.douyin.com/user/{sec_uid}
4. 发 QClaw（用模板A）
5. QClaw 写入 D:/AI_Bridge/cc-inbox.md → 读取展示
```

### 场景B：抓某条视频的评论区热评

```
1. 如果之前抓过该账号，直接查之前保存的数据文件拿 aweme_id
2. 如果没有 aweme_id，先走场景A拿到视频列表（含ID）
3. 用 aweme_id 发 QClaw（用模板B）
4. QClaw 写入 D:/AI_Bridge/cc-inbox.md → 读取展示
```

---

## 步骤1：预解析短链接

```bash
# 拿到重定向地址
curl -sI "https://v.douyin.com/xxxxx/" -o /dev/null -w "%{redirect_url}"

# 返回值示例:
# https://www.iesdouyin.com/share/user/MS4wLjABAAAAkDNXIWzFelsGy4EJTQPxRgTv...
#                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                                      这就是 sec_uid，提取出来

# 主页URL: https://www.douyin.com/user/{sec_uid}
```

## 步骤2：发送 QClaw 指令

**Bridge API：**
```
POST http://127.0.0.1:48763/api/tell-qclaw
Auth: Bearer cc-d956dc35a81d37ae2919c7e3698cd81c4dd245e95be43eef713211b7c26d0705
Body: {"message":"任务描述"}
```

### 模板A：抓主页视频数据
```
用浏览器打开 {主页URL}，不需要截图。
在浏览器里用 eval fetch 直接调抖音 API 拿数据，不要裸调 URL（需要 cookie）。

调这两个 API：
1. /aweme/v1/web/user/profile/other/?sec_user_id={sec_uid}  → 拿昵称、粉丝、总获赞
2. /aweme/v1/web/aweme/post/?sec_user_id={sec_uid}&count=30 → 拿视频列表（含 aweme_id）

跳过置顶视频，取前10个非置顶的：标题、点赞、评论、收藏、分享。
结果写入 D:/AI_Bridge/cc-inbox.md
```

### 模板B：抓评论区热评（已知 aweme_id）
```
用浏览器 eval fetch 调抖音评论 API（不要裸调 URL）：
/aweme/v1/web/comment/list/?aweme_id={aweme_id}&count=30

提取前30条热评的：用户昵称、评论内容、点赞数。
不需要截图。结果写入 D:/AI_Bridge/cc-inbox.md
```

---

## 关键经验

### QClaw 是什么、不是什么
- QClaw 用 **xbrowser（Playwright 浏览器驱动）**，能执行 JS、拦截网络请求
- QClaw **不是** Computer Use，不靠截图+模拟鼠标
- 截图 = 慢且无用，每次都写"不需要截图"

### 为什么 API 方式最快
- DOM 抓取：需等页面渲染、找选择器、处理动态加载
- SSR 数据提取：需解析页面内嵌 JSON，格式不稳定
- 网络拦截：需等请求发出再捕获，有延迟
- **eval fetch 调 API：浏览器已有 cookie，直接拿到结构化 JSON，最快**

### 抖音 API 需要 cookie
- 裸 URL 请求返回 `status_code: 5`（未认证）
- 必须在浏览器内用 `eval fetch` 执行，浏览器自带 cookie

### 数据复用
- QClaw 保存的原始数据在 `C:\Users\yan\.qclaw\workspace\`
- 抓完视频列表后，aweme_id 都在里面，下次抓评论直接用

---

## 耗时记录

| 测试 | 任务 | 耗时 | 当时问题 |
|------|------|------|---------|
| 第1次 | Coach老袁 主页+10视频 | 8:19 | 短链导航试错+DOM抓取+截图确认 |
| 第2次 | 小Lin说 主页+10视频 | 5:58 | 用了直链，但DOM→API切换损耗 |
| 第3次 | 小Lin说 单视频评论30条 | 6:59 | API裸调被拒→SSR→网络拦截→拿到ID |
| 目标 | — | 2-3分钟 | 三项优化全部到位后 |

---

## 场景C：下载视频音频 + 转文字

```
1. cc-haha 先用场景A拿到 aweme_id（QClaw 抓视频列表）
2. cc-haha 拼接视频链接：https://www.douyin.com/video/{aweme_id}
3. 发给 QClaw，让它用 tutjiexi.com 下载音频
4. QClaw 用 funasr 转文字
```

### 下载站点
- **tutjiexi.com**（兔兔解析）— 粘贴视频链接即可解析下载，无需 cookies
- 不要用 yt-dlp（需要 cookies，各种报错）

### funasr 转文字
```bash
pip install funasr -i https://pypi.tuna.tsinghua.edu.cn/simple
python -c "from funasr import AutoModel; model = AutoModel(model='paraformer-zh', vad_model='fsmn-vad', punc_model='ct-punc'); res = model.generate(input='音频文件路径'); import json; print(json.dumps(res, ensure_ascii=False))"
```

## 关键 API

- 用户信息: `GET /aweme/v1/web/user/profile/other/?sec_user_id=...`
- 视频列表: `GET /aweme/v1/web/aweme/post/?sec_user_id=...&count=30`
- 评论列表: `GET /aweme/v1/web/comment/list/?aweme_id=...&count=30`
