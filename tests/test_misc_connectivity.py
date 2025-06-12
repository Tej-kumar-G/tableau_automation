# test_misc_connectivity.py

import logging
import pytest

logger = logging.getLogger("tableau_automation")


def log_section(title: str, data: dict):
    logger.info(f"========== {title.upper()} ==========")
    for key, value in data.items():
        logger.info(f"{key:<18}: {value}")
    logger.info(f"========== END: {title.upper()} ==========\n")


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
    resp = await async_client.post("/tableau/audit_site", params={
        "site_name": "nitidev",
    })
    log_section("Audit Sites", {
        "📡 Status Code": resp.status_code,
        "✅ Site": resp.json().get("site"),
        "📊 User Count": resp.json().get("user_count"),
        "👥 Group Count": resp.json().get("group_count"),
        "📋 Role Breakdown": resp.json().get("role_breakdown", {})
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
        "workbook_name": "Superstore"
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
        "site_name": "nitidev"
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
        "view_name": "Product",
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
        "workbook_name": "Superstore"
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
    assert resp.json().get("workbook") == "Superstore"


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
