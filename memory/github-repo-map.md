---
name: GitHub仓库同步地图
description: 本地文件夹到GitHub仓库的一一对应关系，用于同步备份
type: reference
---

# GitHub 仓库同步地图

> 用户说"同步"或"推GitHub"时，按此表执行

## 项目文件夹 → GitHub 仓库

| 本地路径 | GitHub 仓库 | 说明 |
|----------|------------|------|
| `AI项目管理/AI Agent学习/` | `ai-agent-study` | AI学习笔记 |
| `AI项目管理/小林颈腰椎康复-抖音/` | `rehab-douyin` | 康复抖音项目 |
| `AI项目管理/电话录音灵感选题/` | `call-recording-ideas` | 电话选题项目 |
| `AI项目管理/个人知识库/` | `personal-knowledge-base` | 读书知识库 |
| `AI项目管理/新闻资讯项目/` | `news-briefing` | 新闻简报 |
| `AI项目管理/情侣号-抖音/` | 待建仓库 | 新建空项目 |
| 根目录所有文件 | `cc-haha-tools` | 工具脚本、配置、知识库等 |
| C盘 `memory/` | `cc-haha-tools/memory/` | 项目记忆文件 |

## 同步流程

1. 克隆目标仓库到临时目录
2. 本地文件覆盖进去（保留 .git）
3. 有变更就 commit + push
4. 清理临时目录

## 不在同步范围内的

- `project-backup` 仓库（历史快照，不再更新）
- QClaw 聊天记录（不含项目文件，且含敏感信息）
- C盘 `~/.claude/projects/` 下的会话记录
