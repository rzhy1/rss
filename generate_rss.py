import urllib.request
import json
import time
from xml.sax.saxutils import escape

# 1. 模拟 POST 请求，获取最新数据
url = "https://www.laoyaoba.com/api/category/list"
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
data = json.dumps({
    "source": "pc",
    "is_vip": 2,
    "limit": 20,
    "category_show": 1
}).encode('utf-8')

req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        res_body = response.read().decode('utf-8')
        json_data = json.loads(res_body)
except Exception as e:
    print(f"Error fetching data: {e}")
    exit(1)

# 2. 将 JSON 转换为标准 RSS 格式
rss_items = ""
if "data" in json_data and "list" in json_data["data"]:
    for item in json_data["data"]["list"]:
        title = escape(item.get("title", ""))
        link = f"https://www.laoyaoba.com/n/{item.get('id', '')}"
        # 提取简介并转义特殊字符防止报错
        summary = escape(item.get("summary", "") or item.get("intro", ""))
        pub_time = item.get("publish_time", int(time.time()))
        
        # 转换为 RSS 要求的标准时间格式
        pub_date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(pub_time))
        
        rss_items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <guid>{link}</guid>
            <description>{summary}</description>
            <pubDate>{pub_date}</pubDate>
        </item>"""

rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>集微网 - 最新</title>
        <link>https://www.laoyaoba.com/jwnews</link>
        <description>利用 GitHub Actions 自动生成的集微网 RSS</description>
        {rss_items}
    </channel>
</rss>
"""

# 3. 将生成的 XML 写入文件
with open("rss.xml", "w", encoding="utf-8") as f:
    f.write(rss_xml)

print("rss.xml generated successfully!")
