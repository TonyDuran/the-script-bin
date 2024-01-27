#!/usr/bin/env python3
import argparse
import json
import pandas as pd
import yaml

def read_data(file_path, file_type):
    if file_type == 'json':
        with open(file_path, 'r') as file:
            return pd.read_json(file)
    elif file_type == 'csv':
        return pd.read_csv(file_path)
    elif file_type == 'yaml':
        with open(file_path, 'r') as file:
            return pd.json_normalize(yaml.safe_load(file))
    else:
        raise ValueError("Unsupported file type")

def write_data(data, output_format, output_file):
    if output_format == 'json':
        data.to_json(output_file, orient='records', indent=4)
    elif output_format == 'csv':
        data.to_csv(output_file, index=False)
    elif output_format == 'yaml':
        with open(output_file, 'w') as file:
            yaml.dump(json.loads(data.to_json(orient='records')), file)
    else:
        raise ValueError("Unsupported output format")

def main():
    parser = argparse.ArgumentParser(description='Convert file formats.')
    parser.add_argument('-f', '--file', required=True, help='Path to the input file')
    parser.add_argument('--format', required=True, choices=['json', 'csv', 'yaml'], help='Format to convert to')
    args = parser.parse_args()

    file_type = args.file.split('.')[-1]
    data = read_data(args.file, file_type)
    output_file = args.file.rsplit('.', 1)[0] + '.' + args.format
    write_data(data, args.format, output_file)

if __name__ == "__main__":
    main()

