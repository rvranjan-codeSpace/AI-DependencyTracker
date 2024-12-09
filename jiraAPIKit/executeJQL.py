# create_jira_issue.py
import requests
from requests.auth import HTTPBasicAuth
import json
import os

class JQLExecutor:
    def __init__(self):
        # Initialize JIRA instance URL and authentication
        self.url = os.getenv("JIRA_INSTANCE_URL") + "/rest/api/3/search"
        self.auth = HTTPBasicAuth(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN"))
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def execute_JQL(self, JQL) -> str:
        """Execute the JIRA JQL and fetch the dependent issues for particular JQL """
        formatted_url= self.url

        payload = json.dumps( {
            "expand": [
                    "names",
                "schema",
                "operations"
            ],
        "fields": [
             "*all"
        ],
        "jql": JQL.strip(),
        "startAt": 0
        } )
        print("JQL Query is:",JQL)
        response = requests.request("POST",self.url,data=payload,headers=self.headers,auth=self.auth)
        formatted_response:dict = massageResponse(response.json())
        return formatted_response
    

def massageResponse(response_data)->dict:
    output_string = ""
    json_output = []
    if isinstance(response_data, dict) and 'issues' in response_data:
        for issue in response_data['issues']:
            issue_summary={
            "Issue ID":  issue['key'],
            "Summary": issue['fields']['summary'],
            "Status": issue['fields']['status']['name'],
            "Linked Issues": []
            }
            # Accumulate the string output
            output_string += f"Issue ID: {issue['key']}\n"
            output_string += f"Summary: {issue['fields']['summary']}\n"
            output_string += f"Status: {issue['fields']['status']['name']}\n"

            # Use .get() to safely access 'issuelinks', if it doesn't exist, it will return None
            issue_links = issue['fields'].get('issuelinks', [])
            if issue_links: 
                output_string += "Linked Issues:\n"
                for link in issue_links:
                    # Handle outward links
                    if 'outwardIssue' in link:
                        linked_issue = link['outwardIssue']
                        output_string += f" {issue['key']} BLOCKS {linked_issue['key']}\n"
                        output_string += f" Summary: {linked_issue['fields']['summary']}\n"
                        output_string += f" Status: {linked_issue['fields']['status']['name']}\n"
                        # Append to the JSON structure
                        issue_summary["Linked Issues"].append({
                            "Linked Issue ID": linked_issue['key'],
                            "Summary": linked_issue['fields']['summary'],
                            "Status": linked_issue['fields']['status']['name']
                        })
            else:
                
                output_string += "No linked issues.\n"
            output_string += "-" * 40 + "\n"
    else:
        if "errorMessages" in response_data:
            output_string+= response_data["errorMessages"][-1]
        else:
            output_string += "Invalid response:{""response_data""}"
    # Prepare the final output dictionary
    final_output = {
        "normal": output_string,
        "json": json_output
        }
    print(final_output["normal"])
    return final_output


def massageResponseBackup(response_data):
    if isinstance(response_data, dict) and 'issues' in response_data:
        output_string = ""  
        json_output = []
        for issue in response_data['issues']:
            print(f"Issue ID: {issue['key']}")
            print(f"Summary: {issue['fields']['summary']}")
            print(f"Status: {issue['fields']['status']['name']}")
            
            # Use .get() to safely access 'issuelinks', if it doesn't exist, it will return None
            issue_links = issue['fields'].get('issuelinks', [])
            if issue_links: 
                print("Linked Issues:")
                for link in issue_links:
                    # Handle outward links
                    if 'outwardIssue' in link:
                        linked_issue = link['outwardIssue']
                        print(f" {issue['key']} BLOCKS {linked_issue['key']} ")
                        print(f" Summary: {linked_issue['fields']['summary']}")
                        print(f" Status: {linked_issue['fields']['status']['name']}")
            else:
                print("No linked issues.")
            print("-" * 40)
    else:
        print("Invalid response data")