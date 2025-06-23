import os
import logging
from io import BytesIO
from pathlib import Path
from typing import Optional
import tableauserverclient as TSC

# Base setup
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
import sys

sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth

# Logging
logger = setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))



def find_project(server: TSC.Server, project_name: str) -> Optional[TSC.ProjectItem]:
    all_projects, _ = server.projects.get()
    for project in all_projects:
        if project.name.strip().lower() == project_name.strip().lower():
            return project
    return None


def copy_workbook_to_project(
        workbook_name: str,
        source_project_name: str,
        target_project_name: str
) -> dict:
    """
    Copy a workbook from source project to target project by downloading and republishing.
    """
    try:
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(auth):
            # Lookup source and target projects
            source_proj = find_project(server, source_project_name)
            target_proj = find_project(server, target_project_name)

            if not source_proj:
                return {"success": False, "message": f"Source project '{source_project_name}' not found."}
            if not target_proj:
                return {"success": False, "message": f"Target project '{target_project_name}' not found."}

            # Find the workbook in the source project
            all_workbooks, _ = server.workbooks.get()
            workbook = next(
                (wb for wb in all_workbooks if wb.name == workbook_name and wb.project_id == source_proj.id),
                None
            )
            if not workbook:
                return {"success": False,
                        "message": f"Workbook '{workbook_name}' not found in project '{source_project_name}'."}

            # Download the workbook in memory
            file_obj = BytesIO()
            server.workbooks.download(workbook.id, filepath=file_obj)
            file_obj.seek(0)

            # Publish to target project
            new_workbook = TSC.WorkbookItem(name=workbook_name, project_id=target_proj.id)
            server.workbooks.publish(new_workbook, file_obj, mode=TSC.Server.PublishMode.CreateNew)

            return {
                "success": True,
                "message": f"Workbook '{workbook_name}' successfully copied from '{source_project_name}' to '{target_project_name}'."
            }

    except Exception as e:
        logger.error(f"Error copying workbook: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Unexpected error: {str(e)}"}
