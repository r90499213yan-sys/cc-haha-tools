# -*- coding: utf-8 -*-
"""
京东数据采集 v10 - 通过搜索引擎间接获取京东商品信息
"""
import json, os, time, sys, requests, re
from urllib.parse import quote
sys.stdout.reconfigure(encoding='utf-8')

PROXY = "http://127.0.0.1:7890"
OUTPUT_DIR = r"D:\claude code项目文件\滴水科技调研"
proxies = {"http": PROXY, "https": PROXY}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def search_bing(query, count=20):
    """通过必应搜索京东商品"""
    url = f"https://www.bing.com/search?q={quote(query)}+site:item.jd.com&count={count}"
    try:
        r = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        return r.text
    except Exception as e:
        print(f"必应搜索错误: {e}")
        return ""

def search_google(query, count=20):
    """通过谷歌搜索京东商品"""
    url = f"https://www.google.com/search?q={quote(query)}+site:item.jd.com&num={count}"
    try:
        r = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        return r.text
    except Exception as e:
        print(f"谷歌搜索错误: {e}")
        return ""

def search_baidu(query):
    """通过百度搜索京东商品"""
    url = f"https://www.baidu.com/s?wd={quote(query)}+site:item.jd.com"
    try:
        r = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        return r.text
    except Exception as e:
        print(f"百度搜索错误: {e}")
        return ""

def extract_jd_items(html):
    """从搜索结果提取京东item链接"""
    # 匹配 item.jd.com/数字.html
    pattern = r'item\.jd\.com/(\d+)\.html'
    ids = re.findall(pattern, html)
    return list(set(ids))

def try_jd_mobile_api(sku_ids):
    """批量查询京东商品信息 - 通过移动端接口"""
    results = []
    for sku in sku_ids[:30]:
        url = f"https://item.m.jd.com/product/{sku}.html"
        try:
            r = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
                "Referer": "https://m.jd.com/"
            }, proxies=proxies, timeout=15, allow_redirects=True)

            if r.status_code == 200:
                html = r.text
                # 提取标题
                title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
                title = title_match.group(1).strip() if title_match else ""

                # 提取JSON数据
                json_matches = re.findall(r'\{[^}]*"name"[^}]*\}', html)
                price_info = ""
                for jm in json_matches:
                    if 'price' in jm.lower() or 'name' in jm.lower():
                        price_info += jm[:200] + "\n"

                # 提取页面文本中的关键信息
                text = re.sub(r'<[^>]+>', ' ', html)
                text = re.sub(r'\s+', ' ', text)[:500]

                results.append({
                    "sku": sku,
                    "title": title,
                    "url": f"https://item.jd.com/{sku}.html",
                    "text_preview": text[:300],
                    "price_info": price_info[:300]
                })
                print(f"  [{sku}] {title[:80]}")
        except Exception as e:
            print(f"  [{sku}] 错误: {e}")

    return results

def main():
    all_sku_ids = set()

    # 1. 通过必应搜索
    print("=== 必应搜索: 滴水洗地机 ===")
    html = search_bing("滴水洗地机 京东")
    ids = extract_jd_items(html)
    print(f"找到 {len(ids)} 个京东商品ID")
    all_sku_ids.update(ids)

    # 2. 搜索 DIISEA
    print("\n=== 必应搜索: DIISEA ===")
    html2 = search_bing("DIISEA 洗地机 京东")
    ids2 = extract_jd_items(html2)
    print(f"找到 {len(ids2)} 个京东商品ID")
    all_sku_ids.update(ids2)

    # 3. 搜索不同产品型号
    keywords = [
        "滴水洗地机 D7",
        "滴水洗地机 S8",
        "滴水洗地机 DS",
        "滴水洗地机 D3",
        "DIISEA 洗地机",
    ]
    for kw in keywords:
        print(f"\n=== 必应搜索: {kw} ===")
        h = search_bing(f"{kw} 京东")
        ids = extract_jd_items(h)
        print(f"找到 {len(ids)} 个京东商品ID")
        all_sku_ids.update(ids)
        time.sleep(1)

    # 4. 搜索 DIISEA官方旗舰店
    print("\n=== 必应搜索: DIISEA官方旗舰店 ===")
    h = search_bing("DIISEA官方旗舰店 京东")
    shop_ids = extract_jd_items(h)
    all_sku_ids.update(shop_ids)
    # 也提取店铺ID
    shop_pattern = r'mall\.jd\.com/index-(\d+)\.html'
    mall_ids = re.findall(shop_pattern, h)
    print(f"找到 {len(shop_ids)} 个商品ID, {len(mall_ids)} 个店铺ID")
    for mid in mall_ids:
        print(f"  店铺ID: {mid}")

    print(f"\n=== 去重后共 {len(all_sku_ids)} 个SKU ===")
    sorted_ids = sorted(all_sku_ids)
    print(f"SKU列表: {sorted_ids[:20]}")

    # 现在访问每个商品页面获取详细信息
    print("\n=== 获取商品详细信息 ===")
    products = try_jd_mobile_api(sorted_ids)

    # 保存结果
    with open(os.path.join(OUTPUT_DIR, "jd_products_from_search.json"), "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUTPUT_DIR, "all_sku_ids.json"), "w", encoding="utf-8") as f:
        json.dump({"ids": sorted_ids, "count": len(sorted_ids)}, f, ensure_ascii=False)

    print(f"\n完成! 共 {len(products)} 个商品")
    print(f"结果保存到: jd_products_from_search.json")

if __name__ == "__main__":
    main()
