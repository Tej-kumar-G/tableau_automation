import logging
import os
import sys
from pathlib import Path

from tableauserverclient import Server, PersonalAccessTokenAuth

# Add base_setup directory to Python path
base_setup_path = str(Path(__file__).parent.parent.parent / "base_setup")
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth

# Setup logging
logger = setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))


def check_tcm_access(site_override: str = None) -> dict:
    config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))

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
        logger.info(f"✅ Signed in to Tableau Cloud site: {server.site_id}")

        try:
            current_user_id = server.user_id
            current_user = server.users.get_by_id(current_user_id)
            role = current_user.site_role
            username = current_user.name
        except Exception as e:
            logger.error(f"❌ Failed to retrieve user info: {e}")
            return {
                "site_id": site_override or config["tableau"]["site_id"],
                "user": "Unknown",
                "role": "Unknown",
                "has_tcm": "Unknown"
            }

        logger.info(f"👤 User: {username} | Role: {role}")

        has_tcm = role in ["SiteAdministrator", "SiteAdministratorExplorer", "ServerAdministrator"]
        if has_tcm:
            logger.info("✅ TCM-level access likely granted (admin privileges).")
        else:
            logger.warning("⚠️ TCM access unlikely. User is not an admin.")

        return {
            "success": True,
            "site_id": site_override or config["tableau"]["site_id"],
            "user": username,
            "role": role,
            "has_tcm": has_tcm
        }


if __name__ == "__main__":
    # Pass site_id optionally here if you want to override
    result = check_tcm_access(site_override="nitidev")

    print("\n=== Tableau TCM Access Check ===")
    print(f"Site ID      : {result['site_id']}")
    print(f"User         : {result['user']}")
    print(f"Site Role    : {result['role']}")
    print(f"TCM Access   : {'✅ Yes' if result['has_tcm'] is True else '❌ No' if result['has_tcm'] is False else 'Unknown'}")