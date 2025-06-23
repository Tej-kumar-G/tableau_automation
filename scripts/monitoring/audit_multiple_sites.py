import json
import os
import sys
from collections import Counter
from pathlib import Path

# Add base_setup directory to Python path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth
from base_setup.utils.email_utils import send_email
from tableauserverclient import Pager, Server, PersonalAccessTokenAuth

# Setup logging
logger = setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))


def load_previous_snapshot(snapshot_file):
    if os.path.exists(snapshot_file):
        try:
            with open(snapshot_file, "r") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except Exception as e:
            logger.warning(f"Could not read snapshot file {snapshot_file}: {e}")
    return {}


def save_current_snapshot(snapshot_file, data):
    os.makedirs(os.path.dirname(snapshot_file), exist_ok=True)
    with open(snapshot_file, "w") as f:
        json.dump(data, f, indent=2)


def audit_site_user_group_roles(site_override: str = None) -> dict:
    config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
    email_cfg = config.get("email", {})

    if site_override:
        logger.info(f"Overriding site with '{site_override}'")
        tableau_cfg = config["tableau"]
        auth = PersonalAccessTokenAuth(
            token_name=tableau_cfg["token_name"],
            personal_access_token=tableau_cfg["personal_access_token"],
            site_id=site_override
        )
        server = Server(tableau_cfg["server_url"], use_server_version=True)
    else:
        server, auth = get_tableau_server_and_auth(config)

    with server.auth.sign_in(auth):
        logger.info("Connected to Tableau Cloud site")

        site_id = site_override or config["tableau"]["site_id"]

        # Fetch users
        try:
            users = list(Pager(server.users))
            user_count = len(users)
            role_counter = Counter(user.site_role for user in users)
            logger.info(f"User count: {user_count}")
            logger.info(f"Role breakdown: {dict(role_counter)}")
        except Exception as e:
            logger.error(f"Failed to fetch users: {e}")
            subject = f"🚨 Tableau Audit Failure - {site_id}"
            body = f"""
            <html><body>
              <p style="color:red;"><strong>Feature:</strong> tab-audit-usersite-01 – Site Role/User/Group Audit</p>
              <p>Failed to fetch users from Tableau site <strong>{site_id}</strong>.</p>
              <p><code>{str(e)}</code></p>
            </body></html>
            """
            send_email(subject, body, config)
            return {"success": False, "message": "Failed to fetch users"}

        # Fetch groups
        try:
            group_count = sum(1 for _ in Pager(server.groups))
            logger.info(f"Group count: {group_count}")
        except Exception as e:
            logger.error(f"Failed to fetch groups: {e}")
            subject = f"🚨 Tableau Audit Failure - {site_id}"
            body = f"""
            <html><body>
              <p style="color:red;"><strong>Feature:</strong> tab-audit-usersite-01 – Site Role/User/Group Audit</p>
              <p>Failed to fetch groups from Tableau site <strong>{site_id}</strong>.</p>
              <p><code>{str(e)}</code></p>
            </body></html>
            """
            send_email(subject, body, config)
            return {"success": False, "message": "Failed to fetch groups"}

        result = {
            "site": site_id,
            "user_count": user_count,
            "group_count": group_count,
            "role_breakdown": dict(role_counter)
        }

        # Snapshot logic
        snapshot_dir = os.path.join(base_setup_path, "snapshots")
        snapshot_file = os.path.join(snapshot_dir, f"audit_snapshot_{site_id}.json")
        previous = load_previous_snapshot(snapshot_file)
        negative_changes = []

        # Compare current and previous values
        html_rows = []
        for key in ["user_count", "group_count"]:
            prev = previous.get(key)
            curr = result[key]
            if isinstance(prev, int) and isinstance(curr, int):
                if curr < prev:
                    delta = curr - prev
                    html_rows.append(f"""
                    <tr>
                      <td>{key.replace('_', ' ').title()}</td>
                      <td>{prev}</td><td>{curr}</td><td style="color:red;">↓ {abs(delta)}</td>
                    </tr>
                    """)
                    logger.warning(f"⚠️ {key.replace('_', ' ').capitalize()} decreased from {prev} to {curr}")
                    negative_changes.append(key)
                elif curr > prev:
                    logger.info(f"{key.replace('_', ' ').capitalize()} increased from {prev} to {curr} (+{curr - prev}) — no alert needed")
                else:
                    logger.info(f"{key} unchanged ({curr})")
            elif prev is not None:
                logger.warning(f"⚠️ Could not compare {key}: Previous='{prev}', Current='{curr}'")

        # Send email if negative changes found
        if html_rows:
            subject = f"📉 Tableau Audit Alert - {site_id}"
            body = f"""
            <html>
            <head>
              <style>
                body {{ font-family: Arial, sans-serif; }}
                table {{ border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
                th {{ background-color: #e0e0e0; }}
              </style>
            </head>
            <body>
              <p><strong>Feature:</strong> tab-audit-usersite-01 – Site Role/User/Group Audit</p>
              <p>Detected negative changes in Tableau site <strong>{site_id}</strong>:</p>
              <table>
                <tr><th>Metric</th><th>Previous</th><th>Current</th><th>Status</th></tr>
                {''.join(html_rows)}
              </table>
              <p><i>This alert was auto-generated by the audit script.</i></p>
            </body>
            </html>
            """
            try:
                send_email(subject, body, config)
            except Exception as e:
                logger.error(f"Email send failed: {e}")

        # Save snapshot for next comparison
        save_current_snapshot(snapshot_file, {
            "user_count": user_count,
            "group_count": group_count
        })

        return result


if __name__ == '__main__':
    audit_site_user_group_roles("nitidev")
