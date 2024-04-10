from services.sql_service import get_sql_database
from services.llm_service import get_llm
from services.memory_service import get_memory
from controllers.prompt_chunking import get_full_chucked_prompt
from langchain_community.agent_toolkits import create_sql_agent

def get_agent_executor():
    full_prompt = get_full_chucked_prompt()
    llm = get_llm()
    memory = get_memory()
    db = get_sql_database()                              

    return create_sql_agent(
        llm=llm,
        db=db,
        prompt=full_prompt,
        verbose=True,
        agent_type="openai-tools",
        agent_executor_kwargs={
            "memory": memory
        }
    )
