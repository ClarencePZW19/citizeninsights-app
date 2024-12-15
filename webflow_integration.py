import requests
import streamlit as st
import datetime
from dateutil import parser

def fetch_meta_data(dataset_id):
        url = f"https://api-production.data.gov.sg/v2/public/api/datasets/{dataset_id}/metadata"
        response = requests.get(url)
        
        if response.status_code == 200:
            metadata = response.json()
            last_updated_at = metadata.get('data', {}).get('lastUpdatedAt', '').lower()
            managed_by = metadata.get('data', {}).get('managedBy', '')

            return last_updated_at, managed_by
        else:
            st.error("Failed to fetch metadata from data.gov.sg.")
            return None


def format_date_for_webflow(date_str):
    try:
        # Parse the date string using dateutil
        dt = parser.parse(date_str)
        # Format to ISO 8601
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    except (ValueError, TypeError):
        st.error("Invalid date format.")
        return None

def update_collection(field_data: dict, dataset_id):
    # Fetch metadata for additional fields
    last_updated_at, managed_by = fetch_meta_data(dataset_id)
    
    # Override or set specific fields
    field_data["author"] = "Citizen Insights AI"
    field_data["data-source"] = f"https://data.gov.sg/datasets/{dataset_id}/view"
    field_data["reporting-agency"] = managed_by
    field_data["last-updated"] = format_date_for_webflow(last_updated_at)

    # Verify that all required fields are present
    is_valid, missing_fields = verify_dictionary_fields(field_data)
    if is_valid:
        url = "https://api.webflow.com/v2/collections/675916f5dab2bcd62c392f72/items"
        headers = {
            "Authorization": "Bearer 3c80a854b7864f53ad11d598080e90974d52b3843ec990e93d5238cb288f68d1",
            "Content-Type": "application/json"
        }
        data = {
            "isArchived": False,
            "isDraft": False,
            "fieldData": field_data
        }
        # Send POST request to Webflow API
        response = requests.post(url, headers=headers, json=data)
        print(response.text)
        return response
    else:
        print(f"Missing fields: {missing_fields}")

def verify_dictionary_fields(data_dict):
    """
    Verify if the dictionary has all the relevant fields.

    Parameters:
        data_dict (dict): The dictionary to be verified.

    Returns:
        bool: True if all required fields are present, False otherwise.
        list: A list of missing fields if any.
    """
    # Define the set of required fields
    required_fields = {
        "data-source",
        "last-updated",
        # "key-visualisation-link",
        "name",
        # "author",
        "reporting-agency",
        "key-insight",
        "slug",
        "data-source-name",
    }
    # Get the missing fields
    missing_fields = required_fields - data_dict.keys()

    # Return the result
    if not missing_fields:
        return True, None  # All required fields are present
    else:
        return False, list(missing_fields)  # Return missing fields



