"""
User Clarification and Research Brief Generation

This module implements the scoping phase of the research workflow, where we:
1. Assess if the user's request needs clarification
2. Generate a detailed research brief from the conversation

The workflow uses structured output to make deterministic decisions about
whether sufficient context exists to proceed with research.
"""

from datetime import datetime
from typing_extensions import Literal
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from langchain_core.messages import HumanMessage, get_buffer_string, AIMessage
from langgraph.graph import START, END, StateGraph

from prompts import clarify_with_user_instructions, transform_messages_into_research_topic_prompt
from state_scope import AgentState, ClarifyWithUser, ResearchQuestion, AgentInputState

# ===== UTILITY FUNCTIONS =====

def get_today_str() -> str:
    """Get current date in a human readable format."""
    return datetime.now().strftime("%a %b %-d, %Y")

# ===== CONFIGURATION =====

# Initialize model
model = init_chat_model(model="openai:gpt-4.1-mini", temperature=0.0)

# ===== WORKFLOW NODES =====
def clarify_with_user(state: AgentState) -> Command[Literal["write_research_brief", "__end__"]]:
    """
    Clarification decision node.
    
    Determine if the user's request contains sufficient information to proceed
    with research or if additional clarification is needed.
    
    Users structured output to make deterministric decisions and avoid hallucination.
    Routes to either research brief generation or ends with a clarification question.
    """
    
    # Set up structured output model
    structured_output_model = model.with_structured_output(ClarifyWithUser)
    
    # Use .get to avoid KeyError if messages are not present in the state
    response = structured_output_model.invoke([
        HumanMessage(content=clarify_with_user_instructions.format(
            messages=get_buffer_string(messages=state.get("messages", [])),
            date=get_today_str()
        ))
    ])
    
    if response.need_clarification:
        return Command(
            goto=END,
            update={"messages": [AIMessage(content=response.question)]}
        )
    else:
        return Command(
            goto="write_research_brief",
            update={"messages": [AIMessage(content=response.verification)]}
        )
        
def write_research_brief(state: AgentState):
    """
    Research brief generation node.
    
    Transforms the conversation history into a comprehensive research brief
    that will guide the subsequent research phase.
    
    Uses structured output to ensure the brief follows the required format
    and contains all necessary details for effective research.
    """
    
    structured_output_model = model.with_structured_output(ResearchQuestion)

    # Generate research brief from conversation history
    response = structured_output_model.invoke([
        HumanMessage(content=transform_messages_into_research_topic_prompt.format(
            messages=get_buffer_string(state.get("messages", [])),
            date=get_today_str()
        ))
    ])
    
    # Update state with generated research brief and pass it to the supervisor
    return {
        "research_brief": response.research_brief,
        "supervisor_messages": [HumanMessage(content=f"{response.research_brief}.")]
    }
    
# ===== GRAPH CONSTRUCTION =====

# Build the scoping workflow
deep_research_builder = StateGraph(AgentState, input_schema=AgentInputState)

# Add workflow nodes
deep_research_builder.add_node("clarify_with_user", clarify_with_user)
deep_research_builder.add_node("write_research_brief", write_research_brief)

# Add workflow edges
deep_research_builder.add_edge(START, "clarify_with_user")
deep_research_builder.add_edge("write_research_brief", END)

# scope_research = deep_research_builder.compile()

