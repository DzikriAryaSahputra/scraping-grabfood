import requests
from src.scrapers.grabfood import GrabFoodScraper

def test_dynamic_latlng():
    scraper = GrabFoodScraper()
    with open(scraper.curl_file, "r", encoding="utf-8") as f:
        curl_cmd = f.read().strip()
        
    url, headers, payload = scraper.parse_curl_shlex(curl_cmd)
    
    if 'accept-encoding' in headers:
        del headers['accept-encoding']
        
    # Change latlng to Jakarta (Monas)
    payload["latlng"] = "-6.175392,106.827153"
    payload["offset"] = 0
    
    session = requests.Session()
    resp = session.post(url, headers=headers, json=payload, timeout=10)
    
    print("Status:", resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        search_result = data.get("searchResult", {})
        merchants = search_result.get("searchMerchants", [])
        print("Found merchants:", len(merchants))
        if merchants:
            print("First merchant:", merchants[0].get("address", {}).get("name"))
    else:
        print(resp.text)

if __name__ == "__main__":
    test_dynamic_latlng()
