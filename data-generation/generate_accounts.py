#!/usr/bin/env python3
import argparse
import random
import string
from faker import Faker
import pandas as pd
import json
import yaml

# Function to generate a random password
def generate_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

# Main function to generate fake data
def generate_fake_data(num, include_fields, output_format, filename):
    fake = Faker()
    data = []

    for _ in range(num):
        entry = {}
        if 'address' in include_fields:
            entry['address'] = fake.address().replace("\n", ", ")
        if 'email' in include_fields:
            entry['email'] = fake.email()
        if 'first_name' in include_fields:
            entry['first_name'] = fake.first_name()
        if 'last_name' in include_fields:
            entry['last_name'] = fake.last_name()
        if 'zip_code' in include_fields:
            entry['zip_code'] = fake.zipcode()
        if 'password' in include_fields:
            entry['password'] = generate_password()

        data.append(entry)

    # Output data in the specified format
    if output_format == 'json':
        with open(f'{filename}.json', 'w') as f:
            json.dump(data, f, indent=4)
    elif output_format == 'yaml':
        with open(f'{filename}.yaml', 'w') as f:
            yaml.dump(data, f)
    elif output_format == 'csv':
        df = pd.DataFrame(data)
        df.to_csv(f'{filename}.csv', index=False)

# Setting up argparse
parser = argparse.ArgumentParser(description='Generate fake data.')
parser.add_argument('num', type=int, help='Number of fake accounts to generate')
parser.add_argument('-f', '--fields', nargs='*', default=['address', 'email', 'first_name', 'last_name', 'zip_code', 'password'], help='Fields to include (address, email, first_name, last_name, zip_code, password)')
parser.add_argument('-o', '--output', choices=['json', 'yaml', 'csv'], default='json', help='Output format (json, yaml, csv)')
parser.add_argument('-n', '--filename', required=True, help='Output filename without extension')

# Parse arguments
args = parser.parse_args()

# Generate fake data
generate_fake_data(args.num, args.fields, args.output, args.filename)

