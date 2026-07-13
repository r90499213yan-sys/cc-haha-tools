# -*- coding: utf-8 -*-
"""
京东数据采集 v8 - 尝试各种搜索入口
"""
import json, os, time, sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

PROXY = "http://127.0.0.1:7890"
OUTPUT_DIR = r"D:\claude code项目文件\滴水科技调研"

def try_url(page, url, name):
    """尝试访问URL并获取信息"""
    print(f"\n--- [{name}] ---")
    try:
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(5)
        cur = page.url
        title = page.title()
        text = page.evaluate("() => document.body.innerText")[:2000]
        print(f"Title: {title}")
        print(f"URL: {cur[:120]}")
        print(f"Text(len={len(text)}): {text[:400]}")

        # 检查是否登录页
        if "login" in cur.lower() or "passport" in cur.lower():
            print("  => 需要登录!")
            return None

        page.screenshot(path=os.path.join(OUTPUT_DIR, f"v8_{name.replace('/','_')[:40]}.png"))
        return text
    except Exception as e:
        print(f"Error: {e}")
        return None

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

        # 先访问首页获取 cookies
        page = ctx.new_page()
        page.goto("https://www.jd.com/", wait_until="networkidle", timeout=60000)
        time.sleep(2)

        # 各种搜索URL格式
        urls = [
            # 独立搜索子域名
            ("https://search.jd.com/Search?keyword=滴水洗地机&enc=utf-8&wq=滴水洗地机", "搜索-标准"),
            ("https://search.jd.com/Search?keyword=滴水洗地机&enc=utf-8&page=1&s=1", "搜索-标准+p1"),
            # list.jd.com
            ("https://list.jd.com/list.html?cat=737,738,739&ev=exbrand_28919", "list-品牌(假设)"),
            # 搜索API（JSON格式）
            ("https://so.m.jd.com/ware/search.action?keyword=滴水洗地机", "m搜索API"),
            # 混合搜索
            ("https://search.jd.com/search?keyword=DIISEA&enc=utf-8", "搜索-DIISEA"),
            # p.3.cn (京东价格服务)
            ("https://p.3.cn/prices/mgets?skuIds=J_100093564692", "价格接口"),
        ]

        results = {}
        for url, name in urls:
            text = try_url(page, url, name)
            if text:
                results[name] = text[:3000]

        # 换个思路：看看京东是否有搜索结果嵌入在初始HTML中
        # 尝试通过搜索接口获取SSR内容
        print("\n\n=== 尝试 SSR 搜索 ===")
        ssr_url = "https://search.jd.com/search?keyword=%E6%BB%B4%E6%B0%B4%E6%B4%97%E5%9C%B0%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%BB%B4%E6%B0%B4"
        try_url(page, ssr_url, "SSR搜索")

        # 最后再试试带cookie后访问移动端
        print("\n\n=== 移动端搜索(带首页cookie) ===")
        m_url = "https://m.jd.com/search?keyword=%E6%BB%B4%E6%B0%B4%E6%B4%97%E5%9C%B0%E6%9C%BA"
        try:
            # 模拟点击搜索按钮，而不是直接GOTO
            ctx2 = browser.new_context(
                viewport={"width": 414, "height": 896},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
                locale="zh-CN"
            )
            page2 = ctx2.new_page()

            # 拦截所有请求观察
            captured = []
            def capture_request(request):
                url = request.url
                if any(k in url for k in ['ware', 'search', 'list']):
                    captured.append(url)
            page2.on("request", capture_request)

            page2.goto(m_url, wait_until="networkidle", timeout=60000)
            time.sleep(8)
            print(f"移动端URL: {page2.url}")
            print(f"移动端标题: {page2.title()}")

            # 打印捕获的API请求
            for c in captured:
                print(f"  API: {c[:150]}")

            # 再等一会儿让JS渲染
            page2.wait_for_timeout(10000)
            text = page2.evaluate("() => document.body.innerText")
            with open(os.path.join(OUTPUT_DIR, "m_search_full.txt"), "w", encoding="utf-8") as f:
                f.write(text)
            print(f"文本长度: {len(text)}")
            print(text[:1000])

            page2.screenshot(path=os.path.join(OUTPUT_DIR, "m_search_result.png"))
            ctx2.close()
        except Exception as e:
            print(f"Error: {e}")

        browser.close()

        with open(os.path.join(OUTPUT_DIR, "results_v8.json"), "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
