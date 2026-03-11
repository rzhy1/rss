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

cards = re.findall(r'<li class="card".*?</li>', html, re.S)

items = []

for c in cards:

    id_match = re.search(r'data-id="(\d+)"', c)
    title_match = re.search(r'<p class="ell_two p_two title">\s*(.*?)\s*</p>', c, re.S)
    intro_match = re.search(r'<p class="intro ell_two">\s*(.*?)\s*</p>', c, re.S)

    if not id_match or not title_match:
        continue

    nid = id_match.group(1)

    title = re.sub("<.*?>", "", title_match.group(1)).strip()

    intro = ""
    if intro_match:
        intro = re.sub("<.*?>", "", intro_match.group(1)).strip()

    link = f"https://www.laoyaoba.com/n/{nid}"

    items.append({
        "title": title,
        "link": link,
        "desc": intro or title
    })

rss_items = ""

for i in items[:20]:

    pub = time.strftime(
        "%a, %d %b %Y %H:%M:%S GMT",
        time.gmtime()
    )

    rss_items += f"""
    <item>
        <title>{escape(i['title'])}</title>
        <link>{i['link']}</link>
        <guid>{i['link']}</guid>
        <description>{escape(i['desc'])}</description>
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

print("rss.xml generated:", len(items))
