# import unittest
# from fastapi.testclient import TestClient
# import sys
# from pathlib import Path
# import os
# import yaml
# import time # Import time for potential delays between operations

# # Add the project root to the Python path
# project_root = str(Path(__file__).parent.parent)
# sys.path.append(project_root)

# from main import app
# from base_setup.utils.common_utils import load_config, get_tableau_server_and_auth

# class TestTableauApiIntegration(unittest.TestCase):
#     def setUp(self):
#         """Set up test client and load config."""
#         self.client = TestClient(app)
#         # self.config = load_config('base_setup/config/config.yaml')
#         # self.server, self.tableau_auth = get_tableau_server_and_auth(self.config)
        
#         # Define test resources names (make them unique if running tests frequently)
#         self.test_project_name = "TestProjectForAutomation" + str(int(time.time()))
#         self.test_project_name_2 = "TestProjectForAutomation_Two" + str(int(time.time()))
#         self.test_workbook_name = "TestWorkbookForAutomation" + str(int(time.time()))
#         self.test_datasource_name = "TestDatasourceForAutomation" + str(int(time.time()))
        
#         # Define a dummy workbook file path for testing create/download
#         # You'll need to replace this with a path to an actual .twb or .twbx file
#         # or create one dynamically if possible/necessary.
#         self.dummy_workbook_path = "./test_data/dummy_workbook.twbx" # Example path
#         self.dummy_datasource_path = "./test_data/dummy_datasource.tds" # Example path
        
#         # Ensure a test data directory exists
#         os.makedirs('test_data', exist_ok=True)
#         # Create dummy files if they don't exist (basic content)
#         if not os.path.exists(self.dummy_workbook_path):
#             with open(self.dummy_workbook_path, "w") as f:
#                 f.write("<workbook></workbook>") # Basic valid XML for .twb/.twbx
                
#         if not os.path.exists(self.dummy_datasource_path):
#              with open(self.dummy_datasource_path, "w") as f:
#                 f.write("<datasource></datasource>") # Basic valid XML for .tds
                
#         # --- Create resources needed for multiple tests ---
#         # Create test projects
#         self.client.post("/tableau/create_project", json={
#             "project_name": self.test_project_name,
#             "description": "Primary test project"
#         })
#         self.client.post("/tableau/create_project", json={
#             "project_name": self.test_project_name_2,
#             "description": "Secondary test project"
#         })
#         # Create a test workbook
#         self.client.post("/tableau/create_workbook", json={
#             "workbook_name": self.test_workbook_name,
#             "project_name": self.test_project_name,
#             "file_path": self.dummy_workbook_path
#         })


#     def tearDown(self):
#         """Clean up test resources from Tableau Server."""
#         print(f"\nCleaning up test resources...")
#         # with self.server.auth.sign_in(self.tableau_auth):
#         #     # Attempt to delete test workbook (important to delete content before projects)
#         #     try:
#         #         workbooks, _ = self.server.workbooks.filter(filter_expr=self.server.workbooks.filter.ByFieldName('name', '_eq_', self.test_workbook_name))
#         #         if workbooks:
#         #             self.server.workbooks.delete(workbooks[0].id)
#         #             print(f"Deleted workbook: {self.test_workbook_name}")
#         #     except Exception as e:
#         #         print(f"Error deleting workbook {self.test_workbook_name}: {e}")

#             # Delete test datasource (if implemented and tested)
#             # try:
#             #     datasources, _ = self.server.datasources.filter(filter_expr=self.server.datasources.filter.ByFieldName('name', '_eq_', self.test_datasource_name))
#             #     if datasources:
#             #         self.server.datasources.delete(datasources[0].id)
#             #         print(f"Deleted datasource: {self.test_datasource_name}")
#             # except Exception as e:
#             #     print(f"Error deleting datasource {self.test_datasource_name}: {e}")

#             # Give Tableau Server a moment to process deletions before trying to delete projects
#             # time.sleep(2)
            
#             # Attempt to delete test projects

#         for project_name in [self.test_project_name, self.test_project_name_2]:
#             # try:
#             #     projects, _ = self.server.projects.filter(filter_expr=self.server.projects.filter.ByFieldName('name', '_eq_', project_name))
#             #     if projects:
#             #         self.server.projects.delete(projects[0].id)
#             #         print(f"Deleted project: {project_name}")
#             # except Exception as e:
#             #         print(f"Error deleting project {project_name}. It might not be empty or an error occurred: {e}")
#             try:
#                 self.client.post("/tableau/delete_content", json={
#                     "content_type": "workbook",
#                     "content_name": self.test_workbook_name,
#                     "project_name": project_name
#                 })
#                 print(f"Deleted workbook: {self.test_workbook_name}")
#             except Exception as e:
#                 print(f"Error deleting workbook: {e}")


