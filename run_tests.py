import os
import sys
from datetime import datetime
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout

import pytest

# Setup paths
base_path = Path(__file__).parent
base_setup_path = os.path.join(base_path, 'base_setup')
sys.path.append(base_setup_path)

# Imports
from base_setup.utils.common_utils import load_config, setup_logging
from base_setup.utils.email_utils import send_email

# Load config and logger
config = load_config(os.path.join(base_setup_path, 'config', 'config.yaml'))
logger = setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))


def run_pytest_and_capture():
    logger.info("🚀 Starting test suite...")
    output = StringIO()
    with redirect_stdout(output):
        exit_code = pytest.main(["tests/", "--tb=short", "-q"])
    results = output.getvalue()

    # ✅ Do not log while stdout is redirected.
    logger.info(f"✅ Test suite completed with exit code: {exit_code}")
    return exit_code, results


def send_failure_email(results: str):
    """Send email with embedded traceback output from pytest."""
    subject = config["email"]["mail_sub"]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    body = f"""
    <p><strong style='color:red;'>❌ Test failures detected in Tableau Automation Suite</strong></p>
    <p>⏰ Run Time: {timestamp}</p>
    <p>📍 Location: <code>tests/</code></p>
    <p><strong>📋 Summary:</strong></p>
    <pre style="background:#f9f9f9;border:1px solid #ccc;padding:10px;">{results}</pre>
    <p style="color:gray;"><i>Auto-generated failure report.</i></p>
    """
    send_email(subject, body, config)


if __name__ == "__main__":
    exit_code, output = run_pytest_and_capture()

    if exit_code != 0:
        logger.warning("❗ Tests failed. Sending alert email with details...")
        send_failure_email(output)
    else:
        logger.info("✅ All tests passed. No email sent.")