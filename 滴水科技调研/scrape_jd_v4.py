# -*- coding: utf-8 -*-
"""
京东数据采集 v4 - API 接口 + 店铺页面直接访问
"""
import json, os, time, sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

PROXY = "http://127.0.0.1:7890"
OUTPUT_DIR = r"D:\claude code项目文件\滴水科技调研"

def try_page(page, url, name, wait=5, check_selector=None):
    try:
        print(f"\n--- [{name}] ---")
        print(f"URL: {url}")
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(wait)
        cur = page.url
        title = page.title()
        print(f"标题: {title} | URL: {cur[:100]}")
        text = page.evaluate("() => document.body.innerText")[:3000]
        print(f"文本预览(len={len(text)}):")
        print(text[:600])
        return cur, title, text
    except Exception as e:
        print(f"错误: {e}")
        return "", "", ""

def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            proxy={"server": PROXY}
        )
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="zh-CN"
        )
        page = ctx.new_page()

        # 1. 尝试京东 API 搜索
        # 京东的搜索 API: https://search.jd.com/s_new.php
        api_url = "https://search.jd.com/s_new.php?keyword=%E6%BB%B4%E6%B0%B4%E6%B4%97%E5%9C%B0%E6%9C%BA&enc=utf-8&page=1"
        print("=== API 搜索 ===")
        try_page(page, api_url, "API搜索")

        # 2. 尝试 jsonp 接口
        jsonp_url = "https://suggest.taobao.com/sug?code=utf-8&q=滴水洗地机&callback=cb"
        print("\n=== 淘宝 Suggest API ===")
        page.goto(jsonp_url, wait_until="networkidle", timeout=10000)
        t = page.evaluate("() => document.body.innerText")
        print(f"淘宝suggest: {t[:500]}")

        # 3. 尝试京东的 jsonp 搜索 suggest
        js_url = "https://dd-search.jd.com/?ver=2&key=%E6%BB%B4%E6%B0%B4%E6%B4%97%E5%9C%B0%E6%9C%BA"
        print("\n=== 京东 Suggest ===")
        page.goto(js_url, wait_until="networkidle", timeout=10000)
        t = page.evaluate("() => document.body.innerText")
        print(f"京东suggest: {t[:500]}")

        # 4. 尝试直接访问店铺页面格式
        # 京东店铺页面格式: https://mall.jd.com/index-{shopId}.html
        # 尝试用 DIISEA 搜索店铺 API
        shop_url = "https://shop.jd.com/search?keyword=DIISEA"
        print("\n=== 店铺搜索 ===")
        try_page(page, shop_url, "店铺搜索")

        # 5. 试一下京东的商品 JSON 接口
        for item_id in ["100093564692", "100059252291"]:
            api_item = f"https://p.3.cn/prices/get?skuid=J_{item_id}"
            print(f"\n=== 价格接口 {item_id} ===")
            page.goto(api_item, wait_until="networkidle", timeout=10000)
            t = page.evaluate("() => document.body.innerText")
            print(f"Response: {t[:200]}")

        browser.close()

if __name__ == "__main__":
    main()