#     def test_01_create_project(self):
#         """Test creating a project via the API."""
#         # This is now handled in setUp for dependent tests, but keep a basic check
#         response = self.client.post("/tableau/create_project", json={
#             "project_name": "TempProjectForTest" + str(int(time.time()) + 1),
#             "description": "Temporary project for create test"
#         })
#         self.assertEqual(response.status_code, 200, f"Response: {response.text}")
#         self.assertTrue(response.json()["success"])
#         self.assertIn("Successfully created project", response.json()["message"])

#         # Clean up this specific project
#         # with self.server.server.auth.sign_in(self.tableau_auth):
#         #      try:
#         #          # A more robust way is to fetch the project ID from the creation response if the API returned it.
#         #          # For now, rely on tearDown to clean up most resources.
#         #          pass # Relying on tearDown is simpler here
#         #      except Exception as e:
#         #          print(f"Error during cleanup of temporary project: {e}")

#     def test_02_create_workbook(self):
#         """Test creating a workbook via the API."""
#         # Workbook creation is handled in setUp. This test just verifies setUp succeeded implicitly.
#         # A more explicit test would assert the workbook exists on the server after setUp.
#         # For now, we assume setUp's API call was successful and rely on subsequent tests.
#         pass # Actual creation is in setUp

#     def test_03_move_content(self):
#         """Test moving content via the API."""
#         response = self.client.post("/tableau/move_content", json={
#             "content_type": "workbook",
#             "content_name": self.test_workbook_name,
#             "source_project": self.test_project_name,
#             "new_project": self.test_project_name_2
#         })
#         self.assertEqual(response.status_code, 200, f"Response: {response.text}")
#         self.assertTrue(response.json()["success"])
#         self.assertIn("Successfully moved workbook", response.json()["message"])
        
#         # Verify the workbook is now in the new project (optional but recommended)
#         # with self.server.server.auth.sign_in(self.tableau_auth): # Use self.tableau_auth here
#         #     workbooks, _ = self.server.workbooks.filter(filter_expr=self.server.workbooks.filter.ByFieldName('name', '_eq_', self.test_workbook_name))
#         #     self.assertTrue(len(workbooks) > 0)
#         #     self.assertEqual(workbooks[0].project_name, self.test_project_name_2)

#     def test_04_delete_content(self):
#         """Test deleting content via the API."""
#         # Create a temporary workbook to delete
#         temp_workbook_name = "TempWorkbookToDelete" + str(int(time.time()) + 2)
#         self.client.post("/tableau/create_workbook", json={
#              "workbook_name": temp_workbook_name,
#              "project_name": self.test_project_name, # Create in one of the test projects
#              "file_path": self.dummy_workbook_path
#          })
         
#         # Give Tableau Server a moment
#         time.sleep(2)
        
#         response = self.client.post("/tableau/delete_content", json={
#             "content_type": "workbook",
#             "content_name": temp_workbook_name
#         })
#         self.assertEqual(response.status_code, 200, f"Response: {response.text}")
#         self.assertTrue(response.json()["success"])
#         self.assertIn("Successfully deleted workbook", response.json()["message"])
        
#         # Verify the workbook is deleted (optional but recommended)
#         # with self.server.server.auth.sign_in(self.tableau_auth): # Use self.tableau_auth here
#         #     workbooks, _ = self.server.workbooks.filter(filter_expr=self.server.workbooks.filter.ByFieldName('name', '_eq_', temp_workbook_name))
#         #     self.assertEqual(len(workbooks), 0)

#     def test_05_update_ownership(self):
#         """Test updating content ownership via the API."""
#         # Requires a valid user ID on your Tableau Server
#         # Replace 'YOUR_TEST_USER_ID' with an actual user ID from your server for testing
#         test_user_id = "YOUR_TEST_USER_ID"
#         if test_user_id == "YOUR_TEST_USER_ID":
#             print("\nSkipping test_05_update_ownership: Replace 'YOUR_TEST_USER_ID' with a real user ID in tests/test_api_integration.py to enable this test.")
#             self.skipTest("Test user ID not configured.")
            
#         # Need a workbook to update ownership for (using the one created in setUp)
        
