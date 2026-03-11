import urllib.request
import json
import time
import re
from xml.sax.saxutils import escape

API_URL = "https://www.laoyaoba.com/api/category/list"
WEB_URL = "https://www.laoyaoba.com/jwnews"
LIMIT = 20

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/json; charset=utf-8",
    "Referer": "https://www.laoyaoba.com/",
    "Origin": "https://www.laoyaoba.com",
    "Accept": "application/json, text/plain, */*"
}


def fetch(url, data=None, retry=3):
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers=headers)
            if data:
                req.data = json.dumps(data).encode("utf-8")
                req.method = "POST"

            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8")

        except Exception as e:
            print("fetch error:", e)
            time.sleep(3)

    return ""


def fetch_api():
    print("try API...")

    data = {
        "source": "pc",
        "is_vip": 2,
        "limit": LIMIT,
        "category_show": 1
    }

    res = fetch(API_URL, data)

    if not res:
        return []

    try:
        j = json.loads(res)
    except:
        return []

    items = j.get("data", {}).get("list", [])

    result = []

    for i in items:

        nid = i.get("id")
        title = i.get("title", "").strip()

        if not nid or not title:
            continue

        link = f"https://www.laoyaoba.com/n/{nid}"

        summary = i.get("summary") or i.get("intro") or title

        pub_time = i.get("publish_time", int(time.time()))

        result.append({
            "title": title,
            "link": link,
            "desc": summary,
            "time": pub_time
        })

    return result


def fetch_web():
    print("fallback to web...")

    html = fetch(WEB_URL)

    if not html:
        return []

    pattern = re.findall(r'<a href="/n/(\d+)"[^>]*>(.*?)</a>', html)

    seen = set()
    result = []

    for nid, title in pattern:

        if nid in seen:
            continue
        seen.add(nid)

        title = re.sub("<.*?>", "", title).strip()

        if not title:
            continue

        link = f"https://www.laoyaoba.com/n/{nid}"

        result.append({
            "title": title,
            "link": link,
            "desc": title,
            "time": int(time.time())
        })

        if len(result) >= LIMIT:
            break

    return result


# 1 获取数据
items = fetch_api()

if not items:
    items = fetch_web()

print("items:", len(items))

# 2 排序
items = sorted(items, key=lambda x: x["time"], reverse=True)[:LIMIT]

# 3 生成 RSS
rss_items = ""

for i in items:

    pub_date = time.strftime(
        "%a, %d %b %Y %H:%M:%S GMT",
        time.gmtime(i["time"])
    )

    rss_items += f"""
    <item>
        <title>{escape(i['title'])}</title>
        <link>{i['link']}</link>
        <guid>{i['link']}</guid>
        <description>{escape(i['desc'])}</description>
        <pubDate>{pub_date}</pubDate>
    </item>
"""


rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>集微网 - 最新</title>
<link>https://www.laoyaoba.com/jwnews</link>
<description>GitHub Actions 自动生成 RSS</description>
<lastBuildDate>{time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())}</lastBuildDate>
{rss_items}
</channel>
</rss>
"""

with open("rss.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("rss.xml generated successfully!")
