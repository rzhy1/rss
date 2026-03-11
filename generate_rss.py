import urllib.request
import json
import time
from xml.sax.saxutils import escape

API = "https://www.laoyaoba.com/api/category/list"

LIMIT = 50

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json;charset=utf-8",
    "Origin": "https://www.laoyaoba.com",
    "Referer": "https://www.laoyaoba.com/jwnews",
    "Accept": "application/json, text/plain, */*"
}

payload = {
    "source": "pc",
    "is_vip": 2,
    "limit": LIMIT,
    "category_show": 1
}

req = urllib.request.Request(
    API,
    data=json.dumps(payload).encode("utf-8"),
    headers=headers,
    method="POST"
)

with urllib.request.urlopen(req, timeout=20) as r:
    res = r.read().decode()

print("API response:", res[:500])   # 打印前500字符方便调试

try:
    j = json.loads(res)
except Exception as e:
    print("JSON parse error:", e)
    exit(1)

# 兼容不同结构
items = []

if isinstance(j, dict):
    data = j.get("data")
    if isinstance(data, dict):
        items = data.get("list", [])
    elif isinstance(data, list):
        items = data

if not items:
    print("ERROR: no items returned from API")
    exit(1)

rss_items = ""

for i in items:

    title = escape(i.get("title", ""))
    nid = i.get("id")

    if not nid or not title:
        continue

    link = f"https://www.laoyaoba.com/n/{nid}"

    desc = escape(i.get("summary") or i.get("intro") or title)

    t = i.get("publish_time", int(time.time()))

    pub = time.strftime(
        "%a, %d %b %Y %H:%M:%S GMT",
        time.gmtime(t)
    )

    rss_items += f"""
    <item>
        <title>{title}</title>
        <link>{link}</link>
        <guid>{link}</guid>
        <description>{desc}</description>
        <pubDate>{pub}</pubDate>
    </item>
"""

rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>集微网 - 最新</title>
<link>https://www.laoyaoba.com/jwnews</link>
<description>Auto RSS</description>
<lastBuildDate>{time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())}</lastBuildDate>
{rss_items}
</channel>
</rss>
"""

with open("rss.xml", "w", encoding="utf-8") as f:
    f.write(rss)

print("rss.xml generated:", len(items))
