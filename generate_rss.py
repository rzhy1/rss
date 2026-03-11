import urllib.request
import re
import time
from xml.sax.saxutils import escape

URL = "https://www.laoyaoba.com/jwnews"
MAX_ITEMS = 30

headers = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_html():

    req = urllib.request.Request(URL, headers=headers)

    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


def parse_news(html):

    cards = re.findall(r'<li[^>]*class="card"[^>]*>.*?</li>', html, re.S)

    items = []
    seen = set()

    for c in cards:

        id_match = re.search(r'data-id="(\d+)"', c)
        title_match = re.search(r'class="ell_two p_two title">\s*(.*?)\s*</p>', c, re.S)
        intro_match = re.search(r'class="intro ell_two">\s*(.*?)\s*</p>', c, re.S)
        time_match = re.search(r'class="time[^>]*>\s*.*?(\d+)\s*(分钟|小时|天)前', c)

        if not id_match or not title_match:
            continue

        nid = id_match.group(1)

        if nid in seen:
            continue
        seen.add(nid)

        title = re.sub("<.*?>", "", title_match.group(1)).strip()

        intro = ""
        if intro_match:
            intro = re.sub("<.*?>", "", intro_match.group(1)).strip()

        pub_time = time.time()

        if time_match:

            value = int(time_match.group(1))
            unit = time_match.group(2)

            if unit == "分钟":
                pub_time -= value * 60
            elif unit == "小时":
                pub_time -= value * 3600
            elif unit == "天":
                pub_time -= value * 86400

        link = f"https://www.laoyaoba.com/n/{nid}"

        items.append({
            "title": title,
            "link": link,
            "desc": intro or title,
            "time": pub_time
        })

    return items[:MAX_ITEMS]


def build_rss(items):

    rss_items = ""

    for i in items:

        pub = time.strftime(
            "%a, %d %b %Y %H:%M:%S GMT",
            time.gmtime(i["time"])
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

    return f"""<?xml version="1.0" encoding="UTF-8"?>
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


def main():

    html = fetch_html()

    items = parse_news(html)

    if not items:
        raise RuntimeError("No news items parsed")

    rss = build_rss(items)

    with open("rss.xml", "w", encoding="utf-8") as f:
        f.write(rss)

    print("rss.xml generated:", len(items))


if __name__ == "__main__":
    main()
