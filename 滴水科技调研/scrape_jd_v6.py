# -*- coding: utf-8 -*-
"""
京东数据采集 v6 - 有头模式，等待用户手动登录
思路：打开浏览器让用户扫码登录，然后自动抓取
"""
import json, os, time, sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

PROXY = "http://127.0.0.1:7890"
OUTPUT_DIR = r"D:\claude code项目文件\滴水科技调研"

def save_cookies(context):
    cookies = context.cookies()
    with open(os.path.join(OUTPUT_DIR, "jd_cookies.json"), "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    print(f"Cookies 已保存 ({len(cookies)} 条)")

def load_cookies(context):
    cookie_file = os.path.join(OUTPUT_DIR, "jd_cookies.json")
    if os.path.exists(cookie_file):
        with open(cookie_file, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        print(f"Cookies 已加载 ({len(cookies)} 条)")
        return True
    return False

def parse_products_from_page(page):
    """从搜索结果页提取商品信息"""
    products = page.evaluate("""
    () => {
        const items = [];
        // 尝试多种选择器
        const selectors = [
            '.gl-item',           // PC端旧版
            '[data-sku]',         // 有SKU的元素
            '.goods-list-v2 li',  // PC端新版
            '.search-list .item', // 移动端
            '[class*="goodsItem"]',
            '[class*="gl-i-"]'
        ];

        let elements = [];
        for (const sel of selectors) {
            const els = document.querySelectorAll(sel);
            if (els.length > 0) {
                elements = Array.from(els);
                break;
            }
        }

        if (elements.length === 0) {
            // 尝试从链接中提取
            const links = document.querySelectorAll('a[href*="item.jd.com"]');
            return Array.from(links).slice(0, 20).map(a => ({
                name: a.innerText.trim().substring(0, 100),
                link: a.href,
                sku: (a.href.match(/\\d{8,}/) || [''])[0]
            }));
        }

        elements.slice(0, 20).forEach(el => {
            const name = (el.querySelector('.p-name, [class*="title"], [class*="name"]') || el).innerText.trim();
            const price = (el.querySelector('.p-price, [class*="price"]') || {innerText:''}).innerText.trim();
            const comment = (el.querySelector('.p-commit, [class*="comment"], [class*="evaluate"]') || {innerText:''}).innerText.trim();
            const shop = (el.querySelector('.p-shop, [class*="shop"], [class*="store"]') || {innerText:''}).innerText.trim();
            const img = (el.querySelector('img') || {src:'',getAttribute:()=>''});
            const imgSrc = img.src || img.getAttribute('data-lazy-img') || img.getAttribute('data-src') || '';

            items.push({
                name: name.substring(0, 150),
                price: price,
                comments: comment,
                shop: shop,
                img: imgSrc,
                sku: el.getAttribute('data-sku') || ''
            });
        });
        return items;
    }
    """)
    return products

def go_to_search(page, keyword):
    """搜索"""
    # 先打开京东首页
    url = "https://search.jd.com/Search?keyword=" + keyword + "&enc=utf-8"
    print(f"搜索: {keyword}")
    print(f"URL: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(2)
    # 等待商品或登录页
    page.wait_for_load_state("networkidle", timeout=30000)
    time.sleep(3)

    # 检查是否跳转到登录
    current = page.url
    if "login" in current or "passport" in current or "plogin" in current:
        print(f"需要登录! URL: {current}")
        return None

    # 截图
    safe = keyword.replace("/","_").replace("\\","_")
    page.screenshot(path=os.path.join(OUTPUT_DIR, f"search_{safe}.png"))

    # 解析商品
    products = parse_products_from_page(page)
    print(f"找到 {len(products)} 个商品")
    for i, p in enumerate(products[:5]):
        print(f"  [{i}] {p.get('name','')[:60]} | {p.get('price','')}")

    # 保存页面HTML
    with open(os.path.join(OUTPUT_DIR, f"search_{safe}.html"), "w", encoding="utf-8") as f:
        f.write(page.content())

    return products

def search_shop(page, shop_name):
    """搜索店铺"""
    url = f"https://search.jd.com/shop.html?keyword={shop_name}&enc=utf-8"
    print(f"搜索店铺: {shop_name}")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(2)
    page.wait_for_load_state("networkidle", timeout=30000)
    time.sleep(3)

    current = page.url
    if "login" in current or "passport" in current or "plogin" in current:
        print(f"需要登录!")
        return None

    # 截图
    page.screenshot(path=os.path.join(OUTPUT_DIR, f"shop_{shop_name}.png"))

    # 解析店铺
    text = page.evaluate("() => document.body.innerText")
    print(f"页面文本长度: {len(text)}, 前500: {text[:500]}")

    # 保存HTML
    with open(os.path.join(OUTPUT_DIR, f"shop_{shop_name}.html"), "w", encoding="utf-8") as f:
        f.write(page.content())

    return text

def main():
    with sync_playwright() as playwright:
        # 有头模式 - 用户可以看到浏览器
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

        # 尝试加载已保存的 cookies
        has_cookies = load_cookies(context)

        if not has_cookies:
            # 打开京东登录页，等待用户手动登录
            print("\n" + "="*60)
            print("请在浏览器中扫码登录京东账号")
            print("登录完成后按回车继续...")
            print("="*60)
            page.goto("https://passport.jd.com/new/login.aspx", wait_until="domcontentloaded", timeout=60000)
            input()  # 等待用户回车
            save_cookies(context)

        # 开始抓取
        all_products = {}

        # 1. 搜索滴水洗地机
        print("\n===== 抓取: 滴水洗地机 =====")
        prods = go_to_search(page, "滴水洗地机")
        if prods:
            all_products["滴水洗地机"] = prods

        # 2. 搜索 DIISEA
        print("\n===== 抓取: DIISEA =====")
        prods = go_to_search(page, "DIISEA")
        if prods:
            all_products["DIISEA"] = prods

        # 3. 搜索 DIISEA官方旗舰店
        print("\n===== 搜索店铺: DIISEA官方旗舰店 =====")
        search_shop(page, "DIISEA官方旗舰店")

        # 4. 店铺搜索其他关键词
        print("\n===== 搜索店铺: 滴水京东自营 =====")
        search_shop(page, "滴水京东自营")

        # 保存所有结果
        with open(os.path.join(OUTPUT_DIR, "all_products.json"), "w", encoding="utf-8") as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)

        print("\n===== 完成 =====")
        print("浏览器保持打开，可以手动查看。完成后关掉浏览器即可。")
        input("按回车关闭浏览器...")
        save_cookies(context)
        browser.close()

if __name__ == "__main__":
    main()
