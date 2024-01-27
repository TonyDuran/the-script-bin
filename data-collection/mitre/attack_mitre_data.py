#!/usr/bin/env python3
import argparse
import requests
import json
import csv
import yaml

def fetch_attack_data():
    url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    return response.json()

def extract_techniques(data):
    techniques = []
    for obj in data.get("objects", []):
        if obj.get("type") == "attack-pattern":
            tech_info = {
                "ID": obj.get("external_references", [{}])[0].get("external_id"),
                "Title": obj.get("name"),
                "URL": obj.get("external_references", [{}])[0].get("url")
            }
            techniques.append(tech_info)
    return techniques

def save_as_json(techniques, filename):
    with open(f"{filename}.json", 'w') as file:
        json.dump(techniques, file, indent=4)

def save_as_yaml(techniques, filename):
    with open(f"{filename}.yaml", 'w') as file:
        yaml.dump(techniques, file)

def save_as_csv(techniques, filename, delimiter=','):
    with open(f"{filename}.csv", 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Title", "URL"], delimiter=delimiter)
        writer.writeheader()
        for tech in techniques:
            writer.writerow(tech)

def main():
    parser = argparse.ArgumentParser(description="Fetch MITRE ATT&CK Techniques and save in different formats.")
    parser.add_argument("--format", choices=["json", "yaml", "csv"], required=True, help="Output format")
    parser.add_argument("--filename", default="output", help="Base output filename without extension")
    parser.add_argument("--delimiter", default=",", help="Delimiter for CSV output (default is comma)")
    args = parser.parse_args()

    attack_data = fetch_attack_data()
    techniques = extract_techniques(attack_data)

    if args.format == "json":
        save_as_json(techniques, args.filename)
    elif args.format == "yaml":
        save_as_yaml(techniques, args.filename)
    elif args.format == "csv":
        save_as_csv(techniques, args.filename, args.delimiter)

if __name__ == "__main__":
    main()

