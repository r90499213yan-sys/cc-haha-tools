# 本地看图工具 — 调用 qwen3-vl:4b 描述图片内容
# 用法: powershell -File vision-look.ps1 "图片路径"
param([string]$imagePath)

$ollamaUrl = "http://localhost:11434/api/chat"
$model = "qwen3-vl:4b"

# 1. 检查 Ollama 是否在运行
try {
    $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop
} catch {
    Write-Host "[Vision] Ollama 未运行，尝试启动..." -ForegroundColor Yellow
    $env:OLLAMA_MODELS = "D:\Ollama\models"
    Start-Process "C:\Users\yan\AppData\Local\Programs\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 8
}

# 2. 读取图片并 Base64 编码
$bytes = [IO.File]::ReadAllBytes($imagePath)
$b64 = [Convert]::ToBase64String($bytes)

# 3. 构建请求
$body = @{
    model = $model
    stream = $false
    messages = @(
        @{
            role = "user"
            content = "请详细描述这张图片的内容，包括所有文字和画面信息"
            images = @($b64)
        }
    )
} | ConvertTo-Json -Depth 5

# 4. 调用 Ollama
$result = Invoke-RestMethod -Uri $ollamaUrl -Method Post -Body $body -ContentType "application/json" -TimeoutSec 120

# 5. 输出结果
Write-Output $result.message.content
