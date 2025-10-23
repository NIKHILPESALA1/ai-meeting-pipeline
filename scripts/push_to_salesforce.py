#!/usr/bin/env python3
import os
import json
import requests
from pathlib import Path

SUMMARIES_DIR = "/app/data/summaries"

SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
SF_USERNAME = os.getenv("SF_USERNAME")
SF_PASSWORD = os.getenv("SF_PASSWORD")
SF_INSTANCE_URL = os.getenv("SF_INSTANCE_URL", "https://login.salesforce.com")

# Get OAuth token
data = {
    "grant_type": "password",
    "client_id": SF_CLIENT_ID,
    "client_secret": SF_CLIENT_SECRET,
    "username": SF_USERNAME,
    "password": SF_PASSWORD
}

response = requests.post(f"{SF_INSTANCE_URL}/services/oauth2/token", data=data)
if response.status_code != 200:
    print("Failed to authenticate with Salesforce:", response.text)
    exit(1)

access_token = response.json()["access_token"]
instance_url = response.json()["instance_url"]
headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

# Push all summaries
for file in os.listdir(SUMMARIES_DIR):
    if file.endswith(".json"):
        with open(os.path.join(SUMMARIES_DIR, file), "r") as f:
            payload = json.load(f)

        # Customize Salesforce object API name
        sf_object_url = f"{instance_url}/services/data/v57.0/sobjects/Meeting_Summary__c/"
        response = requests.post(sf_object_url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            print(f"✅ Pushed {file} to Salesforce")
        else:
            print(f"❌ Failed to push {file}: {response.text}")