#         response = self.client.post("/tableau/update_ownership", json={
#             "content_type": "workbook",
#             "content_name": self.test_workbook_name,
#             "new_owner_id": test_user_id,
#             "project_name": self.test_project_name # Assuming the workbook is in the original project from setUp
#         })
#         self.assertEqual(response.status_code, 200, f"Response: {response.text}")
#         self.assertTrue(response.json()["success"])
#         self.assertIn("Successfully updated ownership", response.json()["message"])

#     def test_06_download_content(self):
#         """Test downloading content via the API."""
#         # Need a workbook to download (using the one created in setUp)
#         # Need a download format that is valid for the workbook and server
#         download_format = "twbx" # or 'pdf', 'csv' depending on workbook content and server capabilities
        
#         response = self.client.post("/tableau/download", json={
#             "content_type": "workbook",
#             "content_name": self.test_workbook_name,
#             "project_name": self.test_project_name, # Assuming the workbook is in the original project from setUp
#             "format_type": download_format
#         })
#         self.assertEqual(response.status_code, 200, f"Response: {response.text}")
#         self.assertTrue(response.json()["success"])
#         self.assertIn("Successfully downloaded", response.json()["message"])
#         self.assertIn("download_path", response.json())
        
#         # Optional: Verify the downloaded file exists (requires checking the returned download_path)
#         # downloaded_file_path = response.json()["download_path"]
#         # self.assertTrue(os.path.exists(downloaded_file_path))
#         # Optional: Clean up the downloaded file
#         # os.remove(downloaded_file_path)

#     # Skipping test for revision history (test_07_revision_history) because the script file could not be created.
#     # def test_07_revision_history(self): # Requires the script to be functional
#     #     """Test getting revision history via the API."""
#     #     pass

# if __name__ == '__main__':
#     # Note: To run these tests, you need a Tableau Server configured in
#     # base_setup/config/config.yaml and the server must be accessible.
#     # Ensure your dummy_workbook.twbx and dummy_datasource.tds files exist in ./test_data or update the paths.
#     # Remember to replace 'YOUR_TEST_USER_ID' in test_05_update_ownership with a real user ID.
#     unittest.main(verbosity=2) 


'''

import unittest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import time
from main import app

class TestCustomApiIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test client and resources before each test."""
        cls.client = TestClient(app)
        
        # Define unique resource name using timestamp to avoid conflicts
        cls.test_project_name = ""
        cls.test_project_copy = ""

        #Define exisiting workbook source
        cls.test_workbook_name = "Superstore"
        cls.source_project_name = "Samples"
        
        # Define dummy file path
        cls.dummy_workbook_path = "./test_data/dummy_workbook.twbx"
        
        # Create test_data directory and dummy file
        os.makedirs("test_data", exist_ok=True)
        if not os.path.exists(cls.dummy_workbook_path):
            with open(cls.dummy_workbook_path, "w") as f:
                f.write("<workbook></workbook>")

    @classmethod
    def tearDownClass(cls):
        """Clean up test resources after each test."""
        print(f"\nCleaning up test resources...")
        try:
            cls.client.post("/tableau/delete_content", json={
                "content_type": "project",
                "content_name": cls.test_project_copy
            })
            print(f"Deleted project: {cls.test_project_copy}")

            cls.client.post("/tableau/delete_content", json={
                "content_type": "project",
                "content_name": cls.test_project_name
            })
            print(f"Deleted project: {cls.test_project_name}")
        except Exception as e:
            print(f"Error deleting workbook: {e}")

        # Note: The API doesn't have a delete_project endpoint; in-memory state resets per test

    def test_create_project(self):
        """Test creating a project via the API."""
        self.test_project_name = f"TempProject_{int(time.time()) + 1}"
        response = self.client.post("/tableau/create_project", json={
            "project_name": self.test_project_name,
            "description": "Temporary project for create test"
        })
        
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully created project", response.json().get("message"))

    def test_create_workbook(self):
        """Test creating a workbook via the API."""
        response = self.client.post("/tableau/create_workbook", json={
            "workbook_name": self.test_workbook_name,
            "target_project": self.test_project_name,
            "source_project": self.source_project_name
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully created workbook", response.json().get("message"))

    def test_move_content(self):
        """Test moving a workbook between projects."""   
        self.test_project_copy = self.test_project_name
        self.test_create_project()

        response = self.client.post("/tableau/move_content", json={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "source_project": self.test_project_copy,
            "new_project": self.test_project_name
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully moved workbook", response.json().get("message"))

    def test_update_ownership(self):
        """Test updating workbook ownership."""
        owner_id = "tej.gangineni@gmail.com"
        new_owner_id = "nitheeshkumargorla111@gmail.com"
        response = self.client.post("/tableau/update_ownership", json={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "current_owner": owner_id,
            "new_owner": new_owner_id,
            "project_name": self.test_project_name
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully updated ownership", response.json().get("message"))

    def test_download_content(self):
        """Test downloading a workbook."""
        response = self.client.post("/tableau/download", json={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "project_name": self.test_project_name,
            "format_type": "pdf"
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully downloaded", response.json().get("message"))
        self.assertIn("download_path", response.json())
        download_path = response.json().get("download_path")
        self.assertTrue(os.path.exists(download_path), f"Downloaded file {download_path} does not exist")


    def test_delete_content(self):
        """Test deleting a workbook."""
        response = self.client.post("/tableau/delete_content", json={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "project_name": self.test_project_name
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully deleted workbook", response.json().get("message"))

if __name__ == "__main__":
    unittest.main(verbosity=2)

'''


