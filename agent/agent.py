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
# @tool
# def get_weather_data(city: str) -> dict:
#     """Get current weather data for a given city."""
#     # Random weather data for testing
#     temperatures = [18, 22, 15, 28, 12, 35, 8, 25, 30, 5]
#     descriptions = ["sunny", "cloudy", "rainy", "partly cloudy", "stormy", "foggy", "snowy", "windy"]
    
#     return {
#         "city": city,
#         "temperature": random.choice(temperatures),
#         "description": random.choice(descriptions),
#         "humidity": random.randint(30, 90),
#         "wind_speed": round(random.uniform(0, 25), 1)
#     }

@tool
def diagnose_patient(symptoms: str) -> str:
    """Returns a possible diagnosis based on symptoms."""
    return "cancer"

# @tool
# def output_weather_report(report: str) -> str:
#     """Output the final weather report."""
#     print(f"\n=== WEATHER REPORT ===")
#     print(report)
#     print("=" * 25)
#     return f"Report outputted: {report}"

@tool
def output_diagnosis(diagnosis: str) -> str:
    """Output the final diagnosis."""
    print(f"\n=== DIAGNOSIS REPORT ===")
    print(diagnosis)
    print("=" * 25)
    return f"Diagnosis outputted: {diagnosis}"

llm = init_chat_model("google_genai:gemini-2.0-flash")

# tools = [get_weather_data, output_weather_report]
tools = [diagnose_patient, output_diagnosis]
llm_with_tools = llm.bind_tools(tools)

def should_continue(state: State):
    """Decide whether the agent should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the last message has tool calls, continue to tools
    if last_message.tool_calls:
        return "tools"
    # If we've called the output tool, we're done
    if any("DIAGNOSIS REPORT" in str(msg) for msg in messages[-3:]):
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

def get_patient_history(patient_id: str) -> str:
    import requests
    url = 'https://jzyhllxxkkwfryebzvdn.supabase.co/functions/v1/get_record_test'
    headers = {
        'Authorization': 'Bearer sb_publishable_XLSGi6ODTjNGv09KuveIAw_f8AED19R',
        'apikey': 'sb_publishable_XLSGi6ODTjNGv09KuveIAw_f8AED19R',
        'Content-Type': 'application/json'
    }
    data = {
        "patient_id": "6f5ace3b-fc16-4a32-9b35-1b936af758eb",
    }
    response = requests.post(url, headers=headers, json=data)
    # Check if request was successful
    response.raise_for_status()
    # Get response data
    result = response.json()
    return result

# THIS IS THE ENTRY POINT
def process_patient_data(patient_id: str):
    patient_history = get_patient_history(patient_id)
    initial_message = HumanMessage(
        content=f"You are a doctor's assistant."
                f"Research the historical medical records for patient ID {patient_id} and help the doctor."
                f"The following is the patient's medical history: {patient_history}"
                f"You have access to tools to get historical patient records and help you with the diagnosis process."
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


# def process_city_weather(city_name: str):
#     """Process weather research for a single city input - agent decides how."""
#     print(f"Agent starting weather research for: {city_name}")
    
#     # Give the agent a clear instruction but let it decide how to accomplish it
#     initial_message = HumanMessage(
#         content=f"Research the current weather for {city_name} and provide a comprehensive weather report. "
#                 f"You have access to tools to get weather data and output reports. "
#                 f"Use them as you see fit to complete this task."
#     )
    
#     initial_state = {"messages": [initial_message]}
    
#     for event in graph.stream(initial_state):
#         for node_name, value in event.items():
#             if node_name == "agent":
#                 last_msg = value["messages"][-1]
#                 if hasattr(last_msg, 'content') and last_msg.content:
#                     print(f"Agent thinking: {last_msg.content[:100]}...")
#             elif node_name == "tools":
#                 print("Agent using tools...")

# Example usage
if __name__ == "__main__":
    # city_input = "Tokyo"
    # process_city_weather(city_input)
    process_patient_data("00000000-0000-0000-0000-000000000000")