import logging
from fastapi import APIRouter, HTTPException, logger
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from typing import Optional, List
from scripts.content_management.create_content import create_project, create_workbook, list_projects
from scripts.content_management.move_content import move_content
from scripts.content_management.delete_content import delete_content
from scripts.content_management.update_ownership import update_ownership
from scripts.revision_history.get_revision_history import get_revision_history
from scripts.download_utils.download_content import download_content

router = APIRouter()

class ProjectCreateRequest(BaseModel):
    project_name: str
    description: Optional[str] = ""

class WorkbookCreateRequest(BaseModel):
    workbook_name: str
    target_project: str
    source_project: str


class MoveContentRequest(BaseModel):
    content_type: str
    content_name: str
    source_project: str
    new_project: str

class DeleteContentRequest(BaseModel):
    content_type: str
    content_name: str
    project_name: str


# [tej.gangineni@gmail.com','nitheeshkumargorla111@gmail.com']
class UpdateOwnershipRequest(BaseModel):
    content_type: str  # 'workbook' or 'project'
    content_name: str  # workbook name or project name
    current_owner: EmailStr
    new_owner: EmailStr
    project_name: Optional[str] = None  # Optional, required only for workbook


class RevisionHistoryRequest(BaseModel):
    content_type: str
    content_name: str
    project_name: Optional[str] = None # Add project context if required for lookup

class DownloadRequest(BaseModel):
    content_type: str
    content_name: str
    project_name: Optional[str] = None # Add project context if required for lookup
    format_type: Optional[str] = None # e.g., 'pdf', 'csv', 'twb'


@router.post("/create_project")
def api_create_project(req: ProjectCreateRequest):
    result = create_project(req.project_name, req.description)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/create_workbook")
def api_create_workbook(req: WorkbookCreateRequest):
    # log_blank_line(logger)
    result = create_workbook(req.workbook_name, req.target_project, req.source_project)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/move_content")
def api_move_content(req: MoveContentRequest):
    result = move_content(req.content_type, req.content_name, req.source_project, req.new_project)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/delete_content")
def api_delete_content(req: DeleteContentRequest):
    result = delete_content(req.content_type, req.content_name,project_name=req.project_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/update_ownership")
def api_update_ownership(req: UpdateOwnershipRequest):
    # Placeholder call to the script function
    result = update_ownership(req.content_type, req.content_name, req.current_owner, req.new_owner, req.project_name)
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

@router.post("/download")
def api_download(req: DownloadRequest):
    # Placeholder call to the script function
    result = download_content(req.content_type, req.content_name, req.project_name, req.format_type)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result 