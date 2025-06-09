# Tableau Automation Project

Automate Tableau operations like content management, ownership updates, downloads, and revision history retrieval using Python and Tableau Server Client API.

---

## Project Structure

```plaintext
    tableau_automation 2/
    ├── main.py
    ├── routers/
    │ └── tableau.py
    ├── base_setup/
    │ ├── config/
    │ │ ├── config.example.yaml
    │ │ └── logging_config.yaml
    │ ├── utils/
    │ │ └── common_utils.py
    │ └── requirements.txt
    ├── downloads/
    ├── logs/
    ├── scripts/
    │ ├── content_management/
    │ ├── download_utils/
    │ └── revision_history/
    ├── tests/
    └── venv/
```



---

## Features

- Manage Tableau content (create, move, delete).
- Update ownership of workbooks and data sources.
- Download workbooks, views, and data sources in various formats.
- Fetch revision history for Tableau workbooks.
- Configurable via YAML config file or environment variables.
- FastAPI-based API endpoints for automation and integration.

---

## Prerequisites

- Python 3.8+
- Tableau Server or Tableau Online with API access
- Personal Access Token for authentication

---

## Setup

1. **Clone the repository**

    ```bash
    git clone https://github.com/your-account-name/tableau_automation.git
    cd tableau_automation
    ``` 


2. Create and activate virtual environment

    ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    venv\Scripts\activate      # Windows
    ```

3. Install dependencies

    ```bash
    pip install -r base_setup/requirements.txt
    ```


4. Configure your Tableau connection

    Copy base_setup/config/config.example.yaml to config.yaml

    Fill in your Tableau server URL, token, and site ID in config.yaml

---
 
 
Running the Project

    Start the FastAPI server:

        uvicorn main:app --reload


Usage
    Use the provided API endpoints in /routers/tableau.py to:

        Create, move, delete content

        Update ownership

        Download Tableau content

        Retrieve revision history

    Refer to the API docs for request/response details.


Logging

    Logs are stored in logs/tableau_automation.log with configurable levels in logging_config.yaml.


Tests
    Run tests with:
        pytest tests/


License

    MIT License
