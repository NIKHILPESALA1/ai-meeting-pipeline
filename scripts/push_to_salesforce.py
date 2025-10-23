#!/usr/bin/env python3
import os
import json
import requests

# Salesforce environment variables
SF_CLIENT_ID = os.environ.get("SF_CLIENT_ID")
SF_CLIENT_SECRET = os.environ.get("SF_CLIENT_SECRET")
SF_USERNAME = os.environ.get("SF_USERNAME")
SF_PASSWORD = os.environ.get("SF_PASSWORD")
SF_INSTANCE_URL = os.environ.get("SF_INSTANCE_URL", "https://login.salesforce.com")

# Directory with summaries
SUMMARIES_DIR = "/app/data/summaries"

# Step 1: Get access token via OAuth2 password grant
token_url = f"{SF_INSTANCE_URL}/services/oauth2/token"
data = {
    "grant_type": "password",
    "client_id": SF_CLIENT_ID,
    "client_secret": SF_CLIENT_SECRET,
    "username": SF_USERNAME,
    "password": SF_PASSWORD
}

resp = requests.post(token_url, data=data)
resp_json = resp.json()
if "access_token" not in resp_json:
    raise Exception(f"Failed to get access token: {resp_json}")

access_token = resp_json["access_token"]
instance_url = resp_json["instance_url"]

# Step 2: Push each summary JSON to Salesforce Custom Object
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

for file in os.listdir(SUMMARIES_DIR):
    if file.endswith(".json"):
        with open(os.path.join(SUMMARIES_DIR, file), "r", encoding="utf-8") as f:
            data_json = json.load(f)

        payload = {
            "Video_Name__c": data_json.get("video_name"),
            "Summary__c": data_json.get("summary"),
            "Action_Items__c": "\n".join(data_json.get("action_items", []))
        }

        api_url = f"{instance_url}/services/data/v57.0/sobjects/Meeting_Summary__c/"
        r = requests.post(api_url, headers=headers, json=payload)

        if r.status_code in [200, 201]:
            print(f"Pushed {file} to Salesforce successfully")
        else:
            print(f"Failed to push {file}: {r.status_code} {r.text}")
