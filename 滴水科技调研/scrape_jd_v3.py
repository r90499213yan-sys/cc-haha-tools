# -*- coding: utf-8 -*-
"""
京东数据采集 v3 - 移动端 + 店铺页面
"""
import json, os, time, sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

PROXY = "http://127.0.0.1:7890"
OUTPUT_DIR = r"D:\claude code项目文件\滴水科技调研"

def try_page(page, url, name, wait=5):
    """尝试访问页面，返回文本"""
    print(f"\n{'='*50}")
    print(f"访问 [{name}]: {url}")
    page.goto(url, wait_until="networkidle", timeout=60000)
    time.sleep(wait)
    current_url = page.url
    title = page.title()
    print(f"标题: {title}")
    print(f"跳转后URL: {current_url}")

    text = page.evaluate("() => document.body.innerText") or ""
    print(f"文本长度: {len(text)}")
    if text:
        print(f"文本前800字:\n{text[:800]}")

    # 保存截图
    safe = name.replace("/","_").replace(":","_")
    page.screenshot(path=os.path.join(OUTPUT_DIR, f"jd_{safe}.png"))

    return current_url, text

def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            proxy={"server": PROXY}
        )
        context = browser.new_context(
            viewport={"width": 414, "height": 896},
            user_agent="Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            locale="zh-CN"
        )
        page = context.new_page()

        urls = [
            # 移动端搜索
            ("https://m.jd.com/search?keyword=滴水洗地机", "移动端-滴水洗地机"),
            # 店铺搜索 - DIISEA官方旗舰店
            ("https://search.jd.com/Search?keyword=DIISEA%E5%AE%98%E6%96%B9%E6%97%97%E8%88%B0%E5%BA%97&enc=utf-8&wq=DIISEA%E5%AE%98%E6%96%B9%E6%97%97%E8%88%B0%E5%BA%97", "店铺-DIISEA官方旗舰店"),
            # 直接搜索 DIISEA
            ("https://m.jd.com/search?keyword=DIISEA", "移动端-DIISEA"),
            # 试试 soap page
            ("https://so.m.jd.com/ware/search.action?keyword=滴水洗地机", "移动端so-滴水洗地机"),
        ]

        results = {}
        for url, name in urls:
            try:
                curl, text = try_page(page, url, name)
                results[name] = {"url": curl, "text_preview": text[:2000] if text else ""}
            except Exception as e:
                print(f"错误: {e}")

        # 保存结果
        with open(os.path.join(OUTPUT_DIR, "results_v3.json"), "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        browser.close()

if __name__ == "__main__":
    main()
