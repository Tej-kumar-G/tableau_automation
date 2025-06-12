import os
import sys
import logging
import requests
from pathlib import Path

# Add base_setup directory to Python path
base_setup_path = str(Path(__file__).parent.parent.parent / "base_setup")
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, get_tableau_server_and_auth, setup_logging

# Setup logging
logger = setup_logging(os.path.join(base_setup_path, "config", "logging_config.yaml"))

def fetch_pulse_metrics():
    config = load_config(os.path.join(base_setup_path, "config", "config.yaml"))
    server, auth = get_tableau_server_and_auth(config)

    with server.auth.sign_in(auth):
        logger.info("Authenticated to Tableau Cloud")
        auth_token = server.auth_token
        site_id = server.site_id
        server_url = config["tableau"]["server_url"]
        api_version = "3.26"

        url = f"{server_url}/api/{api_version}/sites/{site_id}/pulse/metric-definitions"
        headers = {
            "X-Tableau-Auth": auth_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        try:
            logger.info("Requesting Pulse metric definitions...")
            response = requests.get(url, headers=headers)

            if response.status_code == 404:
                logger.warning("Pulse API is not enabled for this site. Skipping metric audit.")
                return {"enabled": False, "metrics": []}

            response.raise_for_status()
            data = response.json()
            metrics = data.get("metricDefinitions", {}).get("metricDefinition", [])
            logger.info(f"Found {len(metrics)} Pulse metric(s).")
            return {"enabled": True, "metrics": metrics}

        except Exception as e:
            logger.error(f"Error querying Pulse metrics: {e}")
            return {"enabled": False, "metrics": []}


if __name__ == "__main__":
    result = fetch_pulse_metrics()

    if not result["enabled"]:
        print("❌ Tableau Pulse API not enabled for this site.")
    elif not result["metrics"]:
        print("✅ Pulse API enabled, but no metrics defined.")
    else:
        print("\n✅ Tableau Pulse Metrics Found:")
        for m in result["metrics"]:
            print(f"- {m['name']} (ID: {m['id']})")