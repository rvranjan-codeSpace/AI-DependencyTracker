from langchain_openai import ChatOpenAI
import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from streamlit_mermaid import st_mermaid
import requests

def main():
    st.title("MERMAID DIAGRAM APP")
    st.write("create diagram from any details")
    qsn=st.text_area("ask your question here")
    ts1="""
        Your job is to write the code to generate a colorful Mermaid diagram .
        Describe all the issues and their relationships as indicated in {steps}. Do not include any other information or explanations.
        Stritcly Avoid HTML tag. No <br> tags should be present. Use plain text only and ensure the output is valid Mermaid syntax.
        Each issue and all relationships should be clearly defined. Each line in the code must be properly terminated by a semicolon without any trailing spaces.
        Do not add any extra text after the Mermaid code.
"""

    pt=ChatPromptTemplate.from_template(ts)
    llm=ChatOpenAI(model="gpt-4-turbo",temperature=0.0)
    qa_chain=LLMChain(llm=llm,prompt=pt)
    if qsn is not None:
        btn=st.button("submit")
        if btn:
            response = qa_chain.invoke({"steps": qsn})
            data = response["text"]
            data = data.replace("`", "").replace("mermaid", "")
            data = data.replace("graph TD;", "", 1).strip()
            
            # Add the Mermaid header to the response and clean up formatting
            if not data.startswith("graph TD;"):
                mermaid_code = f"graph TD;\n{data}".strip()
            else:
                mermaid_code = data.strip()
           
            st.write("Mermaid code generated:\n")
            st.text(mermaid_code)

        # Generate and save the Mermaid diagram as PNG
            generate_mermaid_diagram(mermaid_code, "diagram.png")
def generate_mermaid_diagram(data: str, filename: str):
    # Call Kroki API to generate the diagram
    url = "https://kroki.io/mermaid/png"
    print("\n***********************************\n")
    print(data.encode("utf-8"))
    response = requests.post(url, data=data.encode("utf-8"))    
    if response.status_code == 200:
        # Save the image
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Diagram saved as {filename}")
    else:
        print("Failed to generate diagram:", response.content)
        


if __name__ == "__main__":
    main()