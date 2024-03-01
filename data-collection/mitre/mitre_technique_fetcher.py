import argparse
import requests
import yaml
import re
from bs4 import BeautifulSoup

# Scrape MITRE ATT&CK Techniques from a webpage
def scrape_mitre_techniques(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch webpage")

    soup = BeautifulSoup(response.text, 'html.parser')
    scraped_ids = set()

    for row in soup.find_all("tr", class_=["technique", "sub technique"]):
        link_tag = row.find("a", href=True)
        if link_tag:
            link = link_tag['href']
            id_match = re.search(r'/techniques/(T\d+)(/\d+)?', link)
            if id_match:
                tech_id = id_match.group(1)
                if id_match.group(2):
                    subtech_id = id_match.group(2).replace('/', '.')
                    full_tech_id = f"{tech_id}{subtech_id}"
                else:
                    full_tech_id = tech_id
                scraped_ids.add(full_tech_id)

    return scraped_ids

# Fetch attack data from GitHub
def fetch_attack_data(version: str):
    url = f"https://raw.githubusercontent.com/mitre/cti/{version}/enterprise-attack/enterprise-attack.json"
    response = requests.get(url, timeout=60)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    return response.json()

# Fetch available versions from GitHub
def fetch_attack_versions():
    url = "https://api.github.com/repos/mitre/cti/tags"
    response = requests.get(url, timeout=60)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch version data: {response.status_code}")

    tags = response.json()
    return [tag['name'] for tag in tags if 'ATT&CK-' in tag['name']]

# Find the highest matching tag for a version
def find_highest_matching_tag(version, tags):
    version_pattern = re.compile(f"ATT&CK-v{version.replace('v', '')}\.?\d*")
    matching_tags = [tag for tag in tags if version_pattern.match(tag)]
    return sorted(matching_tags, key=lambda x: x.split('-v')[-1], reverse=True)[0] if matching_tags else None

def extract_techniques(data, filtered_ids, version):
    techniques = {"mitre": []}
    technique_objects = {}  # Store the techniques and sub-techniques

    # Define the base URL including the version
    base_url = f"https://attack.mitre.org/versions/v{version}/techniques/"

    # Collect all techniques and sub-techniques
    for obj in data.get("objects", []):
        if obj.get("type") == "attack-pattern":
            tech_id = obj.get("external_references", [{}])[0].get("external_id")
            if tech_id in filtered_ids:
                tactics = [phase['phase_name'] for phase in obj.get('kill_chain_phases', []) if phase.get('kill_chain_name') == 'mitre-attack']
                tech_info = {
                    "id": tech_id,
                    "name": obj.get("name"),
                    "tactics": tactics,
                    "link": f"{base_url}{tech_id.replace('.', '/')}"
                }
                technique_objects[obj["id"]] = tech_info  # Store technique by its internal ID

    # Process relationships to identify sub-techniques
    for rel in data.get("objects", []):
        if rel.get("type") == "relationship" and rel.get("relationship_type") == "subtechnique-of":
            subtech_id = rel["source_ref"]
            parent_id = rel["target_ref"]
            if subtech_id in technique_objects and parent_id in technique_objects:
                parent_name = technique_objects[parent_id]["name"]
                technique_objects[subtech_id]["name"] = f"{parent_name}: {technique_objects[subtech_id]['name']}"
                # Update the link to include the version
                technique_objects[subtech_id]["link"] = f"{base_url}{technique_objects[subtech_id]['id'].replace('.', '/')}"

    # Add only the values to the final list
    for tech_obj in technique_objects.values():
        techniques["mitre"].append(tech_obj)

    return techniques




# Save data as YAML
def save_as_yaml(techniques, filename):
    with open(f"{filename}.yaml", 'w') as file:
        yaml.dump(techniques, file)

def main():
    parser = argparse.ArgumentParser(description="Fetch MITRE ATT&CK Techniques and filter by provided URL.")
    parser.add_argument("--url", required=True, help="URL of the MITRE ATT&CK Techniques page")
    parser.add_argument("--filename", default="output", help="Base output filename without extension")
    args = parser.parse_args()

    url_version_match = re.search(r"/versions/(v\d+)/techniques/enterprise/", args.url)
    if not url_version_match:
        raise ValueError("Invalid URL format. Please provide a valid MITRE ATT&CK URL.")

    url_version = url_version_match.group(1)
    tags = fetch_attack_versions()
    highest_tag = find_highest_matching_tag(url_version, tags)
    if not highest_tag:
        raise ValueError("No matching version tag found in the GitHub repository.")

    scraped_ids = scrape_mitre_techniques(args.url)
    attack_data = fetch_attack_data(highest_tag)
    version = url_version_match.group(1).replace('v', '')  # Extract the version number from the URL
    filtered_techniques = extract_techniques(attack_data, scraped_ids, version)

    print(f"Total techniques after filtering: {len(filtered_techniques['mitre'])}")
    save_as_yaml(filtered_techniques, args.filename)

if __name__ == "__main__":
    main()
