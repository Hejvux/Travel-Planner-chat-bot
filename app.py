import streamlit as st
from typing import Dict, List
import json
import requests

# Initialize API settings
API_KEY = "sk-C5N6CX8Bvif3Uki6bRGu6g"
API_BASE = "https://aiportalapi.stu-platform.live/jpe"

def make_openai_request(endpoint: str, payload: dict) -> dict:
    """Make a request to the OpenAI API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{API_BASE}/{endpoint}",
        headers=headers,
        json=payload
    )
    return response.json()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def load_conversation_history() -> List[Dict]:
    """Load conversation history from session state"""
    return st.session_state.messages

def save_conversation_history(messages: List[Dict]):
    """Save conversation history to session state"""
    st.session_state.messages = messages

def get_travel_requirements(user_input: str) -> Dict:
    """Extract travel requirements using function calling"""
    functions = [
        {
            "name": "extract_travel_info",
            "description": "Extract travel information from user input",
            "parameters": {
                "type": "object",
                "properties": {
                    "time": {
                        "type": "string",
                        "description": "When the trip is planned for"
                    },
                    "location": {
                        "type": "string",
                        "description": "Destination location"
                    },
                    "duration": {
                        "type": "string",
                        "description": "Duration of the trip"
                    },
                    "budget": {
                        "type": "string",
                        "description": "Budget for the trip"
                    },
                    "preferences": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Any specific preferences or requirements"
                    }
                }
            }
        }
    ]

    # Get conversation history for context
    history = load_conversation_history()
    
    # Batch the function calling request with context
    messages = []
    # Add last 5 messages for context if they exist
    if history:
        messages.extend(history[-5:])
    # Add current user input
    messages.append({"role": "user", "content": user_input})
    
    payload = {
        "model": "GPT-4o-mini",
        "messages": messages,
        "functions": functions,
        "function_call": {"name": "extract_travel_info"}
    }
    
    response = make_openai_request("chat/completions", payload)
    
    # Extract the function call result
    if response.get("choices") and response["choices"][0].get("message", {}).get("function_call"):
        function_call = response["choices"][0]["message"]["function_call"]
        return json.loads(function_call["arguments"])
    return {}

def generate_travel_plan(requirements: Dict) -> str:
    """Generate a detailed travel plan based on requirements"""
    # Create a context-aware prompt
    prompt = f"""As a travel planning assistant, create a detailed plan based on these requirements:
    Time: {requirements.get('time', 'Not specified')}
    Location: {requirements.get('location', 'Not specified')}
    Duration: {requirements.get('duration', 'Not specified')}
    Budget: {requirements.get('budget', 'Not specified')}
    Preferences: {', '.join(requirements.get('preferences', ['Not specified']))}

    Please provide a detailed day-by-day itinerary including:
    1. Accommodation recommendations
    2. Activities and attractions
    3. Transportation options
    4. Estimated costs
    5. Local tips and recommendations
    """

    # Get conversation history for context
    history = load_conversation_history()
    
    # Prepare messages with context
    messages = []
    # Add last 5 messages for context if they exist
    if history:
        messages.extend(history[-5:])
    # Add current request
    messages.append({"role": "user", "content": prompt})
    
    # Generate response with context
    payload = {
        "model": "GPT-4o-mini",
        "messages": messages
    }
    
    response = make_openai_request("chat/completions", payload)
    
    if response.get("choices"):
        return response["choices"][0]["message"]["content"]
    return "Sorry, I couldn't generate a travel plan at this moment."

# Streamlit UI
st.title("🌍 AI Travel Planner")

# Chat interface
st.write("Welcome! Let me help you plan your perfect trip. Please provide your travel details, and I'll create a customized plan for you.")

# Display chat history
for message in load_conversation_history():
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("Tell me about your travel plans...")

if user_input:
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Extract travel requirements
    requirements = get_travel_requirements(user_input)
    
    # Generate travel plan
    travel_plan = generate_travel_plan(requirements)
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.write(travel_plan)
    
    # Save to conversation history
    save_conversation_history([
        *load_conversation_history(),
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": travel_plan}
    ])
