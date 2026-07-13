# 每周检查 git-based skills 是否有更新
# 有更新时写入提醒文件，下次 Claude Code 启动时能看到

$skillDirs = @(
    "C:\Users\yan\.claude\skills\headroom",
    "C:\Users\yan\.claude\skills\book-to-webpage"
)

$reminderFile = "D:\claude code项目文件\skill-updates-pending.md"
$results = @()
$today = Get-Date -Format "yyyy-MM-dd"

foreach ($dir in $skillDirs) {
    if (-not (Test-Path "$dir\.git")) { continue }

    Push-Location $dir
    try {
        # 获取远程更新信息
        git fetch origin 2>&1 | Out-Null

        $branch = git rev-parse --abbrev-ref HEAD
        $local = git rev-parse HEAD
        $remote = git rev-parse "origin/$branch"
        $skillName = Split-Path $dir -Leaf

        if ($local -ne $remote) {
            $count = git rev-list --count "HEAD..origin/$branch"
            $results += "- **$skillName**: 落后 $count 个提交（$today）"
        }
    }
    finally {
        Pop-Location
    }
}

if ($results.Count -gt 0) {
    $content = @"
# Skill 更新提醒

检查日期：$today

以下 skill 有可用更新：

$($results -join "`n")

---
*下次和 Claude Code 对话时说"检查 skill 更新"即可查看详情并更新。*
"@
    $content | Out-File -FilePath $reminderFile -Encoding UTF8
} else {
    # 无更新时也写个文件记录上次检查时间
    $content = @"
# Skill 更新状态

上次检查：$today — 所有 skill 已是最新。

"@
    $content | Out-File -FilePath $reminderFile -Encoding UTF8
}
