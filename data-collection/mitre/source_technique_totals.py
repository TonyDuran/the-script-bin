import requests
from bs4 import BeautifulSoup
import re
import argparse

def scrape_mitre_techniques(url):
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to fetch webpage"

    soup = BeautifulSoup(response.text, 'html.parser')
    techniques = []

    for row in soup.find_all("tr", class_=["technique", "sub technique"]):
        link_tag = row.find("a", href=True)
        if link_tag:
            link = link_tag['href']
            full_url = f'https://attack.mitre.org{link}'
            id_match = re.search(r'/techniques/(T\d+)(/\d+)?', link)
            if id_match:
                tech_id = id_match.group(1)
                if id_match.group(2):  # Sub-technique
                    subtech_id = id_match.group(2).replace('/', '.')
                    full_tech_id = f"{tech_id}{subtech_id}"
                else:  # Main technique
                    full_tech_id = tech_id
                techniques.append({'ID': full_tech_id, 'URL': full_url})

    return techniques

def main():
    parser = argparse.ArgumentParser(description="Scrape MITRE ATT&CK Techniques from a provided URL.")
    parser.add_argument("url", help="URL to scrape for MITRE ATT&CK Techniques")
    args = parser.parse_args()

    techniques = scrape_mitre_techniques(args.url)
    if techniques:
        print(f"Total techniques and sub-techniques: {len(techniques)}")
        for tech in techniques[:10]:  # Display first 10 entries for brevity
            print(tech)
    else:
        print("No techniques found.")

if __name__ == "__main__":
    main()
