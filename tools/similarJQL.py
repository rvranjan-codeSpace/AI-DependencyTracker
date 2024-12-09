import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
import constants.constants as cons



# Define response schemas to parse top three similar matches
response_schemas = [
    ResponseSchema(name="most_similar_question_1", description="First most similar question and its Gold JQL"),
    ResponseSchema(name="most_similar_question_2", description="Second most similar question and its Gold JQL"),
    ResponseSchema(name="most_similar_question_3", description="Third most similar question and its Gold JQL")
]

# Define output parser
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# Define example JQLs in text format
example_jql_text = """
Question: Create a mindmap for issues in project ABC with link type "duplicates"
Gold JQL: issueLinkType = "duplicates" AND project = "ABC"

Question: Create a mindmap for issues that are blocked by other issues
Gold JQL: issueLinkType = "is blocked by"

Question: Create a mindmap for To obtain the list of issues linked to a XSP-58
Gold JQL: issue in linkedIssues(XSP-58)

Question: Create a mindmap for all issues (tests, user stories, bug) that blocks issue ABC
Gold JQL: issue in linkedIssues(ABC, "is blocked by") AND issuetype IN( Story, Test, Bug)

Question: Create a mindmap for only and only user stories blocked by issue(tests, userstory, bug) ABC
Gold JQL: issue in linkedIssues(ABC, "is blocked by") AND issuetype IN( Story)
"""

# Define prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in identifying similar JQL queries based on provided examples."),
    ("system", f"Here are some example JQL queries for reference:\n{example_jql_text}"),
    ("user", "Given the examples, find the top 3 most similar JQL queries for the following user query:\n\nUser Query: {user_query}"),
    ("user", "{format_instructions}")
])

# Format instructions for output parser
format_instructions = output_parser.get_format_instructions()

# Define user query
user_query = "create the mind map for all issues blocked by XSP-61"

# Format the prompt with user query and instructions for parsing
formatted_prompt = prompt.format_messages(
    user_query=user_query,
    format_instructions=format_instructions
)

# This formatted prompt can now be used with an LLM to get the structured response
# response = llm(formatted_prompt, output_parser=output_parser)


if __name__ == "__main__":
    llm = cons.getModel()
    
    print(formatted_prompt)
    response = llm(formatted_prompt,    )
    print(response)
