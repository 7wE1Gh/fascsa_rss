import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

URL = "https://sam.gov/supplychainorders"
CHECK_STRING = "There are currently no FASCSA orders in SAM.gov"

ITEMS_FILE = "rss_items.xml"
RSS_FILE = "rss_log.xml"

def load_recent_items(limit=30):
    """Reads and returns the most recent `limit` <item> entries from rss_items.xml"""
    if not os.path.exists(ITEMS_FILE):
        return []

    with open(ITEMS_FILE, "r", encoding="utf-8") as f:
        raw = f.read()

    items = raw.strip().split("</item>")
    # Reattach </item> tag and clean up
    items = [item.strip() + "</item>" for item in items if item.strip()]
    return items[-limit:]

def fetch_status():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return CHECK_STRING not in soup.text  # True = alert
    except Exception as e:
        return f"ERROR: {e}"

def create_rss_item(title, description):
    now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    return f"""<item>
  <title>{title}</title>
  <link>{URL}</link>
  <pubDate>{now}</pubDate>
  <description><![CDATA[{description}]]></description>
</item>
"""

def append_item_to_history(item_xml):
    with open(ITEMS_FILE, "a", encoding="utf-8") as f:
        f.write(item_xml + "\n")

def generate_rss_feed():
    now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = load_recent_items()

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>SAM.gov FASCSA Watch</title>
  <link>{URL}</link>
  <description>Daily update on FASCSA Orders</description>
  <language>en-us</language>
  <ttl>1440</ttl>
  <lastBuildDate>{now}</lastBuildDate>
  {''.join(items)}
</channel>
</rss>"""

    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(rss)

def main():
    result = fetch_status()
    today = datetime.utcnow().strftime("%Y-%m-%d")

    if result is True:
        item = create_rss_item("FASCSA ORDER ALERT", f"A FASCSA order may have been added. ({today})")
    elif result is False:
        item = create_rss_item("NO CHANGE", f"No new FASCSA orders detected. ({today})")
    else:
        item = create_rss_item("ERROR", f"Could not check page: {result} ({today})")

    recent_items = load_recent_items()
    recent_items.append(item)
    recent_items = recent_items[-30:]  # Limit to last 30

    with open(ITEMS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(recent_items))

    generate_rss_feed()


if __name__ == "__main__":
    main()
