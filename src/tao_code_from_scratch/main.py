from dotenv import load_dotenv
load_dotenv()

from langgraph.checkpoint.memory import InMemorySaver
from research_agent_scope import deep_research_builder
from utils import format_messages
from langchain_core.messages import HumanMessage

checkpointer = InMemorySaver()
scope = deep_research_builder.compile(checkpointer=checkpointer)
thread = {"configurable": {"thread_id": 1}}
result = scope.invoke({"messages": [HumanMessage(content="I want to research the best coffee shops in San Francisco")]}, config=thread)
print(format_messages(result["messages"]))