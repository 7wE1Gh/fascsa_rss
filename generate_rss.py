import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://sam.gov/supplychainorders"
CHECK_STRING = "There are currently no FASCSA orders in SAM.gov"
FEED_LOG = "rss_log.xml"

def fetch_status():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return CHECK_STRING not in soup.text  # True = change detected
    except Exception as e:
        return f"ERROR: {e}"

def append_rss_item(title, description):
    now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    item = f"""<item>
  <title>{title}</title>
  <link>{URL}</link>
  <pubDate>{now}</pubDate>
  <description>{description}</description>
</item>\n"""
    with open(FEED_LOG, "a", encoding="utf-8") as f:
        f.write(item)

def main():
    result = fetch_status()
    today = datetime.utcnow().strftime("%Y-%m-%d")

    if result is True:
        append_rss_item("FASCSA ORDER ALERT", f"A FASCSA order may have been added. ({today})")
    elif result is False:
        append_rss_item("NO CHANGE", f"No new FASCSA orders detected. ({today})")
    else:
        append_rss_item("ERROR", f"Could not check page: {result} ({today})")

if __name__ == "__main__":
    main()
