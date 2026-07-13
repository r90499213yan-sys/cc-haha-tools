# -*- coding: utf-8 -*-
"""
京东滴水科技产品信息采集脚本
使用 Playwright 自动化浏览器，数据仅用于调研目的
"""
import json
import os
import re
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 代理设置
PROXY = "http://127.0.0.1:7890"
OUTPUT_DIR = r"D:\claude code项目文件\滴水科技调研"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_browser(playwright):
    """创建带代理的浏览器"""
    browser = playwright.chromium.launch(
        headless=False,
        proxy={"server": PROXY}
    )
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="zh-CN"
    )
    page = context.new_page()
    return browser, context, page

def search_jd(page, keyword):
    """在京东搜索关键词"""
    url = f"https://search.jd.com/Search?keyword={keyword}&enc=utf-8"
    print(f"访问: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)  # 等待页面渲染

    # 保存截图
    safe_name = keyword.replace("/", "_").replace("\\", "_").replace(":", "_")
    page.screenshot(path=os.path.join(OUTPUT_DIR, f"screenshot_{safe_name}.png"), full_page=False)

    # 尝试获取页面内容
    content = page.content()
    return content

def get_page_text(page):
    """提取页面可见文本"""
    try:
        text = page.evaluate("() => document.body.innerText")
        return text[:10000]  # 限制长度
    except:
        return ""

def scrape_product_list(page, keyword):
    """抓取商品列表"""
    try:
        # 等待商品列表出现
        page.wait_for_selector(".gl-item", timeout=10000)
    except PlaywrightTimeout:
        page.wait_for_selector("[class*='gl-i']", timeout=5000)

    time.sleep(3)

    # 用 JavaScript 提取商品信息
    products = page.evaluate("""
    () => {
        const items = document.querySelectorAll('[data-sku], .gl-item, .J_goodsItem');
        const results = [];
        items.forEach((item, idx) => {
            if (idx >= 30) return;
            const sku = item.getAttribute('data-sku') || '';
            const nameEl = item.querySelector('.p-name em, .p-name a, [class*="title"]');
            const priceEl = item.querySelector('.p-price i, .p-price, [class*="price"]');
            const commentEl = item.querySelector('.p-commit a, [class*="comment"]');
            const imgEl = item.querySelector('img');
            const shopEl = item.querySelector('.p-shop a, .p-shop span, [class*="shop"]');
            const linkEl = item.querySelector('a[href*="item.jd.com"]');

            results.push({
                sku: sku,
                name: nameEl ? nameEl.innerText.trim() : '',
                price: priceEl ? priceEl.innerText.trim() : '',
                comments: commentEl ? commentEl.innerText.trim() : '',
                img: imgEl ? imgEl.src || imgEl.getAttribute('data-lazy-img') : '',
                shop: shopEl ? shopEl.innerText.trim() : '',
                link: linkEl ? linkEl.href : ''
            });
        });
        return results;
    }
    """)

    print(f"抓取到 {len(products)} 个商品")
    return products

def visit_product_page(page, url, sku_id):
    """访问单个商品页面"""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        page.screenshot(path=os.path.join(OUTPUT_DIR, f"product_{sku_id}.png"), full_page=False)

        # 获取商品详情
        text = get_page_text(page)
        return text
    except Exception as e:
        print(f"访问商品页面失败: {e}")
        return ""

def get_reviews(page, product_id):
    """抓取评价信息"""
    # 先获取商品评价概览
    try:
        page.goto(f"https://item.jd.com/{product_id}.html", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
    except:
        pass

    # 尝试获取评价信息
    review_info = page.evaluate("""
    () => {
        const info = {};
        const rateEl = document.querySelector('.percent-con');
        const countEl = document.querySelector('.comment-count');
        if (rateEl) info.rate = rateEl.innerText.trim();
        if (countEl) info.count = countEl.innerText.trim();
        return info;
    }
    """)

    # 点击评价tab
    try:
        comment_tab = page.query_selector("li[data-anchor='#comment'], .tab-main li:has-text('评价')")
        if comment_tab:
            comment_tab.click()
            time.sleep(3)
    except:
        pass

    # 获取评价标签
    tags = page.evaluate("""
    () => {
        const tagEls = document.querySelectorAll('.tag-list .tag,.filter-list .tag');
        return Array.from(tagEls).map(el => el.innerText.trim());
    }
    """)

    review_info['tags'] = tags[:30]

    # 获取好评内容
    good_reviews = page.evaluate("""
    () => {
        const items = document.querySelectorAll('.comment-item[data-tab="itemgood"], .comment-item');
        return Array.from(items).slice(0, 10).map(el => {
            const content = el.querySelector('.comment-con, .comment-content');
            const star = el.querySelector('.comment-star');
            return {
                content: content ? content.innerText.trim() : '',
                star: star ? star.innerText.trim() : ''
            };
        });
    }
    """)

    review_info['sample_reviews'] = good_reviews[:10]

    return review_info

def main():
    keywords = [
        "滴水洗地机",
        "滴水科技",
        "滴水旗舰店"
    ]

    all_products = {}

    with sync_playwright() as playwright:
        browser, context, page = create_browser(playwright)

        try:
            for keyword in keywords:
                print(f"\n===== 搜索: {keyword} =====")
                content = search_jd(page, keyword)

                # 抓取商品列表
                products = scrape_product_list(page, keyword)
                all_products[keyword] = products

                # 保存原始HTML供分析
                safe_name = keyword.replace("/", "_").replace("\\", "_")
                with open(os.path.join(OUTPUT_DIR, f"html_{safe_name}.html"), "w", encoding="utf-8") as f:
                    f.write(content)

                # 获取页面文字
                text = get_page_text(page)
                with open(os.path.join(OUTPUT_DIR, f"text_{safe_name}.txt"), "w", encoding="utf-8") as f:
                    f.write(text)

                time.sleep(3)

        finally:
            browser.close()

    # 保存结果
    with open(os.path.join(OUTPUT_DIR, "products_raw.json"), "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print("\n===== 完成 =====")
    print(f"结果保存到: {os.path.join(OUTPUT_DIR, 'products_raw.json')}")

if __name__ == "__main__":
    main()
