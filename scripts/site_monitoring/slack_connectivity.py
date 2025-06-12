import os
import sys
import logging
import requests
from pathlib import Path

# Add the base_setup directory to the Python path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import (
    load_config,
    get_tableau_server_and_auth,
    setup_logging
)

# Setup logging
setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger('tableau_automation')


def slack_integration_with_webhook():
    try:
        # Load configuration
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        tableau_cfg = config["tableau"]
        slack_url = config["slack"].get("webhook_url")

        if not slack_url:
            raise ValueError("Slack webhook URL is missing in config.")

        # Authenticate with Tableau
        server, auth = get_tableau_server_and_auth(config)
        with server.auth.sign_in(auth):
            auth_token = server.auth_token
            site_id = server.site_id
            api_version = "3.10"  # Ensure your site supports this or adjust accordingly

            webhook_endpoint = f"{tableau_cfg['server_url']}/api/{api_version}/sites/{site_id}/webhooks"

            payload = {
                "webhook": {
                    "name": "Slack Integration Test",
                    "event": "WorkbookCreated",
                    "webhook-destination": {
                        "webhook-destination-http": {
                            "method": "POST",
                            "url": slack_url
                        }
                    }
                }
            }

            headers = {
                "X-Tableau-Auth": auth_token,
                "Content-Type": "application/json"
            }

            # Send webhook creation request
            logger.info(f"Sending webhook creation request to {webhook_endpoint}")
            response = requests.post(webhook_endpoint, headers=headers, json=payload)

            if response.status_code == 201:
                return {
                    "success": True,
                    "message": "Slack webhook integration Exists."
                }

    except requests.HTTPError as http_err:
        logger.error(f"HTTP error: {http_err}", exc_info=True)
        print(f"❌ HTTP Error: {http_err}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    slack_integration_with_webhook()
