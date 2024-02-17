#!/usr/bin/env python3
import argparse
import requests
import json
import csv
import yaml

def fetch_attack_data(version: str):
    url = f"https://raw.githubusercontent.com/mitre/cti/{version}/enterprise-attack/enterprise-attack.json"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    return response.json()

#NOTE: Not currently being used, but can be helpful for getting all available tactics
def extract_tactics(data):
    tactics = []

    for obj in data.get("objects", []):
        if obj.get("type") == "x-mitre-tactic":
            tactic_info = {
                "ID": obj.get("external_references", [{}])[0].get("external_id"),
                "Name": obj.get("name"),
                "Description": obj.get("description"),
                "URL": obj.get("external_references", [{}])[0].get("url")
            }
            tactics.append(tactic_info)

    return tactics

def extract_techniques(data):
    techniques = {}
    relationships = []

    # First, collect all techniques and sub-techniques
    for obj in data.get("objects", []):
        if obj.get("type") == "attack-pattern":
            tactics = [phase['phase_name'] for phase in obj.get('kill_chain_phases', []) if phase.get('kill_chain_name') == 'mitre-attack']
            tech_info = {
                "ID": obj.get("external_references", [{}])[0].get("external_id"),
                "Technique": obj.get("name"),
                "Tactics": tactics,
                "URL": obj.get("external_references", [{}])[0].get("url")
            }
            techniques[obj['id']] = tech_info
        elif obj.get("type") == "relationship" and obj.get("relationship_type") == "subtechnique-of":
            relationships.append(obj)

    # Now, process relationships to identify sub-techniques
    for rel in relationships:
        subtechnique_id = rel["source_ref"]
        parent_technique_id = rel["target_ref"]

        if subtechnique_id in techniques and parent_technique_id in techniques:
            # Prepend parent technique name to sub-technique
            parent_name = techniques[parent_technique_id]["Technique"]
            techniques[subtechnique_id]["Technique"] = f"{parent_name}: {techniques[subtechnique_id]['Technique']}"

    return list(techniques.values())



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
    parser.add_argument("--version", default="master", help="Delimiter for CSV output (default is comma)")
    args = parser.parse_args()
    attack_data = fetch_attack_data(args.version)
    techniques = extract_techniques(attack_data)

    if args.format == "json":
        save_as_json(techniques, args.filename)
    elif args.format == "yaml":
        save_as_yaml(techniques, args.filename)
    elif args.format == "csv":
        save_as_csv(techniques, args.filename, args.delimiter)

if __name__ == "__main__":
    main()
