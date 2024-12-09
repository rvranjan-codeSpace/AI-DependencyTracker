from langchain.pydantic_v1 import BaseModel, Field, validator
from typing import List, Optional
from langchain.tools import tool
from jiraAPIKit.create_jira_issue import  JiraIssueCreator
import json

class JIRATicketCreation(BaseModel):      
    project_id: str = Field(
        description="This is the project ID or the project key to create issue or a Ticket for a particular project"
    )
    issue_Type: str = Field(default="Story",
        description="This is the issue type. It can be User Story, task, Bug", enum=["Story","Bug","Test","Task"]
    )
    issue_Summary: Optional[str] = Field(
        description="Free text to describe the title of the issue"
    )
    issue_Desc: Optional[str] = Field(description="Free text to describe more context to the issue")

    @validator("issue_Type")
    def validate_issue_Type(cls, value) -> str:
        if value.upper() not in ["STORY", "BUG", "TASK", "TEST"]:
            raise ValueError("issue type must be of Story, Bug, Test or Task")
        return value

@tool("JiraTicketCreationTool", args_schema=JIRATicketCreation)
def createIssues(    project_id: str, issue_Type: str, issue_Summary: str, issue_Desc: str
) -> str:
    """Use this Tool to create a new the Jira issue"""

    issue_details = {
        "fields":{
        "project": {"key": project_id},
        "description": issue_Desc,
        "summary": issue_Summary,
        "issuetype":{"name":issue_Type}
        }
    }
    temp_issue_detials = json.dumps(issue_details)
    #print(temp_issue_detials)
    resp= JiraIssueCreator().create_issue(issue_details)
    return resp


