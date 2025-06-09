import os
import logging
import requests
from pathlib import Path
from typing import Optional
from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth
import tableauserverclient as TSC

# Setup paths and logging
BASE_DIR = Path(__file__).parent.parent.parent / 'base_setup' / 'config'
CONFIG_PATH = BASE_DIR / 'config.yaml'
LOGGING_CONFIG_PATH = BASE_DIR / 'logging_config.yaml'

setup_logging(str(LOGGING_CONFIG_PATH))
logger = logging.getLogger('tableau_automation')

def find_user_by_email(server: TSC.Server, email: str) -> Optional[TSC.UserItem]:
    logger.debug(f"Searching user by email: {email}")
    all_users, _ = server.users.get()
    for user in all_users:
        if user.name.strip().lower() == email.strip().lower():
            logger.debug(f"Found user: {user.name} with ID: {user.id}")
            return user
    logger.warning(f"User not found: {email}")
    return None

def find_project(server: TSC.Server, project_name: str) -> Optional[TSC.ProjectItem]:
    logger.debug(f"Searching project: {project_name}")
    all_projects, _ = server.projects.get()
    for project in all_projects:
        if project.name.strip().lower() == project_name.strip().lower():
            logger.debug(f"Found project: {project.name} with ID: {project.id}")
            return project
    logger.warning(f"Project not found: {project_name}")
    return None

def find_workbook(server: TSC.Server, workbook_name: str, project_id: Optional[str] = None) -> Optional[TSC.WorkbookItem]:
    logger.debug(f"Searching workbook: {workbook_name} in project ID: {project_id}")
    all_workbooks, _ = server.workbooks.get()
    filtered = [wb for wb in all_workbooks if wb.name.strip().lower() == workbook_name.strip().lower()]
    if project_id:
        filtered = [wb for wb in filtered if wb.project_id == project_id]
    if len(filtered) == 1:
        # Fetch full workbook details to ensure owner_id is populated
        full_workbook = server.workbooks.get_by_id(filtered[0].id)
        logger.debug(f"Found workbook: {full_workbook.name} with ID: {full_workbook.id} and owner ID: {full_workbook.owner_id}")
        return full_workbook
    if len(filtered) > 1:
        logger.warning(f"Multiple workbooks found with name '{workbook_name}'. Please be more specific.")
    else:
        logger.warning(f"No workbook found with name '{workbook_name}' and project ID '{project_id}'")
    return None



def update_project_ownership(server: TSC.Server,project_name: str,requesting_user_email: str, new_owner_email: str) -> dict:
    try:
        logger.info(f"Attempting ownership update for project '{project_name}'")
        
        # Find the project
        project = find_project(server, project_name)
        if not project:
            msg = f"Project '{project_name}' not found."
            logger.error(msg)
            return {"success": False, "message": msg}

        # Find new owner
        new_owner = find_user_by_email(server, new_owner_email)
        if not new_owner:
            msg = f"New owner '{new_owner_email}' not found."
            logger.error(msg)
            return {"success": False, "message": msg}

        # Permission check if requesting_user provided
        if requesting_user_email:
            requesting_user = find_user_by_email(server, requesting_user_email)
            if not requesting_user:
                msg = f"Requesting user '{requesting_user_email}' not found."
                logger.error(msg)
                return {"success": False, "message": msg}

            if project.owner_id != requesting_user.id:
                current_owner = next((u for u in server.users.get()[0] if u.id == project.owner_id), None)
                owner_name = current_owner.email if current_owner else str(project.owner_id)
                msg = (f"Permission denied: Requesting user '{requesting_user_email}' "
                      f"is not the current owner ('{owner_name}')")
                logger.warning(msg)
                return {"success": False, "message": msg}

        # Get current owner details for logging
        current_owner = next((u for u in server.users.get()[0] if u.id == project.owner_id), None)
        current_owner_email = current_owner.email if current_owner else f"ID:{project.owner_id}"

        logger.info(
            f"Transferring ownership of '{project_name}' "
            f"from '{current_owner_email}' to '{new_owner_email}'"
        )

        # Update ownership
        project.owner_id = new_owner.id
        server.projects.update(project)

        logger.info("Ownership updated successfully")
        return {"success": True, "message": f"Project ownership updated to '{new_owner_email}'"}

    except Exception as e:
        logger.error(f"Unexpected error updating ownership: {str(e)}")
        return {"success": False, "message": f"An error occurred: {str(e)}"}


def update_workbook_ownership(server: TSC.Server, workbook_name: str, current_owner_email: str, new_owner_email: str, project_name: Optional[str]) -> dict:
    logger.info(f"Updating ownership of workbook '{workbook_name}' (Project: {project_name}) from '{current_owner_email}' to '{new_owner_email}'")
    project_id = None
    if project_name:
        project = find_project(server, project_name)
        if not project:
            return {"success": False, "message": f"Project '{project_name}' not found."}
        project_id = project.id

    workbook = find_workbook(server, workbook_name, project_id)
    if not workbook:
        return {"success": False, "message": f"Workbook '{workbook_name}' not found."}

    current_owner = find_user_by_email(server, current_owner_email)
    if not current_owner:
        return {"success": False, "message": f"Current owner '{current_owner_email}' not found."}

    logger.debug(f"Workbook owner ID: {workbook.owner_id}")
    owner_user = next((user for user in server.users.get()[0] if user.id == workbook.owner_id), None)
    if owner_user:
        logger.debug(f"Actual workbook owner email: {owner_user.name}")
    else:
        logger.debug("Could not find actual owner email for workbook owner ID")

    if workbook.owner_id != current_owner.id:
        logger.warning(f"Current owner mismatch for workbook '{workbook_name}'")
        return {"success": False, "message": "Current owner does not match the actual owner of the workbook."}

    new_owner = find_user_by_email(server, new_owner_email)
    if not new_owner:
        return {"success": False, "message": f"New owner '{new_owner_email}' not found."}

    workbook.owner_id = new_owner.id
    server.workbooks.update(workbook)
    logger.info(f"Workbook '{workbook_name}' ownership changed successfully to '{new_owner_email}'")
    return {"success": True, "message": f"Workbook '{workbook_name}' ownership changed to '{new_owner_email}'"}

def update_ownership(content_type: str, content_name: str, current_owner: str, new_owner: str, project_name: Optional[str] = None) -> dict:
    try:
        logger.info(f"Request to update ownership - Type: {content_type}, Content: {content_name}, From: {current_owner}, To: {new_owner}, Project: {project_name}")
        config = load_config(str(CONFIG_PATH))
        server, tableau_auth = get_tableau_server_and_auth(config)

        with server.auth.sign_in(tableau_auth):
            if content_type.lower() == 'workbook':
                return update_workbook_ownership(server, content_name, current_owner, new_owner, project_name)
            elif content_type.lower() == 'project':
                # Try Metadata API first
                result = update_project_ownership(server, content_name,current_owner, new_owner)
                return result
            else:
                logger.error(f"Invalid content type: {content_type}")
                return {"success": False, "message": "Invalid content type. Use 'workbook' or 'project'."}
    except Exception as e:
        logger.error(f"Error in update_ownership: {e}", exc_info=True)
        return {"success": False, "message": f"Exception occurred: {str(e)}"}




