import os
import sys
from pathlib import Path

import requests

# Add base_setup directory to Python path
base_setup_path = str(Path(__file__).parent.parent.parent / "base_setup")
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, get_tableau_server_and_auth, setup_logging
from base_setup.utils.email_utils import send_email

# Setup logging
logger = setup_logging(os.path.join(base_setup_path, "config", "logging_config.yaml"))


def get_datastore_id(server, data_source_name):
    logger.info(f"🔍 Looking up data source ID for '{data_source_name}'...")
    datasources, _ = server.datasources.get()
    for ds in datasources:
        if ds.name.strip().lower() == data_source_name.strip().lower():
            logger.info(f"✅ Found Data Source: {ds.name} -> ID: {ds.id}")
            return ds.id
    logger.error(f"❌ Data source '{data_source_name}' not found!")
    return None


def is_pulse_enabled(server_url, site_id, auth_token, api_version="3.26"):
    pulse_url = f"{server_url}/api/{api_version}/sites/{site_id}/pulse/metric-definitions"
    headers = {
        "X-Tableau-Auth": auth_token,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    try:
        logger.info("📡 Checking if Tableau Pulse is enabled...")
        resp = requests.get(pulse_url, headers=headers)
        if resp.status_code == 404:
            logger.warning("🚫 Pulse API not enabled for this site.")
            return False
        resp.raise_for_status()
        logger.info("✅ Pulse is enabled.")
        return True
    except Exception as e:
        logger.error(f"🔥 Pulse check failed: {e}")
        return False


def create_pulse_metric(datastore_name: str | None = None):
    config = load_config(os.path.join(base_setup_path, "config", "config.yaml"))
    server, auth = get_tableau_server_and_auth(config)
    datastore_name = datastore_name if datastore_name else config["test_data"]["datastore_name"]
    metric_name = f"AutoMetric_{datastore_name}"
    metric_expression = "COUNTD([Order ID])"

    with server.auth.sign_in(auth):
        logger.info("🔐 Authenticated to Tableau Cloud")
        auth_token = server.auth_token
        site_id = server.site_id
        server_url = config["tableau"]["server_url"]

        # 1. Check if Pulse is enabled
        if not is_pulse_enabled(server_url, site_id, auth_token):
            logger.error("❌ Aborting — Pulse is not enabled on this site.")
            subject = config["email"]["mail_sub"]
            body = """
            <p><strong style="color:red;">Pulse feature is not enabled</strong></p>
            <p>Please ask Tableau Cloud administrator to enable Tableau Pulse API for your site.</p>
            """
            send_email(subject, body, config)
            return {
                "success": False,
                "message": "Pulse is not enabled on this site."
            }

        # 2. Lookup data source ID
        datastore_id = get_datastore_id(server, datastore_name)
        if not datastore_id:
            logger.error("⚠️ Aborting metric creation — data source not found.")
            return False

        # 3. Compose GraphQL mutation
        graphql_url = f"{server_url}/api/metadata/graphql"
        headers = {
            "X-Tableau-Auth": auth_token,
            "Content-Type": "application/json"
        }

        graphql_query = """
        mutation CreatePulseMetric {
          pulseCreateMetric(input: {
            name: "%s",
            description: "Automated metric from script",
            dataSourceId: "%s",
            expression: "%s"
          }) {
            metric {
              id
              name
            }
          }
        }
        """ % (metric_name, datastore_id, metric_expression)

        payload = {
            "query": graphql_query
        }

        # 4. Execute the request
        try:
            logger.info(f"📤 Creating Pulse metric '{metric_name}' via GraphQL...")
            response = requests.post(graphql_url, headers=headers, json=payload)

            if response.status_code != 200 or "errors" in response.json():
                logger.error(f"❌ GraphQL error: {response.status_code} | {response.text}")
                raise Exception("GraphQL metric creation failed")

            logger.info("✅ Pulse metric created successfully via GraphQL.")
            return True
        except Exception as e:
            logger.error(f"🔥 Exception during GraphQL metric creation: {e}")
            subject = config["email"]["mail_sub"]
            body = f"""
            <p><strong style="color:red;">Pulse metric creation failed!</strong></p>
            <p>Error: {e}</p>
            """
            send_email(subject, body, config)
            return False


if __name__ == "__main__":
    success = create_pulse_metric()
    if success:
        print("✅ Pulse metric created successfully.")
    else:
        print("❌ Failed to create Pulse metric.")
