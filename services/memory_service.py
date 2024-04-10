from config.memory_config import INPUT_KEY, OUTPUT_KEY, MEMORY_KEY, RETURN_MESSAGES
from langchain.memory import ConversationBufferMemory

def get_memory():
    return ConversationBufferMemory(
        input_key=INPUT_KEY,output_key=OUTPUT_KEY,memory_key=MEMORY_KEY,return_messages=RETURN_MESSAGES
    )
