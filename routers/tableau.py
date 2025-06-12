from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from scripts.content_management.copy_content import copy_workbook_to_project
from scripts.content_management.create_content import create_project
from scripts.content_management.delete_content import delete_content
from scripts.content_management.move_content import move_content
from scripts.content_management.update_ownership import update_ownership
from scripts.download_utils.download_content import download_content
from scripts.download_utils.download_view_assets import download_view_asset
from scripts.monitoring.audit_multiple_sites import audit_site_user_group_roles
from scripts.monitoring.check_tcm_access import check_tcm_access
from scripts.monitoring.validate_personal_space import validate_personal_spaces
from scripts.revision_history.get_revision_history import get_revision_history
from scripts.site_monitoring.slack_connectivity import slack_integration_with_webhook

router = APIRouter()


class WorkbookCreateRequest(BaseModel):
    workbook_name: str
    target_project: str
    source_project: str | None = None


class MoveContentRequest(BaseModel):
    content_type: str  # "workbook" or "datasource"
    content_name: str
    source_project: str
    new_project: str


# ['tej.gangineni@gmail.com','nitheeshkumargorla111@gmail.com']
class UpdateOwnershipRequest(BaseModel):
    content_type: str  # 'workbook' or 'project'
    content_name: str  # workbook name or project name
    current_owner: EmailStr
    new_owner: EmailStr
    project_name: Optional[str] = None  # Optional, required only for workbook


class RevisionHistoryRequest(BaseModel):
    content_type: str
    content_name: str
    project_name: Optional[str] = None  # Add project context if required for lookup


class DownloadRequest(BaseModel):
    content_type: str
    content_name: str
    project_name: Optional[str] = None  # Add project context if required for lookup
    format_type: Optional[str] = None  # e.g., 'pdf', 'csv', 'twb'


class ProjectCreateRequest(BaseModel):
    project_name: str
    description: str = ""


class DeleteContentRequest(BaseModel):
    content_type: str  # "project", "workbook", "datasource"
    content_name: str
    project_name: Optional[str] = None


@router.post("/create_project")
def api_create_project(req: ProjectCreateRequest):
    result = create_project(req.project_name, req.description)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/delete_content")
def api_delete_content(req: DeleteContentRequest):
    result = delete_content(req.content_type, req.content_name, project_name=req.project_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/move_content")
def api_move_content(req: MoveContentRequest):
    result = move_content(req.content_type, req.content_name, req.source_project, req.new_project)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.post("/update_ownership")
def api_update_ownership(req: UpdateOwnershipRequest):
    # Placeholder call to the script function
    result = update_ownership(req.content_type, req.content_name, str(req.current_owner), str(req.new_owner),
                              req.project_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/revision_history")
def api_revision_history(req: RevisionHistoryRequest):
    # Placeholder call to the script function
    result = get_revision_history(req.content_type, req.content_name, req.project_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/download_content")
def api_download(req: DownloadRequest):
    # Placeholder call to the script function
    result = download_content(req.content_type, req.content_name, req.project_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/copy_content")
def api_create_workbook(req: WorkbookCreateRequest):
    # log_blank_line(logger)
    result = copy_workbook_to_project(req.workbook_name, req.source_project, req.target_project)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/slack_connection")
def slack_connection():
    """
    Placeholder endpoint to test Slack connection.
    This can be replaced with actual Slack integration logic.
    """
    return slack_integration_with_webhook()


@router.post("/audit_site")
def audit_site(site_name: str = None):
    return audit_site_user_group_roles(site_override=site_name)


@router.get("/personal_spaces")
def get_personal_spaces():
    """
    Placeholder endpoint to fetch personal spaces.
    This can be replaced with actual logic to fetch personal spaces from Tableau.
    """
    result = validate_personal_spaces()
    return result


@router.get("/get_lineage_for_workbook")
def get_lineage_for_workbook(workbook_name: str):
    """
    Placeholder endpoint to get lineage for a specific workbook.
    This can be replaced with actual logic to fetch lineage from Tableau.
    """
    from scripts.monitoring.check_lineage_graphql import get_lineage_for_workbook as lineage_function
    result = lineage_function(workbook_name)
    if not result:
        raise HTTPException(status_code=404, detail="Workbook not found or no lineage data available.")
    return result


@router.get("/check_tcm_access")
def check_tcm_access_for_site(site_name: str = None):
    """
    Placeholder endpoint to check TCM access.
    This can be replaced with actual logic to check TCM access.
    """
    # Implement the actual access check logic here
    return check_tcm_access(site_name)


@router.get("/download_view_features")
def download_view_features(view_name: str, download_format: str = "image"):
    """
    Placeholder endpoint to download view features.
    This can be replaced with actual logic to download view features from Tableau.
    """
    return download_view_asset(view_name, download_format)


@router.get("/check_extensions_in_workbook")
def check_extensions_in_workbook(workbook_name: str):
    """
    Placeholder endpoint to check for extensions in a workbook.
    This can be replaced with actual logic to scan for extensions in Tableau workbooks.
    """
    from scripts.monitoring.verify_dashboard_extensions import check_extensions_in_workbook as extensions_function
    return extensions_function(workbook_name)


@router.get("/confirm_content_labels_and_description")
def confirm_content_labels_and_description():
    """
    Placeholder endpoint to confirm content labels and descriptions.
    This can be replaced with actual logic to verify content labels and descriptions in Tableau.
    """
    from scripts.monitoring.content_labels_and_description import check_metadata_for_content
    return check_metadata_for_content()