import unittest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import time
from main import app

class TestCustomApiIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test client and resources before each test."""
        cls.client = TestClient(app)
        
        # Define unique resource name using timestamp to avoid conflicts
        cls.test_project_name = f"TempProject_{int(time.time())}"
        cls.test_project_copy = f"TempProject_Copy_{int(time.time()) + 1}"

        # Define existing workbook source
        cls.test_workbook_name = "Superstore"
        cls.source_project_name = "Samples"
        
        # Define dummy file path
        cls.dummy_workbook_path = "./test_data/dummy_workbook.twbx"
        
        # Create test_data directory and dummy file
        os.makedirs("test_data", exist_ok=True)
        if not os.path.exists(cls.dummy_workbook_path):
            with open(cls.dummy_workbook_path, "w") as f:
                f.write("<workbook></workbook>")

    @classmethod
    def tearDownClass(cls):
        """Clean up test resources after all tests."""
        print(f"\nCleaning up test resources...")
        try:
            cls.client.post("/tableau/delete_content", json={
                "content_type": "project",
                "content_name": cls.test_project_copy
            })
            print(f"Deleted project: {cls.test_project_copy}")

            cls.client.post("/tableau/delete_content", json={
                "content_type": "project",
                "content_name": cls.test_project_name
            })
            print(f"Deleted project: {cls.test_project_name}")
        except Exception as e:
            print(f"Error deleting project: {e}")

    def test_create_project(self):
        """Test creating a project via the API."""
        response = self.client.post("/tableau/create_project", json={
            "project_name": self.test_project_name,
            "description": "Temporary project for create test"
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully created project", response.json().get("message"))

    def test_create_workbook(self):
        """Test creating a workbook via the API."""
        response = self.client.post("/tableau/create_workbook", json={
            "workbook_name": self.test_workbook_name,
            "target_project": self.test_project_name,
            "source_project": self.source_project_name
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully created workbook", response.json().get("message"))

    def test_move_content(self):
        """Test moving a workbook between projects."""
        # First create destination project
        response = self.client.post("/tableau/create_project", json={
            "project_name": self.test_project_copy,
            "description": "Temporary project for move test"
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post("/tableau/move_content", json={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "source_project": self.test_project_name,
            "new_project": self.test_project_copy
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully moved workbook", response.json().get("message"))

    def test_update_ownership(self):
        """Test updating workbook ownership."""
        owner_id = "tej.gangineni@gmail.com"
        new_owner_id = "nitheeshkumargorla111@gmail.com"
        response = self.client.post("/tableau/update_ownership", json={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "current_owner": owner_id,
            "new_owner": new_owner_id,
            "project_name": self.test_project_copy  # updated to reflect current location
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully updated ownership", response.json().get("message"))

    def test_download_content(self):
        """Test downloading a workbook."""
        response = self.client.post("/tableau/download_content", params={
            "content_type": "workbook",
            "project_name": self.test_project_copy,
            "workbook_name": self.test_workbook_name,
            "format": "pdf"
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully downloaded", response.json().get("message"))
        self.assertIn("download_path", response.json())
        download_path = response.json().get("download_path")
        self.assertTrue(os.path.exists(download_path), f"Downloaded file {download_path} does not exist")

    def test_delete_content(self):
        """Test deleting a workbook."""
        response = self.client.post("/tableau/delete_content", params={
            "content_type": "workbook",
            "content_name": self.test_workbook_name,
            "project_name": self.test_project_copy
        })
        self.assertEqual(response.status_code, 200, f"Response: {response.text}")
        self.assertTrue(response.json().get("success"), "Expected success: True")
        self.assertIn("Successfully deleted workbook", response.json().get("message"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
