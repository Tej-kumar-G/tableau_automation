import sys
import os
import logging
from pathlib import Path
from typing import Optional
import tableauserverclient as TSC

# Setup base path and logging
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth

setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger("tableau_automation")


def get_project_id_map(server: TSC.Server) -> dict:
    projects, _ = server.projects.get()
    return {project.id: project.name for project in projects}


def delete_project(project_name: str) -> dict:
    try:
        logger.info(f"Deleting project: {project_name}")
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(auth):
            projects, _ = server.projects.get()
            project = next((p for p in projects if p.name.strip().lower() == project_name.strip().lower()), None)

            if not project:
                return {"success": False, "message": f"Project '{project_name}' not found."}

            server.projects.delete(project.id)
            return {"success": True, "message": f"Project '{project_name}' deleted successfully."}

    except Exception as e:
        logger.error(f"Error deleting project: {e}", exc_info=True)
        return {"success": False, "message": f"Error deleting project: {e}"}


def delete_workbook(workbook_name: str, project_name: str) -> dict:
    try:
        logger.info(f"Deleting workbook: {workbook_name} from project: {project_name}")
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(auth):
            workbooks, _ = server.workbooks.get()
            project_map = get_project_id_map(server)

            workbook = next(
                (wb for wb in workbooks
                 if wb.name.strip().lower() == workbook_name.strip().lower() and
                 project_map.get(wb.project_id, "").strip().lower() == project_name.strip().lower()),
                None
            )

            if not workbook:
                return {"success": False, "message": f"Workbook '{workbook_name}' not found in project '{project_name}'."}

            server.workbooks.delete(workbook.id)
            return {"success": True, "message": f"Workbook '{workbook_name}' deleted from project '{project_name}'."}

    except Exception as e:
        logger.error(f"Error deleting workbook: {e}", exc_info=True)
        return {"success": False, "message": f"Error deleting workbook: {e}"}


def delete_datasource(datasource_name: str, project_name: str) -> dict:
    try:
        logger.info(f"Deleting datasource: {datasource_name} from project: {project_name}")
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(auth):
            datasources, _ = server.datasources.get()
            project_map = get_project_id_map(server)

            datasource = next(
                (ds for ds in datasources
                 if ds.name.strip().lower() == datasource_name.strip().lower() and
                 project_map.get(ds.project_id, "").strip().lower() == project_name.strip().lower()),
                None
            )

            if not datasource:
                return {"success": False, "message": f"Datasource '{datasource_name}' not found in project '{project_name}'."}

            server.datasources.delete(datasource.id)
            return {"success": True, "message": f"Datasource '{datasource_name}' deleted from project '{project_name}'."}

    except Exception as e:
        logger.error(f"Error deleting datasource: {e}", exc_info=True)
        return {"success": False, "message": f"Error deleting datasource: {e}"}


def delete_content(content_type: str, content_name: str, project_name: Optional[str] = None) -> dict:
    content_type = content_type.strip().lower()
    if content_type == "project":
        return delete_project(content_name)
    elif content_type == "workbook":
        if not project_name:
            return {"success": False, "message": "Project name is required to delete a workbook."}
        return delete_workbook(content_name, project_name)
    elif content_type == "datasource":
        if not project_name:
            return {"success": False, "message": "Project name is required to delete a datasource."}
        return delete_datasource(content_name, project_name)
    else:
        return {"success": False, "message": f"Unsupported content type: {content_type}"}

