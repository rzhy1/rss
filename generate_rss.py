import urllib.request
import re
import time
from xml.sax.saxutils import escape

URL = "https://www.laoyaoba.com/jwnews"

headers = {
    "User-Agent": "Mozilla/5.0"
}

req = urllib.request.Request(URL, headers=headers)

with urllib.request.urlopen(req, timeout=20) as r:
    html = r.read().decode("utf-8")

# 提取新闻ID
ids = re.findall(r'/n/(\d{6,})', html)

# 去重
ids = list(dict.fromkeys(ids))[:20]

rss_items = ""

for nid in ids:

    link = f"https://www.laoyaoba.com/n/{nid}"

    pub = time.strftime(
        "%a, %d %b %Y %H:%M:%S GMT",
        time.gmtime()
    )

    rss_items += f"""
    <item>
        <title>集微网新闻 {nid}</title>
        <link>{link}</link>
        <guid>{link}</guid>
        <description>{link}</description>
        <pubDate>{pub}</pubDate>
    </item>
"""

rss = f"""<?xml version="1.0" encoding="UTF-8"?>
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
    f.write(rss)

print("rss.xml generated:", len(ids))
