import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional
import tableauserverclient as TSC

# Add base_setup to path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth, ensure_directory_exists

# Logging
setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger('tableau_automation')


def download_content(content_type: str, content_name: str, project_name: Optional[str] = None) -> Dict[str, object]:
    """
    Download a workbook (.twbx) or datasource (.tdsx) from Tableau Server.

    Args:
        content_type (str): "workbook" or "datasource"
        content_name (str): Name of the content to download
        project_name (str, optional): Filter by project

    Returns:
        dict: { success: bool, message: str, download_path?: str }
    """
    try:
        content_type = content_type.lower()
        if content_type not in ["workbook", "datasource"]:
            return {"success": False, "message": f"Invalid content type: {content_type}"}

        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, auth = get_tableau_server_and_auth(config)
        download_dir = config.get("tableau", {}).get("download_path", "downloads")
        ensure_directory_exists(download_dir)

        with server.auth.sign_in(auth):
            # Fetch items
            if content_type == "workbook":
                items, _ = server.workbooks.get()
                extension = "twbx"
            else:
                items, _ = server.datasources.get()
                extension = "tdsx"

            # Filter by name
            filtered = [item for item in items if item.name.strip().lower() == content_name.strip().lower()]

            # Further filter by project
            if project_name:
                projects, _ = server.projects.get()
                project = next((p for p in projects if p.name.strip().lower() == project_name.strip().lower()), None)
                if not project:
                    return {"success": False, "message": f"Project '{project_name}' not found."}
                filtered = [item for item in filtered if item.project_id == project.id]

            if not filtered:
                return {"success": False, "message": f"{content_type.capitalize()} '{content_name}' not found."}
            if len(filtered) > 1:
                return {"success": False, "message": f"Multiple items named '{content_name}' found. Please specify a project."}

            item = filtered[0]

            # Let Tableau assign file path, then rename
            if content_type == "workbook":
                downloaded_path = server.workbooks.download(item.id, filepath=download_dir, include_extract=False)
            else:
                downloaded_path = server.datasources.download(item.id, filepath=download_dir)

            final_path = os.path.join(download_dir, f"{content_name.replace(' ', '_')}.{extension}")
            if downloaded_path != final_path:
                os.rename(downloaded_path, final_path)

            return {
                "success": True,
                "message": f"Downloaded {content_type} '{content_name}' successfully.",
                "download_path": final_path
            }

    except Exception as e:
        logger.error(f"Error downloading {content_type}: {e}", exc_info=True)
        return {"success": False, "message": f"Error downloading content: {e}"}