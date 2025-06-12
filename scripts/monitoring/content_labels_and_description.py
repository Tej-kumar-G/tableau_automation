import os
import sys
import logging
from pathlib import Path
from tableauserverclient import Server, Pager

# Setup base path
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth

# Logging
setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))
logger = logging.getLogger('metadata_check')


def check_metadata_for_content():
    config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
    server, auth = get_tableau_server_and_auth(config)

    with server.auth.sign_in(auth):
        logger.info("Signed into Tableau Cloud")

        # --- Workbooks ---
        logger.info("Fetching workbooks...")
        workbooks = list(Pager(server.workbooks))

        workbook_results = []
        for wb in workbooks:
            workbook_results.append({
                "type": "workbook",
                "name": wb.name,
                "project": wb.project_name,
                "description": bool(wb.description and wb.description.strip()),
                "has_data_labels": bool(getattr(wb, 'content_label_ids', []))
            })

        # --- Datasources ---
        logger.info("Fetching datasources...")
        datasources = list(Pager(server.datasources))

        datasource_results = []
        for ds in datasources:
            datasource_results.append({
                "type": "datasource",
                "name": ds.name,
                "project": ds.project_name,
                "description": bool(ds.description and ds.description.strip()),
                "has_data_labels": bool(getattr(ds, 'content_label_ids', []))
            })

        all_results =  workbook_results + datasource_results
        return {
            "success": True,
            "items": all_results
        }


if __name__ == "__main__":
    results = check_metadata_for_content()

    print("\n=== Description & Label Check ===")
    for item in results:
        print(f"{item['type'].capitalize():<10} | {item['name']:<30} | Project: {item['project']:<20} | "
              f"Desc: {'✅' if item['description'] else '❌'} | Labels: {'✅' if item['has_data_labels'] else '❌'}")