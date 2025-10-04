import streamlit as st
import google.generativeai as genai
import os
from typing import Dict, List, Optional
# Corrected Imports: Use relative paths to access services and utils modules
# from services.weather_service import WeatherService
# from services.nasa_service import NASAService
# from utils.data_utils import get_bengaluru_coordinates

# --- API Configuration & Environment Variables (Gemini API) ---
# It's best practice to set this as an environment variable
# st.secrets is a good alternative in Streamlit
# GEMINI_API_KEY = st.secrets["gemini_api_key"]
GEMINI_API_KEY = "AIzaSyBdmm58juT-4EL5Vc78sXhtqNZ8dsxv8c"

# Configure the genai library with the API key
genai.configure(api_key=GEMINI_API_KEY)

# Use a current and stable model name
GEMINI_MODEL = "gemini-1.5-flash-latest"

# Helper function to call the Gemini API using the genai library
def generate_ai_content(system_prompt: str, user_input: str) -> str:
    """Helper function to call the Gemini API using the genai library."""
    try:
        # Instantiate the GenerativeModel
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Combine the system prompt and user input into a single string
        combined_input = f"{system_prompt}\n\n{user_input}"
        
        # Generate content
        response = model.generate_content(combined_input)
        
        # Return the response text
        if response and response.text:
            return response.text
        else:
            return "AI response text not found."
    
    except Exception as e:
        return f"Sorry, I'm having trouble connecting to the Gemini AI service ({GEMINI_MODEL}). Error details: {str(e)}"

# Main function to create and render the chatbot interface
def create_chatbot(stakeholder: str, env_data: Dict):
    st.header("🤖 Terrabot - AI Climate Assistant")
    st.markdown("*Ask me anything about Bengaluru's climate, air quality, water bodies, and urban environment!*")

    # Stakeholder-specific chatbot context setup
    context_prompts = {
        "Citizens": "You are an environmental AI assistant helping citizens of Bengaluru. Provide clear, actionable advice about air quality, water safety, pollution, and health recommendations. Use simple language and focus on practical solutions.",
        "BBMP (City Planning)": "You are an AI assistant for BBMP city planners in Bengaluru. Provide data-driven insights for urban planning...",
        "BWSSB (Water Board)": "You are an AI assistant for BWSSB water management in Bengaluru...",
        "BESCOM (Electricity)": "You are an AI assistant for BESCOM electricity management in Bengaluru...",
        "Researchers": "You are an AI assistant for environmental researchers studying Bengaluru...",
        "General": "You are a general environmental AI assistant for Bengaluru climate data..."
    }
    context_prompt = context_prompts.get(stakeholder, context_prompts["General"])
    st.info(f"💬 **You are currently in the role of a {stakeholder}**. Ask me a question!")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm Terrabot, your AI climate assistant for Bengaluru. What would you like to know?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about Bengaluru's climate..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing environmental data..."):
                env_context = f"""
                Current Bengaluru Environmental Data:
                - Average Temperature: 32.5°C (above normal by 2.1°C)
                - Air Quality Index: 156 (Unhealthy)
                - Lake Health Index: 6.2/10 (declining)
                """
                full_system_prompt = context_prompt + "\n\n" + env_context
                ai_response = generate_ai_content(full_system_prompt, prompt)
                st.markdown(ai_response)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    with st.expander("📊 Available Environmental Data"):
        st.markdown("""... (markdown content here) ...""")

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
