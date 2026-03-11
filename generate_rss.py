import urllib.request
import time
import re
from xml.sax.saxutils import escape

URL = "https://www.laoyaoba.com/jwnews"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html"
}

def fetch(url, retry=3):
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            print("fetch error:", e)
            time.sleep(5)
    return ""

html = fetch(URL)

rss_items = ""

# 解析新闻
pattern = re.findall(r'<a href="/n/(\d+)"[^>]*>(.*?)</a>', html)

seen = set()

for nid, title in pattern:

    if nid in seen:
        continue
    seen.add(nid)

    title = re.sub("<.*?>", "", title).strip()

    if not title:
        continue

    link = f"https://www.laoyaoba.com/n/{nid}"

    pub_date = time.strftime(
        "%a, %d %b %Y %H:%M:%S GMT",
        time.gmtime()
    )

    rss_items += f"""
    <item>
        <title>{escape(title)}</title>
        <link>{link}</link>
        <guid>{link}</guid>
        <description>{escape(title)}</description>
        <pubDate>{pub_date}</pubDate>
    </item>
"""

rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>集微网 - 最新</title>
<link>https://www.laoyaoba.com/jwnews</link>
<description>GitHub Actions 自动生成 RSS</description>
{rss_items}
</channel>
</rss>
"""

with open("rss.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("rss.xml generated successfully!")
