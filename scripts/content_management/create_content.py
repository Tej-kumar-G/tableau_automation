from io import BytesIO
import sys
import os
import logging
from pathlib import Path
from typing import Optional, List
from tableauserverclient import Server, models

# Add the base_setup directory to the Python path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth
import tableauserverclient as TSC

# Setup logging
setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger('tableau_automation')

def get_all_projects(server: TSC.Server) -> List[TSC.ProjectItem]:
    """Get all projects from Tableau Server."""
    try:
        logger.info("Fetching all projects from Tableau Server")
        all_projects, _ = server.projects.get()
        return all_projects
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}", exc_info=True)
        return []

def find_project(server: TSC.Server, project_name: str) -> Optional[TSC.ProjectItem]:
    """Find a project by name (case-insensitive)."""
    try:
        logger.info(f"Searching for project '{project_name}'")
        all_projects = get_all_projects(server)
        clean_project_name = project_name.strip().lower()
        for project in all_projects:
            if project.name.strip().lower() == clean_project_name:
                return project
        logger.info(f"Project '{project_name}' not found")
        return None
    except Exception as e:
        logger.error(f"Error finding project: {str(e)}", exc_info=True)
        return None

def list_projects(server: TSC.Server) -> List[str]:
    """List all project names on the server."""
    try:
        logger.info("Listing all projects")
        all_projects = get_all_projects(server)
        return [project.name for project in all_projects]
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}", exc_info=True)
        return []

def create_project(project_name: str, description: str = "") -> dict:
    """
    Create a new project in Tableau Server.
    
    Args:
        project_name (str): Name of the project to create
        description (str): Optional description of the project
        
    Returns:
        dict: Result with keys: success, message, project_id (if successful), projects (if project exists)
    """
    try:
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, tableau_auth = get_tableau_server_and_auth(config)
        
        with server.auth.sign_in(tableau_auth):
            # Check if project already exists
            logger.info(f"Attempting to create project '{project_name}'")
            existing_project = find_project(server, project_name)
            if existing_project:
                logger.info(f"Project '{project_name}' already exists")
                return {
                    "success": False,
                    "message": f"Project '{project_name}' already exists. Please choose another name.",
                    "projects": list_projects(server)
                }
            
            # Create new project
            new_project = models.ProjectItem(name=project_name, description=description)
            created_project = server.projects.create(new_project)
            
            if not hasattr(created_project, 'id'):
                return {
                    "success": False,
                    "message": f"Failed to create project '{project_name}'"
                }
        logger.info(f"Project '{project_name}' created with ID: {created_project.id}")
        return {
            "success": True,
            "message": f"Successfully created project '{project_name}'",
            "project_id": created_project.id
        }
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Error creating project: {str(e)}"
        }

def create_workbook(workbook_name: str, project_name: str = None, source_project: str = None) -> dict:
    """
    Copy a workbook from one Tableau project (source_project) to another (project_name) without downloading to disk.

    Args:
        workbook_name (str): The name of the workbook to copy (without extension).
        project_name (str): Target project where the workbook should be published.
        source_project (str): Source project where the original workbook resides.

    Returns:
        dict: Result indicating success, message, and workbook ID (if successful).
    """
    try:
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, tableau_auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(tableau_auth):
            # Find source project
            if not source_project:
                return {
                    "success": False,
                    "message": "Source project is required to copy the workbook."
                }

            source_proj = find_project(server, source_project)
            if not source_proj:
                return {
                    "success": False,
                    "message": f"Source project '{source_project}' not found.",
                    "projects": list_projects(server)
                }

            # Find the workbook in the source project
            all_workbooks, _ = server.workbooks.get()
            source_wb = next(
                (wb for wb in all_workbooks if wb.name == workbook_name and wb.project_id == source_proj.id),
                None
            )
            if not source_wb:
                return {
                    "success": False,
                    "message": f"Workbook '{workbook_name}' not found in project '{source_project}'."
                }

            # Download the workbook into memory
            file_obj = BytesIO()
            logger.info(f"Downloading workbook '{workbook_name}' from project '{source_project}'")
            server.workbooks.download(source_wb.id, filepath=file_obj)
            file_obj.seek(0)

            # Find the target project
            target_proj = find_project(server, project_name)
            if not target_proj:
                return {
                    "success": False,
                    "message": f"Target project '{project_name}' not found.",
                    "projects": list_projects(server)
                }

            # Publish the workbook to target project
            new_workbook = TSC.WorkbookItem(name=workbook_name, project_id=target_proj.id)
            logger.info(f"Publishing workbook '{workbook_name}' to project '{target_proj.name}'")
            published_wb = server.workbooks.publish(new_workbook, file_obj, mode=TSC.Server.PublishMode.CreateNew)

            return {
                "success": True,
                "message": f"Workbook '{workbook_name}' copied from '{source_project}' to '{project_name}'",
                "workbook_id": published_wb.id
            }

    except Exception as e:
        logger.error(f"Error copying workbook: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Error copying workbook: {str(e)}"
        }



if __name__ == "__main__":
    try:
        logger.info("Script started")
        if len(sys.argv) < 3:
            logger.error("Insufficient arguments provided")
            print("Usage for project creation: python create_content.py project <project_name> [description]")
            print("Usage for workbook creation: python create_content.py workbook <workbook_name> [project_name]")
            sys.exit(1)
            
        operation = sys.argv[1].lower()
        if operation == "project":
            project_name = sys.argv[2]
            description = sys.argv[3] if len(sys.argv) > 3 else ""
            logger.info(f"Creating project: {project_name}")
            result = create_project(project_name, description)
        elif operation == "workbook":
            workbook_name = sys.argv[2]
            target_project = sys.argv[3] if len(sys.argv) > 3 else None
            source_project = sys.argv[4] if len(sys.argv) > 4 else None
            logger.info(f"Copying workbook: {workbook_name} from {source_project} to {target_project}")
            result = create_workbook(workbook_name, target_project, source_project)
        else:
            logger.error(f"Invalid operation: {operation}")
            print("Error: Invalid operation. Use 'project' or 'workbook'")
            sys.exit(1)
            
        print(result["message"])
        if not result["success"]:
            if "projects" in result:
                print("\nAvailable projects:")
                for project in result["projects"]:
                    print(f"- {project}")
            logger.error(f"Operation failed: {result['message']}")
            sys.exit(1)
            
        logger.info("Script completed successfully")
        
    except Exception as e:
        logger.error(f"Script failed: {str(e)}", exc_info=True)
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)