from dash_extensions import Mermaid
from langchain.prompts import ChatPromptTemplate
from MARCOS.llmmodel.modelFactory import Model
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'MACROS')))
 
model = Model(ai_type="openai", model_name="gpt-4o-mini", temperature=0.5)
llm = model.getModel()
 
# Hardcoded steps for the Mermaid diagram
hardcoded_steps = """
Issue ID: ARMY-5
Summary: Fifth Assignment
Status: To Do
Linked Issues:
ARMY-5 BLOCKS ARMY-1
Summary: First assignment
Status: To Do
----------------------------------------
Issue ID: ARMY-4
Summary: Fourth Assignment
Status: To Do
Linked Issues:
----------------------------------------
Issue ID: ARMY-3
Summary: Third Assignment
Status: To Do
Linked Issues:
ARMY-3 BLOCKS ARMY-1
Summary: First assignment
Status: To Do
----------------------------------------
Issue ID: ARMY-2
Summary: Second Assignment
Status: To Do
Linked Issues:
ARMY-2 BLOCKS ARMY-5
Summary: Fifth Assignment
Status: To Do
----------------------------------------
Issue ID: ARMY-1
Summary: First Assignment
Status: To Do
Linked Issues:
ARMY-1 BLOCKS ARMY-2
Summary: Second Assignment
Status: To Do
ARMY-1 BLOCKS ARMY-4
Summary: Fourth Assignment
Status: To Do
"""
 
# Mermaid diagram generation function
def generate_mermaid_diagram(steps):
    ts = """
    Your job is to write the code to generate a colorful mermaid diagram
    describing the below
    {steps} information only, don't use any other information.
    Only generate the code as output, nothing extra.
    Each line in the code must be terminated by a semicolon.
    Code:
    """
    pt = ChatPromptTemplate.from_template(ts)
    qa_chain = pt | llm
    response = qa_chain.invoke({"steps": steps})
    data = response.content
    data = data.replace("`", "").replace("mermaid", "")
    return data
 
 
 