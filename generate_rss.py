import urllib.request
import json
import time
from xml.sax.saxutils import escape

API = "https://www.laoyaoba.com/api/category/list"

LIMIT = 30

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json;charset=utf-8",
    "Origin": "https://www.laoyaoba.com",
    "Referer": "https://www.laoyaoba.com/jwnews",
    "Accept": "application/json, text/plain, */*"
}

data = {
    "source": "pc",
    "is_vip": 2,
    "limit": LIMIT,
    "category_show": 1
}

req = urllib.request.Request(
    API,
    data=json.dumps(data).encode("utf-8"),
    headers=headers,
    method="POST"
)

with urllib.request.urlopen(req, timeout=20) as r:
    res = r.read().decode()

j = json.loads(res)

items = j["data"]["list"]

rss_items = ""

for i in items:

    title = escape(i["title"])
    nid = i["id"]

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
