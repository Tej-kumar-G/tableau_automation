import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime

# Add base_setup directory to Python path
base_setup_path = str(Path(__file__).parent.parent.parent / "base_setup")
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, get_tableau_server_and_auth, setup_logging

# Setup logging
logger = setup_logging(os.path.join(base_setup_path, "config", "logging_config.yaml"))


def run_metadata_graphql(query: str, variables: dict = None):
    config = load_config(os.path.join(base_setup_path, "config", "config.yaml"))
    server, auth = get_tableau_server_and_auth(config)

    with server.auth.sign_in(auth):
        logger.info("Signed into Tableau Cloud")

        site_id = server.site_id
        token = server.auth_token
        server_url = config["tableau"]["server_url"]

        graphql_url = f"{server_url}/api/metadata/graphql"

        headers = {
            "X-Tableau-Auth": token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "query": query,
            "variables": variables or {}
        }

        try:
            logger.info("Sending GraphQL metadata query...")
            response = requests.post(graphql_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"GraphQL request failed: {e}")
            return None


def get_lineage_for_workbook(workbook_name: str):
    query = """
    query getWorkbookLineage($name: String!) {
      workbooks(filter: {name: $name}) {
        name
        id
        projectName
        upstreamDatasources {
          name
          id
        }
        embeddedDatasources {
          name
          id
        }
        sheets {
          name
          id
        }
        dashboards {
          name
          id
        }
      }
    }
    """
    response = run_metadata_graphql(query, {"name": workbook_name})
    logger.info(f"GraphQL response: {json.dumps(response, indent=2)}")
    return {
        "success": True,
        "response": response
    }


if __name__ == "__main__":
    workbook_name = "Superstore"  # Replace with your workbook name

    result = get_lineage_for_workbook(workbook_name)

    print("\n=== Lineage for Workbook ===")
    if result is None:
        print("❌ GraphQL request failed. Check logs.")
        sys.exit(1)

    if "errors" in result:
        print("❌ GraphQL returned errors:")
        print(json.dumps(result["errors"], indent=2))
        sys.exit(1)

    workbooks = result.get("data", {}).get("workbooks", [])
    if not workbooks:
        print(f"No lineage found for workbook '{workbook_name}'.")
        sys.exit(0)

    for wb in workbooks:
        print(f"\n📘 Workbook: {wb['name']} (ID: {wb['id']})")
        print(f"  📁 Project: {wb.get('projectName', 'N/A')}")

        if wb["upstreamDatasources"]:
            print("  🔼 Upstream Datasources:")
            for ds in wb["upstreamDatasources"]:
                print(f"    - {ds['name']} (ID: {ds['id']})")
        else:
            print("  🔼 No upstream datasources.")

        if wb["embeddedDatasources"]:
            print("  🧩 Embedded Datasources:")
            for ds in wb["embeddedDatasources"]:
                print(f"    - {ds['name']} (ID: {ds['id']})")

        if wb["sheets"]:
            print("  🔽 Downstream Sheets & Dashboards:")
            for sheet in wb["sheets"]:
                print(f"    📄 Sheet: {sheet['name']} (ID: {sheet['id']})")
                dashboards = sheet.get("dashboards", [])
                for dash in dashboards:
                    print(f"      📊 Dashboard: {dash['name']} (ID: {dash['id']})")
        else:
            print("  🔽 No downstream sheets or dashboards.")