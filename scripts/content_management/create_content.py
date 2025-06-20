import sys
import os
import logging
from pathlib import Path
from tableauserverclient import ProjectItem
import tableauserverclient as TSC

# Add the base_setup directory to the Python path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth

# Setup logging
logger = setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))


def find_project(server: TSC.Server, project_name: str):
    all_projects, _ = server.projects.get()
    for project in all_projects:
        if project.name.strip().lower() == project_name.strip().lower():
            return project
    return None


def create_project(project_name: str, description: str = "") -> dict:
    config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
    server, auth = get_tableau_server_and_auth(config)

    with server.auth.sign_in(auth):
        if find_project(server, project_name):
            return {"success": False, "message": f"Project '{project_name}' already exists."}

        new_project = ProjectItem(name=project_name, description=description)
        created = server.projects.create(new_project)

        return {
            "success": True,
            "message": f"Project '{project_name}' created successfully.",
            "project_id": created.id
        }
