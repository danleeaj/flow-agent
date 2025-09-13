from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
import os
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
import random

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Define tools that the agent can choose to use
@tool
def get_weather_data(city: str) -> dict:
    """Get current weather data for a given city."""
    # Random weather data for testing
    temperatures = [18, 22, 15, 28, 12, 35, 8, 25, 30, 5]
    descriptions = ["sunny", "cloudy", "rainy", "partly cloudy", "stormy", "foggy", "snowy", "windy"]
    
    return {
        "city": city,
        "temperature": random.choice(temperatures),
        "description": random.choice(descriptions),
        "humidity": random.randint(30, 90),
        "wind_speed": round(random.uniform(0, 25), 1)
    }

@tool
def output_weather_report(report: str) -> str:
    """Output the final weather report."""
    print(f"\n=== WEATHER REPORT ===")
    print(report)
    print("=" * 25)
    return f"Report outputted: {report}"

# Initialize LLM and tools
# os.environ["GOOGLE_API_KEY"] = "AIzaSyC5d6eNtQBxJJmato3FK3l7xnpRmREZCM4"
llm = init_chat_model("google_genai:gemini-2.0-flash")

tools = [get_weather_data, output_weather_report]
llm_with_tools = llm.bind_tools(tools)

def should_continue(state: State):
    """Decide whether the agent should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the last message has tool calls, continue to tools
    if last_message.tool_calls:
        return "tools"
    # If we've called the output tool, we're done
    if any("output_weather_report" in str(msg) for msg in messages[-3:]):
        return "end"
    # Otherwise, continue with the agent
    return "agent"

def call_model(state: State):
    """Let the agent decide what to do next."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Create the graph
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("agent", call_model)
graph_builder.add_node("tools", ToolNode(tools))

# Define the flow with conditional logic
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END,
        "agent": "agent"
    }
)
graph_builder.add_edge("tools", "agent")

graph = graph_builder.compile()

def process_city_weather(city_name: str):
    """Process weather research for a single city input - agent decides how."""
    print(f"Agent starting weather research for: {city_name}")
    
    # Give the agent a clear instruction but let it decide how to accomplish it
    initial_message = HumanMessage(
        content=f"Research the current weather for {city_name} and provide a comprehensive weather report. "
                f"You have access to tools to get weather data and output reports. "
                f"Use them as you see fit to complete this task."
    )
    
    initial_state = {"messages": [initial_message]}
    
    for event in graph.stream(initial_state):
        for node_name, value in event.items():
            if node_name == "agent":
                last_msg = value["messages"][-1]
                if hasattr(last_msg, 'content') and last_msg.content:
                    print(f"Agent thinking: {last_msg.content[:100]}...")
            elif node_name == "tools":
                print("Agent using tools...")

# Example usage
if __name__ == "__main__":
    city_input = "Tokyo"
    process_city_weather(city_input)