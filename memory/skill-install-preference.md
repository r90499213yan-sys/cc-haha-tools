---
name: skill-install-preference
description: 安装 skill 默认用软链接方式，不用本地副本
type: feedback
---

安装新 skill 时默认使用软链接方式（symlink），不要用本地副本。

**Why:** 软链接指向源头仓库，`git pull` 更新后 Claude Code 自动读取最新内容；副本方式需要手动同步两份文件，容易遗漏。

**How to apply:** 安装任何 skill 时，优先创建软链接（`ln -s` 或 marketplace 默认方式），避免直接复制文件到 `.claude/skills/`。
