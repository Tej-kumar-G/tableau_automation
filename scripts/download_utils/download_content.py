import sys
import os
import logging
from pathlib import Path

# Add the base_setup directory to the Python path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth, ensure_directory_exists

# Setup logging
setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger('tableau_automation')



def download_content(content_type: str, content_name: str, project_name: str | None = None, format_type: str | None = None) -> dict:
    """
    Download content (workbook or datasource) from Tableau Server.
    
    Args:
        content_type (str): Type of content ('workbook' or 'datasource')
        content_name (str): Name of the content
        project_name (str, optional): Project name to narrow down search.
        format_type (str, optional): Format to download (e.g., 'pdf', 'csv', 'twb').
        
    Returns:
        dict: Result with download path if successful.
    """
    try:
        if content_type.lower() not in ['workbook', 'datasource']:
            return {
                "success": False,
                "message": f"Invalid content type: {content_type}. Must be 'workbook' or 'datasource'"
            }

        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, tableau_auth = get_tableau_server_and_auth(config)
        download_path_base = config.get('tableau', {}).get('download_path', 'downloads')
        ensure_directory_exists(download_path_base)

        with server.auth.sign_in(tableau_auth):
            # Find the content item
            if content_type.lower() == 'workbook':
                if not format_type:
                    return {"success": False, "message": "format_type is required for workbooks"}
                all_items = server.workbooks.get()[0]
            else:
                all_items = server.datasources.get()[0]

            # Filter by name
            filtered_items = [item for item in all_items 
                           if item.name.lower() == content_name.lower()]

            # Filter by project if specified
            if project_name:
                project = next((p for p in server.projects.get()[0] 
                             if p.name.lower() == project_name.lower()), None)
                if not project:
                    return {
                        "success": False,
                        "message": f"Project '{project_name}' not found"
                    }
                filtered_items = [item for item in filtered_items 
                               if item.project_id == project.id]

            if not filtered_items:
                return {
                    "success": False,
                    "message": f"{content_type} '{content_name}' not found" + 
                             (f" in project '{project_name}'" if project_name else "")
                }
            if len(filtered_items) > 1:
                return {
                    "success": False,
                    "message": f"Multiple {content_type}s found with name '{content_name}'." + 
                             (" Provide project name to narrow down." if not project_name else "")
                }

            content_item = filtered_items[0]
            file_ext = format_type if content_type.lower() == 'workbook' else 'tds'
            download_path = os.path.join(download_path_base, f"{content_name.replace(' ', '_')}.{file_ext}")

            # Download with appropriate method
            if content_type.lower() == 'workbook':
                server.workbooks.download(
                    content_item.id,
                    filepath=download_path,
                    no_extract=False,
                    include_extract=False
                )
            else:
                server.datasources.download(
                    content_item.id,
                    filepath=download_path,
                    no_extract=False
                )

            return {
                "success": True,
                "message": f"Downloaded {content_type} '{content_name}' successfully",
                "download_path": download_path
            }

    except Exception as e:
        logger.error(f"Error downloading content: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Error downloading content: {str(e)}"
        }


