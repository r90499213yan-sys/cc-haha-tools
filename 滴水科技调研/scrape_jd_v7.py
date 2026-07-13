# -*- coding: utf-8 -*-
"""
京东数据采集 v7 - 无头模式，加大等待时间 + 拦截XHR获取API数据
"""
import json, os, time, sys, re
sys.stdout.reconfigure(encoding='utf-8')
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

        # 收集所有网络请求
        api_responses = []
        def capture_response(response):
            url = response.url
            if any(k in url for k in ['search', 'ware', 'list', 's_new']):
                try:
                    body = response.text()
                    if len(body) > 50:
                        api_responses.append({"url": url, "body": body[:5000]})
                except:
                    pass

        page = context.new_page()
        page.on("response", capture_response)

        # 先访问京东首页获取 cookie
        print("访问京东首页...")
        page.goto("https://www.jd.com/", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        print(f"首页: {page.title()}")

        # 搜索滴水洗地机
        url = "https://search.jd.com/Search?keyword=%E6%BB%B4%E6%B0%B4%E6%B4%97%E5%9C%B0%E6%9C%BA&enc=utf-8"
        print(f"\n搜索: 滴水洗地机")
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(10)  # 等 JS 完全加载

        cur = page.url
        title = page.title()
        print(f"当前URL: {cur[:100]}")
        print(f"标题: {title}")

        # 保存完全渲染后的页面
        with open(os.path.join(OUTPUT_DIR, "search_rendered.html"), "w", encoding="utf-8") as f:
            f.write(page.content())

        # 保存 API 响应
        with open(os.path.join(OUTPUT_DIR, "api_responses.json"), "w", encoding="utf-8") as f:
            json.dump(api_responses, f, ensure_ascii=False, indent=2)

        print(f"捕获到 {len(api_responses)} 个API响应")

        # 获取页面文字
        text = page.evaluate("() => document.body.innerText")[:5000]
        print(f"\n页面文本(前2000字符):")
        print(text[:2000])

        # 截图
        page.screenshot(path=os.path.join(OUTPUT_DIR, "search_final.png"))

        # 尝试获取JS变量
        js_data = page.evaluate("""
        () => {
            const vars = {};
            // 尝试常见的全局数据变量
            for (let key of Object.keys(window)) {
                if (key.includes('data') || key.includes('list') || key.includes('result') || key.includes('page')) {
                    try {
                        const val = window[key];
                        if (typeof val === 'object' && val !== null) {
                            vars[key] = JSON.stringify(val).substring(0, 500);
                        } else if (typeof val === 'string' && val.length < 500) {
                            vars[key] = val;
                        }
                    } catch(e) {}
                }
            }
            return vars;
        }
        """)
        with open(os.path.join(OUTPUT_DIR, "js_vars.json"), "w", encoding="utf-8") as f:
            json.dump(js_data, f, ensure_ascii=False, indent=2)
        print(f"JS变量数量: {len(js_data)}")

        browser.close()

if __name__ == "__main__":
    main()
