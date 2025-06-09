import sys
import os
import logging
from pathlib import Path
from typing import Dict, Optional, Union

# Add the base_setup directory to the Python path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth
import tableauserverclient as TSC

# Setup logging
setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger('tableau_automation')


def find_project(server: TSC.Server, project_name: str) -> Optional[TSC.ProjectItem]:
    try:
        all_projects, _ = server.projects.get()
        clean_project_name = project_name.strip().lower()
        for project in all_projects:
            if project.name.strip().lower() == clean_project_name:
                return project
        return None
    except Exception as e:
        logger.error(f"Error finding project: {str(e)}", exc_info=True)
        return None


def get_content_item(server: TSC.Server,content_type: str,content_name: str,project_id: str) -> Optional[Union[TSC.WorkbookItem, TSC.DatasourceItem]]:
    try:
        clean_content_name = content_name.strip().lower()

        if content_type.lower() == 'workbook':
            all_items, _ = server.workbooks.get()
            filtered_items = [wb for wb in all_items if wb.project_id == project_id]
        else:
            all_items, _ = server.datasources.get()
            filtered_items = [ds for ds in all_items if ds.project_id == project_id]

        for item in filtered_items:
            if item.name.strip().lower() == clean_content_name:
                return item

        return None
    except Exception as e:
        logger.error(f"Error retrieving {content_type} items: {str(e)}", exc_info=True)
        return None


def move_content(content_type: str, content_name: str, source_project: str, new_project: str) -> Dict[str, object]:
    try:
        if content_type.lower() not in ['workbook', 'datasource']:
            return {
                "success": False,
                "message": f"Invalid content type: {content_type}. Must be 'workbook' or 'datasource'"
            }

        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, tableau_auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(tableau_auth):
            current_site = server.sites.get_by_id(server.site_id)
            logger.debug(f"Operating in site: {current_site.name} (ID: {current_site.id})")

            all_projects, _ = server.projects.get()
            logger.debug(f"All accessible projects: {[p.name for p in all_projects]}")

            source_project_item = find_project(server, source_project)
            if not source_project_item:
                return {
                    "success": False,
                    "message": f"Source project '{source_project}' not found in site '{current_site.name}'"
                }

            content_item = get_content_item(server, content_type, content_name, source_project_item.id)
            if not content_item:
                return {
                    "success": False,
                    "message": f"{content_type} '{content_name}' not found in project '{source_project}'"
                }

            new_project_item = find_project(server, new_project)
            if not new_project_item:
                return {
                    "success": False,
                    "message": f"Destination project '{new_project}' not found in site '{current_site.name}'"
                }

            logger.info(f"Moving {content_type} '{content_name}' from '{source_project}' to '{new_project}'")

            # Update the item's project ID and send update
            content_item.project_id = new_project_item.id

            if content_type.lower() == 'workbook':
                server.workbooks.update(content_item)
            else:
                server.datasources.update(content_item)

            logger.info(f"Successfully moved {content_type} '{content_name}' to project '{new_project}'")
            return {
                "success": True,
                "message": f"Successfully moved {content_type} '{content_name}' to project '{new_project}'"
            }

    except Exception as e:
        logger.error(f"Unexpected error in move_content: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }


if __name__ == "__main__":
    # Example CLI usage
    if len(sys.argv) != 5:
        print("Usage: python move_content.py <content_type> <content_name> <source_project> <new_project>")
        sys.exit(1)

    result = move_content(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(result["message"])



