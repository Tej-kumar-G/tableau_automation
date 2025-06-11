import os
import time
import unittest
from fastapi.testclient import TestClient
from main import app


class TestCustomApiIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test client and create unique projects for each test case."""
        cls.client = TestClient(app)
        cls.timestamp = int(time.time())

        # Common workbook and source project
        cls.test_workbook_name = "Superstore"
        cls.source_project_name = "Samples"

        # Unique project names for each test
        cls.projects = {
            "create": f"Project_Create_{cls.timestamp}",
            "move": f"Project_Move_{cls.timestamp + 1}",
            "ownership": f"Project_Ownership_{cls.timestamp + 2}",
            "download": f"Project_Download_{cls.timestamp + 3}",
            "delete": f"Project_Delete_{cls.timestamp + 4}",
        }

        # Create all projects once
        for key, project_name in cls.projects.items():
            if key == "create":
                continue
            print(f"Creating project for {key}: {project_name}")
            resp = cls.client.post("/tableau/create_project", json={
                "project_name": project_name,
                "description": f"Test project for {key}"
            })
            print(f"Create response [{key}]: {resp.status_code} - {resp.json().get('message', '')}")

    @classmethod
    def tearDownClass(cls):
        """Delete all test projects created."""
        print("\nCleaning up test projects...")
        for key, project_name in cls.projects.items():
            response = cls.client.post("/tableau/delete_content", json={
                "content_type": "project",
                "content_name": project_name
            })
            print(f"Deleted project [{key}]: {project_name} - {response.status_code}")

    def test_create_project(self):
        """Test attempting to create an already existing project."""
        project = self.projects["create"]
        response = self.client.post("/tableau/create_project", json={
            "project_name": project,
            "description": "Attempt duplicate creation"
        })
        self.assertEqual(response.status_code, 200)

    def test_move_content(self):
        """Test moving a workbook within the same project (simulated)."""
        project = self.projects["move"]
        self.client.post("/tableau/copy_content", json={
            "workbook_name": self.test_workbook_name,
            "source_project": self.source_project_name,
            "target_project": project
        })

        response = self.client.post("/tableau/move_content", json={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "source_project": project,
            "new_project": project
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))

    def test_update_ownership(self):
        """Test updating ownership of a copied workbook."""
        project = self.projects["ownership"]
        self.client.post("/tableau/copy_content", json={
            "workbook_name": self.test_workbook_name,
            "source_project": self.source_project_name,
            "target_project": project
        })

        # These emails must be valid Tableau users in your org
        current_owner = "tej.gangineni@gmail.com"
        new_owner = "nitheeshkumargorla111@gmail.com"

        response = self.client.post("/tableau/update_ownership", json={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "project_name": project,
            "current_owner": current_owner,
            "new_owner": new_owner
        })
        self.assertEqual(response.status_code, 200, f"Ownership update failed: {response.text}")
        self.assertTrue(response.json().get("success"))

    def test_download_content(self):
        """Test downloading a workbook after copying it."""
        project = self.projects["download"]
        self.client.post("/tableau/copy_content", json={
            "workbook_name": self.test_workbook_name,
            "source_project": self.source_project_name,
            "target_project": project
        })

        response = self.client.post("/tableau/download_content", json={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "project_name": project
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        download_path = response.json().get("download_path")
        self.assertTrue(download_path and os.path.exists(download_path),
                        f"File not found at {download_path}")

    def test_delete_content(self):
        """Test deleting a copied workbook."""
        project = self.projects["delete"]
        self.client.post("/tableau/copy_content", json={
            "workbook_name": self.test_workbook_name,
            "source_project": self.source_project_name,
            "target_project": project
        })

        response = self.client.post("/tableau/delete_content", json={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "project_name": project
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))


    def test_slack_connection(self):
        """Test Slack connection endpoint."""
        response = self.client.get("/tableau/slack_connection")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
