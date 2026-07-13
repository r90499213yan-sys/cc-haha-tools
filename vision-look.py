# Local vision tool - calls qwen3-vl:4b to describe image content
# Usage: python vision-look.py "image_path"
import sys, base64, json, time, subprocess, urllib.request, os, io, pathlib

# Fix GBK encoding issue on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

IMAGE_PATH = sys.argv[1]
OLLAMA_EXE = r"C:\Users\yan\AppData\Local\Programs\Ollama\ollama.exe"
OLLAMA_MODELS_DIR = r"D:\Ollama\models"
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_CHAT = f"{OLLAMA_BASE}/api/chat"
OLLAMA_TAGS = f"{OLLAMA_BASE}/api/tags"
MODEL_NAME = "qwen3-vl:4b"

def log(msg):
    print(f"[Vision] {msg}")

def http_get(url, timeout=10):
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        return resp.read()
    except Exception:
        return None

def ollama_running():
    return http_get(OLLAMA_TAGS, timeout=3) is not None

def get_models():
    data = http_get(OLLAMA_TAGS)
    if not data:
        return []
    try:
        return [m["name"] for m in json.loads(data).get("models", [])]
    except:
        return []

def start_ollama():
    """Start Ollama, ensuring correct model path via env var and junction fallback."""
    # Ensure junction exists (belt: permanent env; suspenders: junction)
    default_models = os.path.expandvars(r"%USERPROFILE%\.ollama\models")
    if not os.path.exists(default_models):
        os.makedirs(os.path.dirname(default_models), exist_ok=True)
        try:
            # Try creating a junction (works even if env var fails)
            import _winapi
            _winapi.CreateJunction(r"D:\Ollama\models", default_models)
            log("已创建模型目录链接")
        except Exception:
            pass  # Already exists or can't create, fall through to env var

    log("正在启动 Ollama...")
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = OLLAMA_MODELS_DIR
    subprocess.Popen(
        [OLLAMA_EXE, "serve"],
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

# Step 1: Check image file
path = pathlib.Path(IMAGE_PATH)
if not path.exists():
    log(f"错误：文件不存在 - {IMAGE_PATH}")
    sys.exit(1)
if path.stat().st_size == 0:
    log(f"错误：文件为空（0 字节） - {IMAGE_PATH}")
    log("提示：可能是粘贴失败，试试用 Win+Shift+S 截图 → 画图保存 → 拖文件进来")
    sys.exit(1)

# Step 2: Ensure Ollama is running with models available
for attempt in range(3):
    if not ollama_running():
        log("Ollama 未运行")
        start_ollama()
        time.sleep(10)
        continue

    models = get_models()
    if MODEL_NAME in models:
        break  # All good

    if models:
        log(f"模型列表中没有 {MODEL_NAME}，只有: {models}")
        log(f"请运行: ollama pull {MODEL_NAME}")
        sys.exit(1)
    else:
        # Models empty — likely wrong path. Kill and restart with env var.
        log("模型列表为空，可能是路径问题，正在重启 Ollama...")
        subprocess.run(["taskkill", "/f", "/im", "ollama.exe"], capture_output=True)
        time.sleep(3)
        start_ollama()
        time.sleep(12)
else:
    log("错误：Ollama 多次启动失败")
    sys.exit(1)

# Step 3: Encode image
with open(IMAGE_PATH, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

# Step 4: Call the vision model (with retry for cold start)
payload = json.dumps({
    "model": MODEL_NAME,
    "stream": False,
    "messages": [{
        "role": "user",
        "content": "Please describe the content of this image in detail, including all text and visual information. Reply in Chinese.",
        "images": [b64]
    }]
}).encode("utf-8")

last_error = None
for retry in range(3):
    try:
        req = urllib.request.Request(OLLAMA_CHAT, data=payload, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=180)
        result = json.loads(resp.read())
        print(result["message"]["content"])
        sys.exit(0)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            log(f"模型 {MODEL_NAME} 未找到，尝试拉取...")
            # Let the user know they need to pull it
            log(f"请手动运行: ollama pull {MODEL_NAME}")
            sys.exit(1)
        last_error = e
        log(f"HTTP {e.code}，{2 ** retry} 秒后重试...")
        time.sleep(2 ** retry)
    except Exception as e:
        last_error = e
        log(f"请求失败: {e}，{2 ** retry} 秒后重试...")
        time.sleep(2 ** retry)

log(f"错误：重试 3 次后仍失败 - {last_error}")
sys.exit(1)
