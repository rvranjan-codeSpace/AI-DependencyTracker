from langchain.pydantic_v1 import BaseModel, Field, validator
from typing import List, Optional
from langchain.tools import tool
from jiraAPIKit.create_jira_issue import JiraIssueCreator
import json
import constants.constants as cons
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from stateGraph.state import AgentState
from langchain.schema import (AIMessage,FunctionMessage)
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


JQL_tool = "JQL_Creation_tool"


class JQL(BaseModel):
    user_input: str = Field(
        description="This is the Human message or user input that will be used along with project_id, userStory_id and testCase_id to create a JQL querry"
    )

    project_id: str = Field(
        description="This is the project ID for which dependendent user stories or dependent test cases in the entire Project needs to be searched"
    )

    userStory_id: Optional[str] = Field(
        description="This is the User story ID if the dependency needs to be searched only for individual User story"
    )

    testCase_id: Optional[str] = Field(
        description="This is the Test case ID if the dependent test case needs to be searched only for individual Test cases"
    )

    epic_id: Optional[str] = Field(
        description="This is the Epic ID if the dependent test case needs to be searched only for particular Epic"
    )


@tool(JQL_tool, args_schema=JQL)
def createJQLs(
    user_input: str,
    project_id: str,
    userStory_id: Optional[str] = None,
    testCase_id: Optional[str] = None,
    epic_id: Optional[str]=None
) -> str:
    """Use this Tool 
    -to convert a normal human conversation about JIRA requirement for project, User stories and test cases to conver to JIRA
    - to write Jira Query Langauage(JQL)
    """
      # Define the input variables for the prompt
    if userStory_id is None:
        userStory_id= "NA"
    if testCase_id is None:
        testCase_id = "NA"
    if epic_id is None:
        epic_id = "NA"

    inputs = {
        "user_input": user_input,
        "project_id": project_id,
        "userStory_id": userStory_id,
        "testcase_id": testCase_id,
        "epic_id": epic_id
    }
 
    prompt = getJQLPromptRefined()
    time.sleep(1) 
    chain = prompt | cons.getModel()
    
    resp:AIMessage = chain.invoke(inputs)
    time.sleep(1)
    print("Normal JQL Resp=",resp.content.strip())
    return resp

def getJQLPrompt():
    prompt = ChatPromptTemplate.from_messages(
           [
            (
                "system",
                """
                You are an expert in writing JIRA JQL queries. The user will describe their requirement in English using the variables 
                'user_input', 'project_id', 'userStory_id', 'testcase_id', and 'epic_id'. 
                Based on the inputs provided, generate the corresponding JQL query. The output **must strictly follow** these rules:

                1. If `project_id` is available and 'userStory_id is NA or None', 'testcase_id is NA or Nne', and 'epic_id' is `NA or None'
                   AI Output: project = "{project_id}" 

                2. If `epic_id` is available, and `userStory_id`, `testcase_id`, and `project_id` are `NA` or `None`:
                   AI Output: 'parent = "{epic_id}" AND issuetype = Story

                3. If `epic_id` is available, and `userStory_id`, `testcase_id`, and `project_id` are `NA` or `None`:
                   AI Output: 'parent' = "{epic_id}" AND issuetype = Test

                4. If `userStory_id` is available and 'issuetype' is Test, return:
                   AI Output: issue in linkedIssues('{userStory_id}') AND issuetype = Test

                Ensure that outputs are always valid JQL queries and adapt **strictly** to the user’s specific input. **Do not add extra conditions** unless explicitly mentioned in the user's input.
                """
            ),
            (
                "human",
                """
                User input: {user_input}
                Project ID: {project_id}
                User Story ID: {userStory_id}
                Test Case ID: {testcase_id}
                Epic ID: {epic_id}
                """
            )
        ]
    )
  
    return prompt

