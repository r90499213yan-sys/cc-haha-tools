@echo off
:: FunASR 语音转文字 - 快捷启动
:: 用法: FunASR.bat 音频文件.mp3
::       FunASR.bat 音频文件夹/

set ARG=%1
if "%ARG%"=="" (
    echo 用法: FunASR.bat 音频文件或文件夹
    echo 示例: FunASR.bat D:\视频素材\*.mp3
    pause
    exit /b 1
)

D:\CC-HAHA\cheat-venv\Scripts\python.exe D:\CC-HAHA\FunASR.py "%ARG%"
pause
