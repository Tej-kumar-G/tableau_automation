import os
import sys
import time
import pytest
import pytest_asyncio
import logging
from pathlib import Path

# ----------------- Path Setup ----------------- #
base_path = Path(__file__).parent
base_setup_path = os.path.join(base_path.parent, 'base_setup')
sys.path.append(base_setup_path)

# ----------------- Imports ----------------- #
from base_setup.utils.common_utils import load_config, setup_logging

# ----------------- Config & Logging ----------------- #
config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
test_cfg = config['test_data']
logger = setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))

# ----------------- Constants ----------------- #
TEST_WORKBOOK = test_cfg["workbook_name"]
SOURCE_PROJECT = test_cfg["source_project"]
CURRENT_OWNER = test_cfg["owner_current"]
NEW_OWNER = test_cfg["owner_new"]


# ----------------- Logging Helper ----------------- #
def log_section(title: str, data: dict):
    logger.info(f"========== {title.upper()} ==========")
    for key, value in data.items():
        logger.info(f"{key:<18}: {value}")
    logger.info(f"========== END: {title.upper()} ==========\n")


# ----------------- Fixtures ----------------- #
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


# ----------------- Helper ----------------- #
async def copy_workbook(async_client, project):
    logger.info(f"📥 Copying workbook '{TEST_WORKBOOK}' to project '{project}'")
    resp = await async_client.post("/tableau/copy_content", json={
        "workbook_name": TEST_WORKBOOK,
        "source_project": SOURCE_PROJECT,
        "target_project": project
    })
    logger.info(f"📥 Copy Response: {resp.status_code} | {resp.json()}")
    return resp


# ----------------- Test Cases ----------------- #
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
    resp = await async_client.post("/tableau/update_ownership", json={
        "content_type": "workbook",
        "content_name": TEST_WORKBOOK,
        "project_name": project,
        "current_owner": CURRENT_OWNER,
        "new_owner": NEW_OWNER
    })
    log_section("Update Ownership", {
        "📁 Project": project,
        "📄 Workbook": TEST_WORKBOOK,
        "👤 From": CURRENT_OWNER,
        "👤 To": NEW_OWNER,
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
