# -*- coding: utf-8 -*-
"""
简化版京东数据采集 - 先了解页面结构
"""
import json
import os
import time
from playwright.sync_api import sync_playwright

PROXY = "http://127.0.0.1:7890"
OUTPUT_DIR = r"D:\claude code项目文件\滴水科技调研"

def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            proxy={"server": PROXY}
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="zh-CN"
        )
        page = context.new_page()

        # 搜索滴水洗地机
        url = "https://search.jd.com/Search?keyword=滴水洗地机&enc=utf-8"
        print(f"访问: {url}")
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(5)

        # 获取页面文字前3000字
        text = page.evaluate("() => document.body.innerText")
        with open(os.path.join(OUTPUT_DIR, "page_text.txt"), "w", encoding="utf-8") as f:
            f.write(text[:5000])

        # 获取页面 title
        title = page.title()
        print(f"页面标题: {title}")

        # 检查是否有验证码/反爬页面
        current_url = page.url
        print(f"当前URL: {current_url}")

        if "risk" in current_url.lower() or "cfe" in current_url.lower() or "verify" in current_url.lower():
            print("触发了京东反爬！页面被重定向到风险验证。")
            page.screenshot(path=os.path.join(OUTPUT_DIR, "blocked.png"))
        else:
            page.screenshot(path=os.path.join(OUTPUT_DIR, "search_page.png"))

        # 打印页面文字前2000字符以便了解结构
        print("\n===== 页面文本(前2000字符) =====")
        print(text[:2000])

        # 也试试其他搜索词
        page.goto("https://search.jd.com/Search?keyword=DIISEA&enc=utf-8", wait_until="networkidle", timeout=60000)
        time.sleep(5)
        text2 = page.evaluate("() => document.body.innerText")
        print(f"\n===== DIISEA 搜索URL: {page.url} =====")
        print(text2[:3000])

        browser.close()

if __name__ == "__main__":
    main()
