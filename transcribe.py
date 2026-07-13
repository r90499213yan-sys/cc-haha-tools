"""
============================================================
  FunASR 中文语音转文字 -- 独立工具
  位置: D:\CC-HAHA\transcribe.py
  环境: D:\CC-HAHA\cheat-venv
============================================================

用法（任何 AI 工具 / 终端都可用）:

  D:\CC-HAHA\cheat-venv\Scripts\python.exe D:\CC-HAHA\transcribe.py <音频文件或文件夹>

示例:
  D:\CC-HAHA\cheat-venv\Scripts\python.exe D:\CC-HAHA\transcribe.py 视频.mp3
  D:\CC-HAHA\cheat-venv\Scripts\python.exe D:\CC-HAHA\transcribe.py ./audio_folder/

输出: 同目录下生成 <原文件名>_transcript.txt

模型:
  FunASR paraformer-large (阿里 DAMO) -- 中文普通话
  + VAD（语音端点检测）
  + 标点恢复
============================================================
"""
import sys
import os
from pathlib import Path

# 强制模型缓存走D盘（别吃C盘空间）
os.environ["MODELSCOPE_CACHE"] = r"D:\AI-Downloads\modelscope"

# Windows GBK 终端兼容
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

MODEL_NAME = "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
VAD_MODEL = "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch"
PUNC_MODEL = "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch"

AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma", ".mp4", ".webm", ".mov", ".avi", ".mkv"}

def find_audio_files(paths):
    files = []
    for p in paths:
        pp = Path(p)
        if pp.is_file() and pp.suffix.lower() in AUDIO_EXTS:
            files.append(pp)
        elif pp.is_dir():
            for f in sorted(pp.rglob("*")):
                if f.is_file() and f.suffix.lower() in AUDIO_EXTS:
                    files.append(f)
        else:
            print(f"[skip] not audio or missing: {p}")
    return files

def transcribe_one(model, audio_path: Path):
    out_path = audio_path.with_suffix(audio_path.suffix + "_transcript.txt")
    if out_path.exists():
        text = out_path.read_text(encoding="utf-8")
        print(f"  [cached] {out_path.name} ({len(text)} chars)")
        return text

    print(f"  [transcribing] {audio_path.name} ...", end=" ", flush=True)
    try:
        result = model.generate(input=str(audio_path))
        text = result[0]["text"] if result else ""
        out_path.write_text(text, encoding="utf-8")
        print(f"done ({len(text)} chars)")
        return text
    except Exception as e:
        print(f"failed: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("[ERROR] please provide at least one audio file or folder path")
        sys.exit(1)

    targets = find_audio_files(sys.argv[1:])
    if not targets:
        print("[ERROR] no supported audio files found")
        print(f"   supported formats: {', '.join(sorted(AUDIO_EXTS))}")
        sys.exit(1)

    print(f"[scan] found {len(targets)} audio file(s)")
    print(f"[load] loading FunASR model (first run downloads ~1-2 min)...")

    from funasr import AutoModel
    model = AutoModel(
        model=MODEL_NAME,
        vad_model=VAD_MODEL,
        punc_model=PUNC_MODEL,
        device="cuda:0",
    )
    print("[load] model ready\n")

    ok, fail = 0, 0
    for f in targets:
        result = transcribe_one(model, f)
        if result:
            ok += 1
        else:
            fail += 1

    print(f"\n{'='*50}")
    print(f"[done] {ok} ok / {fail} failed")

if __name__ == "__main__":
    main()
