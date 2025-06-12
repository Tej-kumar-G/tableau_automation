import logging
import os
import sys
from collections import Counter
from pathlib import Path

# Add base_setup directory to Python path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth

# Setup logging
logger = setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))

from tableauserverclient import Pager, Server, PersonalAccessTokenAuth


def audit_site_user_group_roles(site_override: str = None) -> dict:
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
        logger.info("Connected to Tableau Cloud site")

        # Users
        try:
            users = list(Pager(server.users))
            user_count = len(users)
            role_counter = Counter(user.site_role for user in users)
            logger.info(f"User count: {user_count}")
            logger.info(f"Role breakdown: {dict(role_counter)}")
        except Exception as e:
            logger.error(f"Failed to fetch users: {e}")
            user_count = "Error"
            role_counter = {}

        # Groups
        try:
            group_count = sum(1 for _ in Pager(server.groups))
            logger.info(f"Group count: {group_count}")
        except Exception as e:
            logger.error(f"Failed to fetch groups: {e}")
            group_count = "Error"

        return {
            "site": site_override or config["site_id"],
            "user_count": user_count,
            "group_count": group_count,
            "role_breakdown": dict(role_counter)
        }


if __name__ == '__main__':
    audit_site_user_group_roles("nitidev")
