import logging
import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Add base_setup directory to Python path
base_setup_path = str(Path(__file__).parent.parent.parent / "base_setup")
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import (
    load_config,
    setup_logging,
    get_tableau_server_and_auth,
    ensure_directory_exists,
)

import tableauserverclient as TSC

# Setup logging
logger = setup_logging(os.path.join(base_setup_path, "config", "logging_config.yaml"))


def extract_twb_from_twbx(twbx_path: str, extract_to_dir: str) -> str:
    with zipfile.ZipFile(twbx_path, "r") as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith(".twb"):
                zip_ref.extract(file, extract_to_dir)
                twb_path = os.path.join(extract_to_dir, file)
                logger.info(f"Extracted .twb: {twb_path}")
                return twb_path
    raise FileNotFoundError("No .twb file found in the .twbx archive.")


def scan_for_extensions(twb_path: str) -> dict:
    try:
        tree = ET.parse(twb_path)
        root = tree.getroot()

        tabpy_used = any("tabpy" in el.attrib.get("url", "").lower() for el in root.iter("script"))
        einstein_used = any("einstein" in el.attrib.get("url", "").lower() for el in root.iter("extension"))
        viz_ext_used = any("extension" in el.tag.lower() for el in root.iter())

        return {
            "tabpy": tabpy_used,
            "einstein": einstein_used,
            "viz_ext": viz_ext_used
        }

    except Exception as e:
        logger.error(f"Failed to parse {twb_path}: {e}", exc_info=True)
        return {
            "tabpy": False,
            "einstein": False,
            "viz_ext": False
        }


def check_extensions_in_workbook(workbook_name: str):
    config = load_config(os.path.join(base_setup_path, "config", "config.yaml"))
    download_dir = config.get("tableau", {}).get("download_path", "downloads")
    ensure_directory_exists(download_dir)

    server, auth = get_tableau_server_and_auth(config)

    with server.auth.sign_in(auth):
        logger.info("Signed into Tableau Server")

        # Fetch all workbooks
        logger.info("Querying all workbooks on site")
        workbooks = list(TSC.Pager(server.workbooks))

        workbook = next((w for w in workbooks if w.name.strip().lower() == workbook_name.strip().lower()), None)
        if not workbook:
            print(f"Workbook '{workbook_name}' not found.")
            return

        # Download workbook — don't add extension manually
        download_stub = os.path.join(download_dir, workbook.name.replace(' ', '_'))
        downloaded_path = server.workbooks.download(workbook.id, filepath=download_stub, include_extract=False)
        logger.info(f"Downloaded workbook to {downloaded_path} (ID: {workbook.id})")

        # Extract .twb and scan
        twb_path = extract_twb_from_twbx(downloaded_path, download_dir)
        ext_usage = scan_for_extensions(twb_path)

        # Output result
        print("\n=== Dashboard Extension Scan ===")
        print(f"Workbook         : {workbook.name}")
        print(f"Path             : {twb_path}")
        print(f"Uses TabPy       : {'✅' if ext_usage['tabpy'] else '❌'}")
        print(f"Uses Einstein    : {'✅' if ext_usage['einstein'] else '❌'}")
        print(f"Uses Viz Ext     : {'✅' if ext_usage['viz_ext'] else '❌'}")
        return {
            "workbook": workbook.name,
            "path": twb_path,
            "tabpy_used": ext_usage["tabpy"],
            "einstein_used": ext_usage["einstein"],
            "viz_ext_used": ext_usage["viz_ext"]
        }


if __name__ == "__main__":
    # Provide workbook name here
    check_extensions_in_workbook("Superstore")
