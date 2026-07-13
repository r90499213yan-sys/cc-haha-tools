@echo off
:: cc-gateway 启动脚本
:: 放到 shell:startup 目录可开机自启

cd /d "D:\claude code项目文件\cc-gateway"
echo [%date% %time%] Starting cc-gateway on port 48763...
node cc-gateway.js
