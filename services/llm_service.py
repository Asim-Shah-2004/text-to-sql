from config.llm_config import MODEL,TEMPERATURE
from langchain_openai import ChatOpenAI

def get_llm():
    return ChatOpenAI(model=MODEL,temperature=TEMPERATURE)

