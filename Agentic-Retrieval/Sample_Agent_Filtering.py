# This code is for a sample agent that can perform filtering for RAG based on 

# Dependencies
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser

# Ollama model name
local_llm = "phi3:latest" # Specify language model here


# LLM
llm = ChatOllama(model=local_llm, format="json", temperature=0)


# Setting up an agent for automated filtering based on document structure:
prompt = PromptTemplate(
    template="""You are a research expert. Given a user query, you identify which document chapters one should search for answers. 
    The following are the document chapters:
    DOCUMENT CHAPTERS: \n\n {chapters} \n\n
    Here is the USER QUERY: {question} \n
    Please return the chapter(s) that you would suggest to search for answers to the user query (could be one or multiple). 
    Provide your response as a JSON with a single key 'Chapters' and no premable or explanation.""",
    input_variables=["question", "chapters"],
)

# Sample inputs: 
Chapters = "Strategic Vision for Open-Source, \nDigital Transformation Needs in the Public Sector, \nAI Applications in the Public Sector"
question = "What are the advantages of open-source in the context of digital transformation?"

# Activating the agent workflow
choose_filters_agent = prompt | llm | JsonOutputParser()

print(choose_filters_agent.invoke({"question": question, "chapters": Chapters}))
