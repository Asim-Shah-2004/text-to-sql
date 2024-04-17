from langchain_core.messages import SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from services.system_prefix_service import get_system_prefix
#this is service
def get_full_chucked_prompt():
    system_prefix = get_system_prefix(True)

    system_prompt_chunks = [
        system_prefix[i : i + 4096] for i in range(0, len(system_prefix), 4096)
    ]

    
    system_messages = []
    for chunk in system_prompt_chunks:
        system_messages.append(SystemMessage(content=chunk))

    
    full_prompt = ChatPromptTemplate.from_messages(
        system_messages
        + [
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    
    return full_prompt