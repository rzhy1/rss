import urllib.request
import urllib.parse
import json
import time
from xml.sax.saxutils import escape

API = "https://www.laoyaoba.com/api/category/list"

LIMIT = 50

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://www.laoyaoba.com/jwnews",
    "Origin": "https://www.laoyaoba.com"
}

payload = {
    "source": "pc",
    "is_vip": "2",
    "limit": str(LIMIT),
    "category_show": "1"
}

data = urllib.parse.urlencode(payload).encode()

req = urllib.request.Request(API, data=data, headers=headers)

with urllib.request.urlopen(req, timeout=20) as r:
    res = r.read().decode()

print("API response:", res[:300])

j = json.loads(res)

items = j.get("data", {}).get("list", [])

if not items:
    print("ERROR: no items returned")
    exit(1)

rss_items = ""

for i in items:

    title = escape(i.get("title", ""))
    nid = i.get("id")

    if not nid:
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