def getJQLPromptRefined():
      prompt = ChatPromptTemplate.from_messages(
           [
            (
                "system",
                """
                ### Generate the correct JQL query for a iven user inout. The JQL will depend mainly for 4 user 
                inputs : {project_id},{userStory_id},{testcase_id} and {epic_id}. Do not use this input if they are 'NA'.
                user_input might be - Create a mindmap 
                                    - Create a JQL
                                    - Create a flowchart
                                    - Create a dependency graph.
                All the above implies to create a JQL

                Rules:
                If {project_id} is 'NA' , do no include {project_id}  in JQL
                If {userStory_id} is 'NA' , do no include issuetype story in JQL
                If {testcase_id} is 'NA' , do no include issuetype test in JQL
                If {epic_id} is 'NA' , do no include parent in JQL
                epic_id refers to parent e.g : All issue under epic "VAN" means parent="VAN"

                ### Gold Examples of frequently used JQL you can refer while creating JQL
                - Question: Create a mindmap for all issues assgined to me or current user
                - Gold JQL : assignee = 'currentUser()'
                - Question: Create a mindmap for user story key ABC
                - Gold JQL : project = "{project_id}" AND issueType IN (story)
                - Question: Create a dependency tree for story key ABC
                - Gold JQL : project = "{project_id}" AND issueType IN (story)
                - Question: Create a mindmap or Create a JQL of issues that were reported to me and issue type is Story or issue type is Test
                - Gold JQL : project = 'currentUser() AND issuetype IN (Story, Test)'
                - Question: Create a mindmap for project ABC of type Story
                - Gold JQL : project = "ABC"
                - Question: Create a mindmap or Create a JQL for project BGRFG and issuetype is Story 
                - Gold JQL : project = "{project_id}" AND issueType='story'
                - Question: Create a mindmap or Create a JQL for project ABC and issuetype is Story and issue type is test 
                - Gold JQL : project = "{project_id}" AND issueType IN (story,test)'
                - Question: Create a mindmap  for all issues whose status is in progess or to do"
                - Gold JQL : status In ("In Progress", "To Do")
                - Question: Create a mindmap or JQL for project{project_id} for all issues whcih has not been assigned or whose assigness ine empty
                - Gold JQL : assignee is empty ANF project IN(ABC)
                - Question: Create a mind map or under epic XSP-3 and XSP-8 of issue type story, test or bug
                - Gold JQL : parent In (XSP-3, XSP-8) and type In (story, test, bug)
                - Question: Find all issues under epic XSP-3 of issue type story
                - Gold JQL : parent In (XSP-3) and type In (story)
                - Question: Find the issue with with a link type of "duplicates" in project ABC
                - Gold JQL :issueLinkType in (duplicates,clones)AND project='ABC'
                - Question: Find the issue that are blocked by other issues, or that don't have any blockers:
                - Gold JQL: issueLinkType = "is blocked by"
                - Question: Find the issue that are blocked by other issues in the epic (or under the epic) XSP-3 and XSP-8
                - Gold JQL: parent In (XSP-3, XSP-8) and issueLinkType = "is blocked by"
                - Question: Find the issue that are blocked by other issues in the project(or under the project ARMY and KJL
                - Gold JQL :project IN (XSP, ARMY) and issueLinkType = "is blocked by"

                Your thought : Did it match one of the Gold Examples above ?
                Yes : Construct the JQL referring to example
                Your thought: if {project_id} is 'NA' , did you exclude it from JQL ? If no , Please contruct JQL and exclude {project_id}
                Your thought:if {epic_id} is 'NA' , did you exclude it from JQL ? If no , Please contruct JQL and exclude {epic_id}
                Your thought:if {testcase_id} is 'NA' , did you exclude it from JQL ? If no , Please contruct JQL and exclude {testcase_id}
                Your thought:if {userStory_id} is 'NA' , did you exclude it from JQL ? If no , Please contruct JQL and exclude {userStory_id}

                Your thought : Did you replace the {project_id}, {epic_id},{testcase_id} and {userStory_id} with actual values as provided by the user query.
                Stricly Please dont provide JQL with "project=your project id" and "parent=parent_id". It has to be a validd values so that JQL is executable
            
            
                ### Your answer:
                your answer has to be direclty fed to JQL engine. So it should be executable JQL. Dont add any comments or explantion in your answer.

                """
            ),
            (
                "human",
                """
                User input: {user_input}
                Project ID: {project_id}
                User Story ID: {userStory_id}
                Test Case ID: {testcase_id}
                Epic ID: {epic_id}
                """
            )
        ]
    )
      return prompt



def JQLCreator_node(state: AgentState):
    tools = [createJQLs]
    message = state["messages"]
    last_message = message[-1]
    tool_executor = ToolExecutor(tools=tools)
    some = last_message.additional_kwargs["tool_calls"][-1]["function"]["name"]
    tool_input:dict=json.loads(last_message.additional_kwargs["tool_calls"][-1]["function"]["arguments"])
    action = ToolInvocation(tool=JQL_tool, tool_input=tool_input)
    response = tool_executor.invoke(action)
    if isinstance(response,AIMessage):
        return {"messages": [response]}
