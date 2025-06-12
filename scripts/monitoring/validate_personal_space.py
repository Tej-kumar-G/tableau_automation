import os
import sys
import logging
from pathlib import Path
import requests

# Add base_setup directory to Python path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, get_tableau_server_and_auth, setup_logging

# Setup logging
logger = setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))


def validate_personal_spaces():
    config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
    server, auth = get_tableau_server_and_auth(config)

    with server.auth.sign_in(auth):
        logger.info("Connected to Tableau Cloud")
        auth_token = server.auth_token
        site_id = server.site_id
        server_url = config["tableau"]["server_url"]
        api_version = "3.26"  # or adjust as needed

        headers = {
            "X-Tableau-Auth": auth_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        results = []

        try:
            logger.info("Fetching personal spaces...")
            url = f"{server_url}/api/{api_version}/sites/{site_id}/projects?pageSize=1000"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            project_data = response.json()

            all_projects = project_data.get("projects", {}).get("project", [])
            for p in all_projects:
                logger.debug(
                    f"Project: {p['name']} | personalSpace: {p.get('personalSpace')} | Owner: {p.get('owner', {}).get('id')}")
            personal_spaces = [p for p in all_projects if p.get("personalSpace") is True]

            logger.info(f"Found {len(personal_spaces)} personal space(s).")
            results = [
                {
                    "name": p["name"],
                    "id": p["id"],
                    "owner_id": p.get("owner", {}).get("id", "N/A")
                }
                for p in personal_spaces
            ]
        except Exception as e:
            logger.error(f"Failed to fetch personal spaces: {e}")

        return {
            "success": True,
            "results": results,
        }


if __name__ == "__main__":
    personal_spaces = validate_personal_spaces()

    print("\n=== Personal Spaces ===")
    if personal_spaces:
        for ps in personal_spaces:
            print(f"- {ps['name']} (ID: {ps['id']}, Owner: {ps['owner_id']})")
    else:
        print("No personal spaces found.")