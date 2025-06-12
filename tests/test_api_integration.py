import os
import sys
import time
from pathlib import Path

import pytest
import pytest_asyncio
import logging
from httpx import AsyncClient, ASGITransport
from main import app

from base_setup.utils.common_utils import setup_logging


# Setup logging
# ------ Add base_setup to sys.path and import logging setup ------
base_setup_path = str(Path(__file__).parent.parent / 'base_setup')
sys.path.append(base_setup_path)
# ------ Setup logging using external YAML config ------
setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger("tableau_automation")

# Constants
TEST_WORKBOOK = "Superstore"
SOURCE_PROJECT = "Samples"


# ----------- Logging Helper ----------- #
def log_section(title: str, data: dict):
    logger.info(f"\n========== {title.upper()} ==========")
    for key, value in data.items():
        logger.info(f"{key:<18}: {value}")
    logger.info(f"========== END: {title.upper()} ==========\n")


# ----------- Fixtures ----------- #
@pytest.fixture(scope="session")
def timestamp():
    return int(time.time())


@pytest.fixture(scope="session")
def test_projects(timestamp):
    return {
        "create": f"Project_Create_{timestamp}",
        "move": f"Project_Move_{timestamp + 1}",
        "ownership": f"Project_Ownership_{timestamp + 2}",
        "download": f"Project_Download_{timestamp + 3}",
        "delete": f"Project_Delete_{timestamp + 4}",
    }


@pytest_asyncio.fixture(scope="session")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session", autouse=True)
async def one_time_project_setup_and_teardown(async_client, test_projects):
    logger.info("🚧 One-time setup: Creating all test projects (except 'create')")
    for key, name in test_projects.items():
        if key == "create":
            continue
        resp = await async_client.post("/tableau/create_project", json={
            "project_name": name,
            "description": f"Test project for {key}"
        })
        logger.info(f"📁 Created [{key}] '{name}' -> {resp.status_code}")
    yield
    logger.info("🧹 Cleanup: Deleting all test projects")
    for key, name in test_projects.items():
        resp = await async_client.post("/tableau/delete_content", json={
            "content_type": "project",
            "content_name": name
        })
        logger.info(f"🗑️ Deleted [{key}] '{name}' -> {resp.status_code}")


# ----------- Helper ----------- #
async def copy_workbook(async_client, project):
    logger.info(f"📥 Copying workbook '{TEST_WORKBOOK}' to project '{project}'")
    resp = await async_client.post("/tableau/copy_content", json={
        "workbook_name": TEST_WORKBOOK,
        "source_project": SOURCE_PROJECT,
        "target_project": project
    })
    logger.info(f"📥 Copy Response: {resp.status_code} | {resp.json()}")
    return resp


# ----------- Test Cases ----------- #

@pytest.mark.asyncio
async def test_create_project(async_client, test_projects):
    project = test_projects["create"]
    resp = await async_client.post("/tableau/create_project", json={
        "project_name": project,
        "description": "Duplicate create test"
    })
    log_section("Create Project", {
        "📁 Project": project,
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success", "N/A"),
        "📨 Message": resp.json().get("message", "N/A")
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_move_content(async_client, test_projects):
    project = test_projects["move"]
    await copy_workbook(async_client, project)
    resp = await async_client.post("/tableau/move_content", json={
        "content_type": "workbook",
        "content_name": TEST_WORKBOOK,
        "source_project": project,
        "new_project": project
    })
    log_section("Move Workbook", {
        "📁 Project": project,
        "📄 Workbook": TEST_WORKBOOK,
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success")
    })
    assert resp.status_code == 200
    assert resp.json().get("success")


@pytest.mark.asyncio
async def test_update_ownership(async_client, test_projects):
    project = test_projects["ownership"]
    await copy_workbook(async_client, project)
    current_owner = "tej.gangineni@gmail.com"
    new_owner = "nitheeshkumargorla111@gmail.com"
    resp = await async_client.post("/tableau/update_ownership", json={
        "content_type": "workbook",
        "content_name": TEST_WORKBOOK,
        "project_name": project,
        "current_owner": current_owner,
        "new_owner": new_owner
    })
    log_section("Update Ownership", {
        "📁 Project": project,
        "📄 Workbook": TEST_WORKBOOK,
        "👤 From": current_owner,
        "👤 To": new_owner,
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success")
    })
    assert resp.status_code == 200
    assert resp.json().get("success")


@pytest.mark.asyncio
async def test_download_content(async_client, test_projects):
    project = test_projects["download"]
    await copy_workbook(async_client, project)
    resp = await async_client.post("/tableau/download_content", json={
        "content_type": "workbook",
        "content_name": TEST_WORKBOOK,
        "project_name": project
    })
    data = resp.json()
    log_section("Download Workbook", {
        "📁 Project": project,
        "📄 Workbook": TEST_WORKBOOK,
        "📡 Status Code": resp.status_code,
        "✅ Success": data.get("success"),
        "📂 Path Exists": os.path.exists(data.get("download_path", "")),
        "📎 Path": data.get("download_path", "")
    })
    assert resp.status_code == 200
    assert data.get("success")
    assert os.path.exists(data.get("download_path"))


@pytest.mark.asyncio
async def test_delete_content(async_client, test_projects):
    project = test_projects["delete"]
    await copy_workbook(async_client, project)
    resp = await async_client.post("/tableau/delete_content", json={
        "content_type": "workbook",
        "content_name": TEST_WORKBOOK,
        "project_name": project
    })
    log_section("Delete Workbook", {
        "📁 Project": project,
        "📄 Workbook": TEST_WORKBOOK,
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success")
    })
    assert resp.status_code == 200
    assert resp.json().get("success")


@pytest.mark.asyncio
async def test_slack_connection(async_client):
    resp = await async_client.get("/tableau/slack_connection")
    log_section("Slack Connectivity", {
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success"),
        "🔗 Message": resp.json().get("message", "N/A")
    })
    assert resp.status_code == 200
    assert resp.json().get("success")
