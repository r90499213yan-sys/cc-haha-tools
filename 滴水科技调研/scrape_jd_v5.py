# -*- coding: utf-8 -*-
"""
京东数据采集 v5 - 修复下载问题 + 完整 API 抓取
"""
import json, os, time, sys, requests
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

PROXY = "http://127.0.0.1:7890"
OUTPUT_DIR = r"D:\claude code项目文件\滴水科技调研"

def main():
    # === 先用 requests 抓取 ===
    proxies = {"http": PROXY, "https": PROXY}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 1. API 搜索 (s_new.php)
    print("=== API 搜索 (requests) ===")
    api_url = "https://search.jd.com/s_new.php?keyword=%E6%BB%B4%E6%B0%B4%E6%B4%97%E5%9C%B0%E6%9C%BA&enc=utf-8&page=1&s=1&scrolling=y&tpl=2_M"
    try:
        r = requests.get(api_url, headers=headers, proxies=proxies, timeout=30)
        print(f"Status: {r.status_code}, Len: {len(r.text)}")
        print(f"Preview (500): {r.text[:500]}")
        if len(r.text) > 100:
            with open(os.path.join(OUTPUT_DIR, "api_search_result.html"), "w", encoding="utf-8") as f:
                f.write(r.text)
    except Exception as e:
        print(f"Error: {e}")

    # 2. 店铺搜索
    print("\n=== 店铺搜索 (requests) ===")
    shop_url = "https://search.jd.com/shop.html?keyword=DIISEA&enc=utf-8"
    try:
        r = requests.get(shop_url, headers=headers, proxies=proxies, timeout=30, allow_redirects=True)
        print(f"Status: {r.status_code}, Len: {len(r.text)}")
        print(f"URL: {r.url}")
        print(f"Preview: {r.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. 试 jd.com 手机版直接搜索 - 带 cookies 模拟
    print("\n=== m.jd.com 搜索 (requests with referer) ===")
    m_url = "https://m.jd.com/search?keyword=%E6%BB%B4%E6%B0%B4%E6%B4%97%E5%9C%B0%E6%9C%BA"
    m_headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Referer": "https://m.jd.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        r = requests.get(m_url, headers=m_headers, proxies=proxies, timeout=30, allow_redirects=True)
        print(f"Status: {r.status_code}, Len: {len(r.text)}")
        print(f"URL: {r.url}")
        with open(os.path.join(OUTPUT_DIR, "mjd_search.html"), "w", encoding="utf-8") as f:
            f.write(r.text)

        # 检查是否包含商品信息
        has_products = "ware" in r.text.lower() or "item" in r.text.lower() or "sku" in r.text.lower()
        print(f"包含商品关键词: {has_products}")

    except Exception as e:
        print(f"Error: {e}")

    # 4. 尝试店铺页面直接访问（可能的店铺ID格式）
    print("\n=== 可能的店铺页面 ===")
    shop_ids = [
        "https://mall.jd.com/index-1000447512.html",  # 常见搜索引擎结果中的ID
        "https://diisea.jd.com/",  # 品牌子域名
        "https://shop.m.jd.com/?shopId=1000447512",
        "https://shop.m.jd.com/search?keyword=DIISEA%E5%AE%98%E6%96%B9%E6%97%97%E8%88%B0%E5%BA%97",
    ]
    for url in shop_ids:
        try:
            r = requests.get(url, headers=headers, proxies=proxies, timeout=30, allow_redirects=True)
            title = ""
            if "<title>" in r.text:
                title = r.text.split("<title>")[1].split("</title>")[0] if "</title>" in r.text.split("<title>")[1] else ""
            print(f"[{r.status_code}] {url[:60]} | Title: {title}")
        except Exception as e:
            print(f"Error: {e}")

    # 5. 京东的搜索 suggest 接口
    print("\n=== 京东搜索 Suggest ===")
    suggest_url = "https://search.jd.com/suggest?keyword=%E6%BB%B4%E6%B0%B4%E6%B4%97%E5%9C%B0%E6%9C%BA&enc=utf-8"
    try:
        r = requests.get(suggest_url, headers=headers, proxies=proxies, timeout=30)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

    # 6. 直接加载 API 返回的 HTML 并用 Playwright 渲染
    print("\n=== Playwright 渲染 HTML ===")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, proxy={"server": PROXY})
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="zh-CN")
        page = ctx.new_page()

        # 拦截下载
        page.on("download", lambda d: print(f"下载被拦截: {d.suggested_filename}"))

        # 直接打开 s_new.php
        page.goto(api_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        text = page.evaluate("() => document.body.innerText")
        print(f"页面文本长度: {len(text)}")
        print(f"预览:\n{text[:1000]}")

        # 查找商品列表
        items = page.evaluate("""
        () => {
            const skus = [];
            document.querySelectorAll('[data-sku]').forEach(el => skus.push(el.getAttribute('data-sku')));
            const lis = document.querySelectorAll('.gl-item, .goods-list-v2 li, [class*="goods"]');
            return {
                skuCount: skus.length,
                skus: skus.slice(0, 10),
                liCount: lis.length
            };
        }
        """)
        print(f"商品元素: {items}")

        page.screenshot(path=os.path.join(OUTPUT_DIR, "api_render.png"))
        browser.close()

if __name__ == "__main__":
    main()
