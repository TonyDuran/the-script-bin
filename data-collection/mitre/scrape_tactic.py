import argparse
import requests
from bs4 import BeautifulSoup

def scrape_mitre_tactics(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch webpage")

    soup = BeautifulSoup(response.text, 'html.parser')
    tactics = []

    for row in soup.select("tbody tr"):
        id_cell, name_cell = row.find_all("td")[:2]
        if id_cell and name_cell and id_cell.find("a"):
            id_text = id_cell.get_text(strip=True)
            name_text = name_cell.get_text(strip=True)
            link = id_cell.find("a", href=True)["href"]
            short_name = name_text.lower().replace(' ', '-')
            tactics.append({'ID': id_text, 'URL': f'https://attack.mitre.org{link}', 'short_name': short_name})

    return tactics

def main():
    parser = argparse.ArgumentParser(description="Scrape MITRE ATT&CK Tactics from a provided URL.")
    parser.add_argument("url", help="URL to scrape for MITRE ATT&CK Tactics")
    args = parser.parse_args()

    tactics = scrape_mitre_tactics(args.url)
    for tactic in tactics:
        print(tactic)

if __name__ == "__main__":
    main()
