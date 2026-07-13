# -*- coding: utf-8 -*-
"""
京东数据采集 v9 - 直接调用 API
"""
import json, os, time, sys, requests, re
from urllib.parse import quote, unquote
sys.stdout.reconfigure(encoding='utf-8')

PROXY = "http://127.0.0.1:7890"
OUTPUT_DIR = r"D:\claude code项目文件\滴水科技调研"
proxies = {"http": PROXY, "https": PROXY}
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Referer": "https://m.jd.com/",
    "Accept": "application/json, text/plain, */*"
}

def call_jd_api(appid, functionId, body_dict, extra_params=""):
    """调用京东移动端API"""
    body_str = json.dumps(body_dict, ensure_ascii=False)
    body_encoded = quote(body_str)
    ts = int(time.time() * 1000)
    url = f"https://api.m.jd.com/api?appid={appid}&functionId={functionId}&body={body_encoded}&_={ts}&sceneval=2&gzip=y&loginType=2{extra_params}"
    try:
        r = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        return r.status_code, r.text
    except Exception as e:
        return -1, str(e)

def main():
    # 1. 尝试搜索 API - 多种 functionId
    search_apis = [
        # yinliu_service_display 可能是引流搜索
        ("yinliu", "yinliu_service_display", {"keyword": "滴水洗地机", "page": 1, "pagesize": 20}),
        # m_search 系列
        ("jd-cphdeveloper-m", "m_search", {"keyword": "滴水洗地机", "page": 1}),
        # search 系列
        ("search_h5", "search", {"keyword": "滴水洗地机"}),
        # ware/search
        ("ware_business_h5", "searchPageForJdv", {"keyword": "滴水洗地机"}),
        # 京东搜索核心
        ("search_h5", "search_pc", {"keyword": "滴水洗地机", "page": 1, "pagesize": 20}),
    ]

    for name, func_id, body in search_apis:
        status, text = call_jd_api(name, func_id, body)
        preview = text[:500] if len(text) > 500 else text
        print(f"\n[{name}/{func_id}] Status={status}")
        print(f"  Response: {preview}")
        if status == 200 and len(text) > 100:
            with open(os.path.join(OUTPUT_DIR, f"api_{func_id}.json"), "w", encoding="utf-8") as f:
                f.write(text)

    # 2. 尝试店铺搜索
    print("\n\n=== 店铺搜索 ===")
    shop_apis = [
        ("shop_h5", "searchShopList", {"keyword": "DIISEA"}),
        ("shop_h5", "searchShopList", {"keyword": "滴水"}),
    ]
    for name, func_id, body in shop_apis:
        status, text = call_jd_api(name, func_id, body)
        preview = text[:500] if len(text) > 500 else text
        print(f"[{name}/{func_id}] Status={status}")
        print(f"  Response: {preview}")

    # 3. 尝试获取品牌/店铺页面内容
    # 可能通过店铺ID获取商品
    print("\n\n=== 品牌商品搜索 ===")
    brand_apis = [
        ("search_h5", "brand_search", {"brandId": "DIISEA", "page": 1}),
        ("ware_business_h5", "searchWareByShopId", {"shopId": "1000000000"}),
    ]
    for name, func_id, body in brand_apis:
        status, text = call_jd_api(name, func_id, body)
        preview = text[:500] if len(text) > 500 else text
        print(f"[{name}/{func_id}] Status={status}")
        print(f"  Response: {preview}")

if __name__ == "__main__":
    main()
