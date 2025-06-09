import sys
import os
import logging
from pathlib import Path
import requests # Import the requests library

# Add the base_setup directory to the Python path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth # Updated import

try:
    from tableauserverclient import Filter  # Try modern import first
except ImportError:
    from tableauserverclient.server.request_options import Filter # Import Filter

# Setup logging
setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger('tableau_automation')

def get_revision_history(content_type: str, content_name: str, project_name: str | None = None) -> dict:
    """
    Get the revision history for a content item.
    
    Args:
        content_type (str): Type of content ('workbook' or 'datasource')
        content_name (str): Name of the content
        project_name (str, optional): Project name to narrow down search.
        
    Returns:
        dict: Result with revision history data or error message
    """
    if content_type.lower() not in ['workbook', 'datasource']:
        return {
            "success": False,
            "message": f"Invalid content type: {content_type}. Must be 'workbook' or 'datasource'"
        }

    try:
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, tableau_auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(tableau_auth):  # Changed from server.server.auth
            logger.info(f"Fetching revision history for {content_type} '{content_name}'" + 
                      (f" in project '{project_name}'" if project_name else ""))

            # Find the content item
            if content_type.lower() == 'workbook':
                items, _ = server.workbooks.get()
            else:
                items, _ = server.datasources.get()

            # Filter by name and project
            filtered_items = [item for item in items 
                            if item.name.lower() == content_name.lower()]
            
            if project_name:
                project = next((p for p in server.projects.get()[0] 
                              if p.name.lower() == project_name.lower()), None)
                if not project:
                    msg = f"Project '{project_name}' not found."
                    logger.error(msg)
                    return {"success": False, "message": msg, "revisions": []}
                filtered_items = [item for item in filtered_items 
                                if item.project_id == project.id]

            if not filtered_items:
                msg = f"{content_type.capitalize()} '{content_name}'" + \
                      (f" in project '{project_name}'" if project_name else "") + " not found."
                logger.error(msg)
                return {"success": False, "message": msg, "revisions": []}
            elif len(filtered_items) > 1:
                msg = f"Multiple {content_type}s found with name '{content_name}'." + \
                      (" Please provide a project name to narrow down." if not project_name else "")
                logger.error(msg)
                return {"success": False, "message": msg, "revisions": []}

            content_item = filtered_items[0]

            # Get revision history via REST API
            server_info = server.server_info.get()
            api_version = server_info.rest_api_version
            base_url = server.server_address.replace('/api', '')  # Ensure clean base URL
            site_id = server.site_id
            auth_token = server.auth_token

            endpoint = f"workbooks/{content_item.id}/revisions" if content_type.lower() == 'workbook' \
                      else f"datasources/{content_item.id}/revisions"
            
            url = f"{base_url}/api/{api_version}/sites/{site_id}/{endpoint}"
            headers = {
                "X-Tableau-Auth": auth_token,
                "Accept": "application/json"
            }

            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                msg = f"API request failed ({response.status_code}): {response.text}"
                logger.error(msg)
                return {"success": False, "message": msg, "revisions": []}

            try:
                revisions = response.json().get("revisions", {}).get("revision", [])
                revision_data = []
                for rev in revisions:
                    revision_data.append({
                        "version_number": rev.get("revisionNumber", "N/A"),
                        "created_at": rev.get("publishedAt", "N/A"),
                        "modified_by": rev.get("publisher", {}).get("name", "Unknown")
                    })
                    logger.debug(f"Found revision: {revision_data[-1]}")

                logger.info(f"Successfully retrieved {len(revision_data)} revisions")
                return {
                    "success": True,
                    "message": "Revision history fetched successfully",
                    "revisions": revision_data
                }

            except ValueError as e:
                msg = f"Failed to parse API response: {str(e)}"
                logger.error(msg)
                return {"success": False, "message": msg, "revisions": []}

    except Exception as e:
        logger.error(f"Error fetching revision history: {str(e)}", exc_info=True)
        return {"success": False, "message": str(e), "revisions": []}