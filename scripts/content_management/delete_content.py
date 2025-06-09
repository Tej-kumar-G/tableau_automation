import sys
import os
import logging
from pathlib import Path

# Add the base_setup directory to the Python path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth

# Setup logging
setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger('tableau_automation')


def delete_project(project_name: str) -> dict:
    """
    Delete a project by name.
    """
    logger.info(f"Attempting to delete project: {project_name}")
    try:
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, tableau_auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(tableau_auth):
            projects, _ = server.projects.get()
            project_to_delete = None
            for project in projects:
                if project.name == project_name:
                    project_to_delete = project
                    break
            
            if not project_to_delete:
                logger.info(f"Project '{project_name}' not found")
                return {"success": False, "message": f"Project '{project_name}' not found"}

            server.projects.delete(project_to_delete.id)
            logger.info(f"Project '{project_name}' deleted successfully")
            return {"success": True, "message": f"Project '{project_name}' deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Error deleting project: {str(e)}"}


def delete_workbook(workbook_name: str, project_name: str) -> dict:
    """
    Delete a workbook by name and project name.
    """
    logger.info(f"Attempting to delete workbook: {workbook_name} from project: {project_name}")
    try:
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, tableau_auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(tableau_auth):
            # Get all workbooks
            workbooks, _ = server.workbooks.get()
            workbook_to_delete = None
            for wb in workbooks:
                # Fetch project info for the workbook
                if wb.name == workbook_name:
                    # Usually, workbook.project_name attribute exists; if not, check project ID
                    # If project name attribute missing, you may need extra API call to get project details
                    if hasattr(wb, 'project_name') and wb.project_name == project_name:
                        workbook_to_delete = wb
                        break
                    else:
                        # Fallback: Compare project ID to project name by fetching projects
                        projects, _ = server.projects.get()
                        project_dict = {p.id: p.name for p in projects}
                        if project_dict.get(wb.project_id) == project_name:
                            workbook_to_delete = wb
                            break

            if not workbook_to_delete:
                logger.info(f"Workbook '{workbook_name}' in project '{project_name}' not found")
                return {"success": False, "message": f"Workbook '{workbook_name}' in project '{project_name}' not found"}

            server.workbooks.delete(workbook_to_delete.id)
            logger.info(f"Workbook '{workbook_name}' deleted successfully from project '{project_name}'")
            return {"success": True, "message": f"Workbook '{workbook_name}' deleted successfully from project '{project_name}'"}

    except Exception as e:
        logger.error(f"Error deleting workbook: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Error deleting workbook: {str(e)}"}


def delete_datasource(datasource_name: str, project_name: str) -> dict:
    """
    Delete a datasource by name and project name.
    """
    logger.info(f"Attempting to delete datasource: {datasource_name} from project: {project_name}")
    try:
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, tableau_auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(tableau_auth):
            datasources, _ = server.datasources.get()
            datasource_to_delete = None
            for ds in datasources:
                if ds.name == datasource_name:
                    if hasattr(ds, 'project_name') and ds.project_name == project_name:
                        datasource_to_delete = ds
                        break
                    else:
                        projects, _ = server.projects.get()
                        project_dict = {p.id: p.name for p in projects}
                        if project_dict.get(ds.project_id) == project_name:
                            datasource_to_delete = ds
                            break

            if not datasource_to_delete:
                logger.info(f"Datasource '{datasource_name}' in project '{project_name}' not found")
                return {"success": False, "message": f"Datasource '{datasource_name}' in project '{project_name}' not found"}

            server.datasources.delete(datasource_to_delete.id)
            logger.info(f"Datasource '{datasource_name}' deleted successfully from project '{project_name}'")
            return {"success": True, "message": f"Datasource '{datasource_name}' deleted successfully from project '{project_name}'"}

    except Exception as e:
        logger.error(f"Error deleting datasource: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Error deleting datasource: {str(e)}"}


def delete_content(content_type: str, content_name: str, project_name: str = None):
    """
    Wrapper function to delete project, workbook, or datasource.
    """
    logger.info(f"Delete request - Type: {content_type}, Name: {content_name}, Project: {project_name}")
    if content_type == "project":
        return delete_project(content_name)
    elif content_type == "workbook":
        return delete_workbook(content_name, project_name)
    elif content_type == "datasource":
        return delete_datasource(content_name, project_name)
    else:
        logger.info(f"Invalid content type: {content_type}")
        return {"success": False, "message": f"Invalid content type: {content_type}"}


if __name__ == "__main__":
    # CLI usage
    args = sys.argv
    if len(args) < 3:
        print("Usage:")
        print("  Delete Project: python delete_content.py project <project_name>")
        print("  Delete Workbook: python delete_content.py workbook <workbook_name> <project_name>")
        print("  Delete Datasource: python delete_content.py datasource <datasource_name> <project_name>")
        sys.exit(1)

    content_type = args[1].lower()
    content_name = args[2]
    project_name = args[3] if len(args) == 4 else None

    logger.info(f"Script called with arguments: {args[1:]}")
    result = delete_content(content_type, content_name, project_name)
    print(result["message"])


