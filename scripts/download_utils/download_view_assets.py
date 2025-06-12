

import logging
import os
import sys
from pathlib import Path

# Setup paths
base_setup_path = str(Path(__file__).parent.parent.parent / 'base_setup')
sys.path.append(base_setup_path)

from base_setup.utils.common_utils import load_config, setup_logging, get_tableau_server_and_auth, ensure_directory_exists

# Logging
logger = setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))


def download_view_asset(view_name: str, download_type: str = "image") -> dict:
    """
    Download Tableau view as image/pdf/csv.

    Args:
        view_name (str): Name of the view (sheet or dashboard)
        download_type (str): "image", "pdf", or "csv"

    Returns:
        dict: { success, message, path? }
    """
    try:
        config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
        server, auth = get_tableau_server_and_auth(config)
        download_dir = config.get("tableau", {}).get("download_path", "downloads")
        ensure_directory_exists(download_dir)

        with server.auth.sign_in(auth):
            logger.info("Signed into Tableau Server")

            all_views, _ = server.views.get()
            view = next((v for v in all_views if v.name.strip().lower() == view_name.strip().lower()), None)

            if not view:
                return {"success": False, "message": f"View '{view_name}' not found."}

            # Populate the desired asset
            if download_type == "pdf":
                server.views.populate_pdf(view)
                content = view.pdf
                ext = "pdf"
            elif download_type == "image":
                server.views.populate_image(view)
                content = view.image
                ext = "png"
            elif download_type == "csv":
                server.views.populate_csv(view)
                content = b''.join(view.csv)  # <-- Fix: join generator output into bytes
                ext = "csv"
            else:
                return {"success": False, "message": f"Invalid download type '{download_type}'"}

            filename = f"{view.name.replace(' ', '_')}.{ext}"
            full_path = os.path.join(download_dir, filename)

            with open(full_path, "wb") as f:
                f.write(content)

            logger.info(f"{download_type.upper()} for view '{view.name}' saved to {full_path}")
            return {"success": True, "message": f"{download_type.capitalize()} downloaded", "path": full_path}

    except Exception as e:
        logger.error(f"Failed to download view asset: {e}", exc_info=True)
        return {"success": False, "message": f"Error: {e}"}


if __name__ == "__main__":
    view_name = "Product"  # Change this to your actual view name

    print(download_view_asset(view_name, download_type="image"))
    print(download_view_asset(view_name, download_type="pdf"))
    print(download_view_asset(view_name, download_type="csv"))

