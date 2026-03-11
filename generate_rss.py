import urllib.request
import json
import re
import time
from xml.sax.saxutils import escape

API_URL = "https://www.laoyaoba.com/api/category/list"
WEB_URL = "https://www.laoyaoba.com/jwnews"

LIMIT = 30
RETRY = 3

headers_api = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json;charset=utf-8",
    "Referer": "https://www.laoyaoba.com/",
    "Origin": "https://www.laoyaoba.com",
    "Accept": "application/json, text/plain, */*"
}

headers_web = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html"
}


def fetch(url, headers, data=None):

    for _ in range(RETRY):

        try:

            if data:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(data).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
            else:
                req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8")

        except Exception as e:
            print("retry:", e)
            time.sleep(3)

    return ""


def parse_time(text):

    now = int(time.time())

    if "分钟前" in text:
        m = int(re.search(r"(\d+)", text).group(1))
        return now - m * 60

    if "小时前" in text:
        h = int(re.search(r"(\d+)", text).group(1))
        return now - h * 3600

    if "天前" in text:
        d = int(re.search(r"(\d+)", text).group(1))
        return now - d * 86400

    return now


def fetch_api():

    print("try API...")

    data = {
        "source": "pc",
        "is_vip": 2,
        "limit": LIMIT,
        "category_show": 1
    }

    res = fetch(API_URL, headers_api, data)

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
        title = (i.get("title") or "").strip()

        if not nid or not title:
            continue

        link = f"https://www.laoyaoba.com/n/{nid}"

        desc = i.get("summary") or i.get("intro") or title

        pub = i.get("publish_time") or int(time.time())

        result.append({
            "title": title,
            "link": link,
            "desc": desc,
            "time": pub
        })

    return result


def fetch_web():

    print("fallback to HTML...")

    html = fetch(WEB_URL, headers_web)

    if not html:
        return []

    cards = re.findall(r'<li class="card".*?</li>', html, re.S)

    result = []

    for c in cards:

        id_match = re.search(r'data-id="(\d+)"', c)
        title_match = re.search(r'<p class="ell_two p_two title">\s*(.*?)\s*</p>', c, re.S)
        intro_match = re.search(r'<p class="intro ell_two">(.*?)</p>', c, re.S)
        time_match = re.search(r'<div class="time.*?>.*?(\d+.*?前)</div>', c, re.S)

        if not id_match or not title_match:
            continue

        nid = id_match.group(1)

        title = re.sub("<.*?>", "", title_match.group(1)).strip()

        intro = ""
        if intro_match:
            intro = re.sub("<.*?>", "", intro_match.group(1)).strip()

        t = int(time.time())
        if time_match:
            t = parse_time(time_match.group(1))

        link = f"https://www.laoyaoba.com/n/{nid}"

        result.append({
            "title": title,
            "link": link,
            "desc": intro or title,
            "time": t
        })

    return result


# -------------------
# 主逻辑
# -------------------

items = fetch_api()

if not items:
    items = fetch_web()

# 去重
seen = set()
unique = []

for i in items:

    if i["link"] in seen:
        continue

    seen.add(i["link"])
    unique.append(i)

items = unique

# 排序
items = sorted(items, key=lambda x: x["time"], reverse=True)[:LIMIT]

if not items:
    print("ERROR: no items fetched")
    exit(1)


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

print("rss.xml generated successfully:", len(items))
