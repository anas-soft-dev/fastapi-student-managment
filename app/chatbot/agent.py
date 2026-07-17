from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from app.chatbot.config import model
from app.chatbot.prompt import PROMPT
from app.chatbot.tools import get_tools
import uuid

memory = InMemorySaver()


def build_agent(db):
    print("inside build_agent",db)
    tools = get_tools(db)

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=PROMPT,
        checkpointer = memory
    )

    return agent


def run_agent(db, message: str, conversation_id: str):
    print("inside run_agent",db)
    agent = build_agent(db)
    
    config = {
        "configurable":{
            "thread_id":conversation_id
        }
    }

    result = agent.invoke(
        {
            "messages":[
                {
                    "role":"user",
                    "content": message
                }
            ]
        },
        config=config
    )

    return extract_reply(result)

def extract_reply(result)->str:

    messages = result.get("messages",{})

    if not messages:
        return ""
    
    return getattr(messages[-1],"content", "") or ""