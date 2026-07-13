---
name: local-vision-model
description: 本地看图模型 qwen3-vl:4b 部署信息、启动方式、调用模板
type: reference
---

## 本地看图功能已部署

### 环境信息
- **Ollama 版本**：0.31.2
- **Ollama 程序**：`C:\Users\yan\AppData\Local\Programs\Ollama\`
- **模型**：`qwen3-vl:4b`（Q4_K_M 量化，3.3GB）
- **模型存放**：`D:\Ollama\models\`（环境变量 `OLLAMA_MODELS=D:\Ollama\models`）
- **能力**：vision + completion + tools + thinking，上下文 256K

### 启动 Ollama 服务
Ollama 关闭后需要重启才能看图。在 bash 里执行：
```
OLLAMA_MODELS="D:\\Ollama\\models" "/c/Users/yan/AppData/Local/Programs/Ollama/ollama.exe" serve > /dev/null 2>&1 &
```

### 调用模板（Python）
```python
import base64, json, urllib.request

image_path = r'图片路径'

with open(image_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

payload = json.dumps({
    'model': 'qwen3-vl:4b',
    'stream': False,
    'messages': [{
        'role': 'user',
        'content': '请详细描述这张图片的内容',
        'images': [b64]
    }]
}).encode('utf-8')

req = urllib.request.Request('http://localhost:11434/api/chat', data=payload, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req, timeout=120)
result = json.loads(resp.read())
# 结果在 result['message']['content']
```

### 与 CC-HAHA 配合
用户在 CC-HAHA 里拖图/粘贴图片后，告诉 Claude Code"帮我看这张图"，Claude Code 用上述模板调 Ollama 获取文字描述。

### 环境变量（已永久设置）
- `OLLAMA_MODELS` = `D:\Ollama\models`（通过 PowerShell SetEnvironmentVariable 写入用户变量）
