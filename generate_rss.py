import urllib.request
import re
import time
from html import unescape
from xml.sax.saxutils import escape

URL = "https://www.laoyaoba.com/jwnews"
MAX_ITEMS = 30

# 1. 完善请求头，模拟真实浏览器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive"
}

# XML 1.0 非法控制字符（保留 \t \n \r），以及 U+FFFE / U+FFFF
INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\uFFFE\uFFFF]')


def clean_text(s):
    """去 HTML 标签 -> 解码实体 -> 删除 XML 非法控制字符 -> strip"""
    s = re.sub(r'<[^>]+>', '', s)
    s = unescape(s)
    s = INVALID_XML_CHARS.sub('', s)
    return s.strip()


def xml_text(s):
    """写入 XML 前：先删非法控制字符，再做 XML 转义"""
    return escape(INVALID_XML_CHARS.sub('', str(s)))


def fetch_html():
    req = urllib.request.Request(URL, headers=headers)
    
    # 2. 增加重试机制和延长超时时间
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 超时时间延长到 30 秒
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise RuntimeError("获取网页失败，已达到最大重试次数") from e
            time.sleep(5)  # 每次失败后等待 5 秒再试


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

        title = clean_text(title_match.group(1))

        intro = ""
        if intro_match:
            intro = clean_text(intro_match.group(1))

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
        <title>{xml_text(i['title'])}</title>
        <link>{xml_text(i['link'])}</link>
        <guid>{xml_text(i['link'])}</guid>
        <description>{xml_text(i['desc'])}</description>
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

    # 兜底：整份 XML 再清一次非法字符
    rss = INVALID_XML_CHARS.sub("", rss)

    with open("rss.xml", "w", encoding="utf-8") as f:
        f.write(rss)

    print("rss.xml generated:", len(items))


if __name__ == "__main__":
    main()
