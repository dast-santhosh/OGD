import streamlit as st
import requests
import json
import os
from typing import Dict, List, Optional
# Corrected Imports: Use relative paths to access services and utils modules
from services.weather_service import WeatherService
from services.nasa_service import NASAService
from utils.data_utils import get_bengaluru_coordinates
# --- API Configuration & Environment Variables (Gemini API) ---
# Use a current and stable model name
GEMINI_API_KEY = "AIzaSyBdmm58juT-4EL5Vc78sXhtqNZ8dsxv8c"
GEMINI_MODEL = "gemini-1.5-flash-latest"  # Changed to a current, stable model
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# Helper function to call the Gemini API using requests
def generate_ai_content(system_prompt: str, user_input: str) -> str:
    """Helper function to call the Gemini API using requests."""
    url = GEMINI_URL
    model_name = GEMINI_MODEL
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": user_input}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }

    try:
        max_retries = 3
        initial_delay = 1
        for attempt in range(max_retries):
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                break
            if response.status_code in [429, 500, 503] and attempt < max_retries - 1:
                import time
                time.sleep(initial_delay * (2 ** attempt))
            else:
                response.raise_for_status()
        
        result = response.json()
        candidate = result.get('candidates', [{}])[0]
        if candidate and candidate.get('content') and candidate['content'].get('parts'):
            return candidate['content']['parts'][0].get('text', "AI response text not found.")
        else:
            error_message = result.get('error', {}).get('message', 'Unknown API Error')
            return f"The Gemini AI returned an error: {error_message}"

    except requests.exceptions.RequestException as e:
        return f"Sorry, I'm having trouble connecting to the Gemini AI service ({model_name}). Error details: {str(e)}"

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
