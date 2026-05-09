import requests
from src.scrapers.grabfood import GrabFoodScraper

def test_total_count():
    scraper = GrabFoodScraper()
    with open(scraper.curl_file, "r", encoding="utf-8") as f:
        curl_cmd = f.read().strip()
        
    url, headers, payload = scraper.parse_curl_shlex(curl_cmd)
    
    if 'accept-encoding' in headers:
        del headers['accept-encoding']
        
    # Quick ping
    payload["offset"] = 0
    payload["pageSize"] = 1 # Just to ping
    
    session = requests.Session()
    resp = session.post(url, headers=headers, json=payload, timeout=10)
    
    if resp.status_code == 200:
        data = resp.json()
        search_result = data.get("searchResult", {})
        print("Total count keys:", list(search_result.keys()))
        print("Total Count:", search_result.get("totalCount"))
    else:
        print(resp.text)

if __name__ == "__main__":
    test_total_count()
