import json
import os
import sys
from pathlib import Path
import pytest

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


# ----------------- Logging Helper ----------------- #
def log_section(title: str, data: dict):
    logger.info(f"========== {title.upper()} ==========")
    for key, value in data.items():
        logger.info(f"{key:<18}: {value}")
    logger.info(f"========== END: {title.upper()} ==========\n")


# ----------------- Test Cases ----------------- #
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


@pytest.mark.asyncio
async def test_audit_sites(async_client):
    site_name = test_cfg["site_name"]

    resp = await async_client.post("/tableau/audit_site", params={"site_name": site_name})

    result = resp.json()

    log_section("Audit Sites", {
        "📡 Status Code": resp.status_code,
        "✅ Site": result.get("site"),
        "📊 User Count": result.get("user_count"),
        "👥 Group Count": result.get("group_count"),
        "📋 Role Breakdown": result.get("role_breakdown", {})
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_validate_personal_spaces(async_client):
    resp = await async_client.get("/tableau/personal_spaces")
    log_section("Validate Personal Spaces", {
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success"),
        "📊 Results": resp.json().get("results", [])
    })
    assert resp.status_code == 200
    assert resp.json().get("success") is True
    assert isinstance(resp.json().get("results"), list)


@pytest.mark.asyncio
async def test_get_lineage_for_workbook(async_client):
    resp = await async_client.get("/tableau/get_lineage_for_workbook", params={
        "workbook_name": test_cfg["workbook_name"]
    })
    log_section("Get Lineage for Workbook", {
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success"),
        "📊 Lineage Data": resp.json().get("response", {})
    })
    assert resp.status_code == 200
    assert resp.json().get("success") is True
    assert isinstance(resp.json().get("response"), dict)


@pytest.mark.asyncio
async def test_check_tcm_access(async_client):
    resp = await async_client.get("/tableau/check_tcm_access", params={
        "site_name": test_cfg["site_name"]
    })
    log_section("Check TCM Access", {
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success"),
        "🔗 JSON": resp.json()
    })
    assert resp.status_code == 200
    assert resp.json().get("success") is True


@pytest.mark.asyncio
async def test_download_view_features(async_client):
    resp = await async_client.get("/tableau/download_view_features", params={
        "view_name": test_cfg["view_name"],
        "download_format": "image"
    })
    log_section("Download View Features", {
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success"),
        "🔗 Message": resp.json().get("message", "N/A"),
        "📥 Path": resp.json().get("path", "N/A")
    })
    assert resp.status_code == 200
    assert resp.json().get("success") is True


@pytest.mark.asyncio
async def test_check_extensions_in_workbook(async_client):
    resp = await async_client.get("/tableau/check_extensions_in_workbook", params={
        "workbook_name": test_cfg["workbook_name"]
    })
    log_section("Check Extensions in Workbook", {
        "📡 Status Code": resp.status_code,
        "✅ Workbook": resp.json().get("workbook"),
        "📂 Path": resp.json().get("path"),
        "🔗 TabPy Used": resp.json().get("tabpy_used"),
        "🔗 Einstein Used": resp.json().get("einstein_used"),
        "🔗 Viz Ext Used": resp.json().get("viz_ext_used")
    })
    assert resp.status_code == 200
    assert resp.json().get("workbook") == test_cfg["workbook_name"]


@pytest.mark.asyncio
async def test_content_labels_and_description(async_client):
    resp = await async_client.get("/tableau/confirm_content_labels_and_description")
    log_section("Confirm Content Labels and Description", {
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success"),
        "🔗 report": resp.json().get("items", "N/A")
    })
    assert resp.status_code == 200
    assert resp.json().get("success") is True


@pytest.mark.asyncio
async def test_validate_pulse(async_client):
    resp = await async_client.get("/tableau/validate_pulse", params={
        "datastore_name": test_cfg["datastore_name"]
    })
    log_section("Validate Pulse", {
        "📡 Status Code": resp.status_code,
        "✅ Success": resp.json().get("success"),
        "🔗 Message": resp.json().get("message", "N/A")
    })
    assert resp.status_code == 200
    if resp.json().get("success") is False:
        assert resp.json().get("message") == "Pulse is not enabled on this site."
    else:
        assert resp.json().get("success") is True
        assert resp.json().get("message") == "Pulse metric created successfully."
