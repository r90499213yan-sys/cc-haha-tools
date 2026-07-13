Stop-Process -Name ollama -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
$env:OLLAMA_MODELS = "D:\Ollama\models"
Start-Process -FilePath "C:\Users\yan\AppData\Local\Programs\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep -Seconds 12
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
