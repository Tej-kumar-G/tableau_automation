import os

import yaml
import logging
import logging.config
from pathlib import Path
from tableauserverclient import Server, PersonalAccessTokenAuth


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise Exception(f"Error loading config file {config_path}: {str(e)}")


def setup_logging(logging_config_path: str):
    """Setup logging configuration."""
    try:
        with open(logging_config_path, 'r') as file:
            logging_config = yaml.safe_load(file)
            log_file_path = logging_config['handlers']['file']['filename']
            log_dir = os.path.dirname(log_file_path)
            os.makedirs(log_dir, exist_ok=True)
            logging.config.dictConfig(logging_config)
            return logging.getLogger("tableau_automation")
    except Exception as e:
        raise Exception(f"Error setting up logging: {str(e)}")


def ensure_directory_exists(directory: str):
    """Ensure that a directory exists, create if it doesn't."""
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_tableau_server_and_auth(config: dict) -> tuple[Server, PersonalAccessTokenAuth]:
    """
    Initialize and return a Tableau Server instance and PersonalAccessTokenAuth object.
    """
    server = Server(config['tableau']['server_url'], use_server_version=True)
    tableau_auth = PersonalAccessTokenAuth(
        config['tableau']['token_name'],
        config['tableau']['personal_access_token'],
        site_id=config['tableau']['site_id']
    )
    return server, tableau_auth
