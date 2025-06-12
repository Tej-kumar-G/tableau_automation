
# 📊 Tableau Automation Project

Automate Tableau operations such as content management, ownership transfer, downloads, and revision history using Python scripts. This project is script-first, focusing on standalone automation, with optional API support via FastAPI.

---

## 🗂️ Project Structure


```
tableau_automation/
├── main.py                         # Optional FastAPI entry point
├── routers/
│   └── tableau.py                  # API endpoint definitions
├── base_setup/
│   ├── config/
│   │   ├── config.yaml             # Tableau & Slack config
│   │   └── logging_config.yaml     # Logging setup
│   └── utils/                      # Shared helpers/utilities
├── scripts/                        # Core Tableau automation logic
│   ├── content_management/
│   ├── download_utils/
│   ├── monitoring/
│   ├── revision_history/
│   └── site_monitoring/
│       ├── run_monitoring.py
│       └── slack_connectivity.py
├── test_data/                      # Sample inputs/data
├── tests/
│   ├── downloads/                  # Download output directory
│   ├── logs/                       # Log output directory
│   ├── conftest.py
│   ├── test_misc_connectivity.py
│   └── test_tableau_workflow.py
├── requirements.txt
├── README.md
└── .gitignore
```


## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone ....git
cd tableau_automation
```

### 2. Create & Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Tableau & Slack

Create a `config.yaml` in `base_setup/config/` with the following structure:

```yaml
tableau:
  server_url: ""
  token_name: ""
  personal_access_token: ""
  site_id: ""
  log_path: tests/logs/tableau.log
  download_path: tests/downloads

slack:
  webhook_url: ""
```

---

## 🚀 How to Run Scripts

Each Python script inside `scripts/` is standalone. Run them as:

```bash
python scripts/site_monitoring/run_monitoring.py
```

Logs will be stored in `tests/logs/` and any downloaded files will be placed in `tests/downloads/`.

---

## 🧪 Run Tests

```bash
PYTHONPATH=.:$PYTHONPATH pytest tests/
```

This command validates connectivity, Tableau operations, and logging via defined test cases.

---

## 🌐 Optional FastAPI API

To run the API server:

```bash
uvicorn main:app --reload
```

Open in browser: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 💬 Interview Highlights


- **Primary focus is on automation scripts**, not APIs.
- **All logic is config-driven** via YAML for easy changes.
- **Secure PAT-based access** for Tableau authentication.
- **Test cases included** for repeatable validations.
- **Slack integration** for alerts/notifications on execution.


---

## 📜 License

MIT License – free for personal and commercial use.

