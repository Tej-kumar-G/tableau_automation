import tableauserverclient as TSC
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
from base_setup.utils.common_utils import load_config

def get_tableau_auth_and_server():
    config = load_config("base_setup/config/config.yaml")
    tableau_cfg = config["tableau"]

    auth = TSC.PersonalAccessTokenAuth(
        token_name=tableau_cfg["token_name"],
        personal_access_token=tableau_cfg["personal_access_token"],
        site_id=tableau_cfg["site_id"]
    )

    server = TSC.Server(tableau_cfg["server_url"], use_server_version=True)
    server.auth.sign_in(auth)

    return server, tableau_cfg

def get_new_users_since_yesterday(server):
    users = list(TSC.Pager(server.users))
    yesterday = datetime.now() - timedelta(days=1)
    return [u for u in users if u.created_at and u.created_at > yesterday]

def get_new_groups_metadata_api(tableau_cfg):
    yesterday_iso = (datetime.now() - timedelta(days=1)).isoformat()

    transport = RequestsHTTPTransport(
        url=f"{tableau_cfg['server_url']}/api/metadata/graphql",
        headers={"X-Tableau-Auth": tableau_cfg["personal_access_token"]},
        verify=True
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
        query {
          groups {
            name
            createdAt
          }
        }
    """)

    results = client.execute(query)
    return [
        group for group in results["groups"]
        if group["createdAt"] and group["createdAt"] > yesterday_iso
    ]

def validate_licensed_users(server):
    users = list(TSC.Pager(server.users))
    return len([u for u in users if u.site_role and u.site_role != "Unlicensed"])

def send_slack_alert(users, groups, license_count):
    config = load_config("base_setup/config/config.yaml")
    slack_token = config["slack"]["slack_token"]
    slack_channel = config["slack"].get("channel", "#sysadmin")

    client = WebClient(token=slack_token)

    user_list = "\n".join([f"- {u.name} ({u.email})" for u in users]) or "No new users"
    group_list = "\n".join([f"- {g['name']}" for g in groups]) or "No new groups"

    message = f"""
📊 *Tableau New Users/Groups Report*
Date: {datetime.today().strftime('%Y-%m-%d')}

👤 *New Users:* {len(users)}
{user_list}

👥 *New Groups:* {len(groups)}
{group_list}

🔑 *Licensed Users:* {license_count}
"""

    try:
        client.chat_postMessage(channel=slack_channel, text=message)
        print("✅ Slack message sent.")
    except SlackApiError as e:
        print(f"Slack Error: {e.response['error']}")

def run_monitoring():
    server, tableau_cfg = get_tableau_auth_and_server()

    new_users = get_new_users_since_yesterday(server)
    new_groups = get_new_groups_metadata_api(tableau_cfg)
    license_count = validate_licensed_users(server)

    if new_users or new_groups:
        send_slack_alert(new_users, new_groups, license_count)
    else:
        print("✅ No new users or groups created since yesterday.")

    server.auth.sign_out()