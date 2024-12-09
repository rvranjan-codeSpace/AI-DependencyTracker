# create_jira_issue.py
import requests
from requests.auth import HTTPBasicAuth
import json
import os

class JiraIssueCreator:
    def __init__(self):
        # Initialize JIRA instance URL and authentication
        self.url = os.getenv("JIRA_INSTANCE_URL") + "/rest/api/2/issue"
        self.auth = HTTPBasicAuth(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN"))
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_issue(self, body) -> str:
        """Create a JIRA issue with the given body."""
        payload = json.dumps(body)
        response = requests.post(self.url, data=payload, headers=self.headers, auth=self.auth)
        
        # Print and return the response
        print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        return response.text
