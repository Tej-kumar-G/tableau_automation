import sys
import os
import logging
from pathlib import Path
from typing import Dict, Optional, Union
import tableauserverclient as TSC

# Setup base path and logging
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth

setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger('tableau_automation')


def find_project(server: TSC.Server, project_name: str) -> Optional[TSC.ProjectItem]:
    """Find a project by name (case-insensitive)."""
    try:
        all_projects, _ = server.projects.get()
        name = project_name.strip().lower()
        return next((p for p in all_projects if p.name.strip().lower() == name), None)
    except Exception as e:
        logger.error(f"Error finding project '{project_name}': {e}", exc_info=True)
        return None


def get_content_item(
    server: TSC.Server,
    content_type: str,
    content_name: str,
    project_id: str
) -> Optional[Union[TSC.WorkbookItem, TSC.DatasourceItem]]:
    """Retrieve a workbook or datasource by name and project_id."""
    try:
        name = content_name.strip().lower()

        if content_type == "workbook":
            items, _ = server.workbooks.get()
        else:  # datasource
            items, _ = server.datasources.get()

        return next((i for i in items if i.project_id == project_id and i.name.strip().lower() == name), None)

    except Exception as e:
        logger.error(f"Error retrieving {content_type} '{content_name}': {e}", exc_info=True)
        return None


def move_content(
    content_type: str,
    content_name: str,
    source_project: str,
    new_project: str
) -> Dict[str, object]:
    """
    Move a workbook or datasource from one project to another.

    Args:
        content_type: "workbook" or "datasource"
        content_name: The name of the content item to move
        source_project: The current project name
        new_project: The destination project name

    Returns:
        A dictionary with success status and message
    """
    content_type = content_type.lower()
    if content_type not in ["workbook", "datasource"]:
        return {
            "success": False,
            "message": f"Invalid content type '{content_type}'. Must be 'workbook' or 'datasource'."
        }

    try:
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(auth):
            source_proj = find_project(server, source_project)
            if not source_proj:
                return {
                    "success": False,
                    "message": f"Source project '{source_project}' not found."
                }

            target_proj = find_project(server, new_project)
            if not target_proj:
                return {
                    "success": False,
                    "message": f"Destination project '{new_project}' not found."
                }

            content_item = get_content_item(server, content_type, content_name, source_proj.id)
            if not content_item:
                return {
                    "success": False,
                    "message": f"{content_type.capitalize()} '{content_name}' not found in project '{source_project}'."
                }

            # Perform the move
            content_item.project_id = target_proj.id
            if content_type == "workbook":
                server.workbooks.update(content_item)
            else:
                server.datasources.update(content_item)

            logger.info(f"Moved {content_type} '{content_name}' to project '{new_project}'")
            return {
                "success": True,
                "message": f"{content_type.capitalize()} '{content_name}' successfully moved to project '{new_project}'.",
                "content_id": content_item.id,
                "project_id": target_proj.id
            }

    except Exception as e:
        logger.error(f"Unexpected error during move: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Unexpected error: {e}"
        }
