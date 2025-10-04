import streamlit as st
import requests
import json
import os
import folium
from streamlit_folium import st_folium
from typing import Dict, List, Optional
from services.gemini_service import GeminiService
from services.weather_service import WeatherService
from services.nasa_service import NASAService
from utils.data_utils import get_bengaluru_coordinates

# --- 1. API Configuration & Environment Variables (Gemini API) ---
GEMINI_API_KEY = "AIzaSyBdmm58juT-4EL5Vc78sXhtqNZ8dsxv8c"
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# Helper function to call the Gemini API using requests
def generate_ai_content(system_prompt: str, user_input: str) -> str:
    """Helper function to call the Gemini API using requests."""
    url = GEMINI_URL
    model_name = GEMINI_MODEL

    headers = {
        "Content-Type": "application/json",
    }
    
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
        print(f"Error calling Gemini API: {e}")
        return f"Sorry, I'm having trouble connecting to the Gemini AI service ({model_name}). Please check the network connection. Error details: {str(e)}"

# Main function to create and render the chatbot interface
def create_chatbot(stakeholder: str, env_data: Dict):
    st.header("🤖 Terrabot - AI Climate Assistant")
    st.markdown("*Ask me anything about Bengaluru's climate, air quality, water bodies, and urban environment!*")

    # Stakeholder-specific chatbot context setup
    context_prompts = {
        "Citizens": "You are an environmental AI assistant helping citizens of Bengaluru. Provide clear, actionable advice about air quality, water safety, pollution, and health recommendations. Use simple language and focus on practical solutions.",
        "BBMP (City Planning)": "You are an AI assistant for BBMP city planners in Bengaluru. Provide data-driven insights for urban planning, infrastructure development, policy decisions, and resource allocation. Focus on actionable recommendations.",
        "BWSSB (Water Board)": "You are an AI assistant for BWSSB water management in Bengaluru. Provide insights on water quality, lake conservation, supply planning, and infrastructure maintenance. Focus on water sustainability.",
        "BESCOM (Electricity)": "You are an AI assistant for BESCOM electricity management in Bengaluru. Provide insights on power demand, grid management, renewable energy integration, and infrastructure planning.",
        "Researchers": "You are an AI assistant for environmental researchers studying Bengaluru. Provide detailed analysis, research insights, statistical correlations, and environmental trend analysis.",
        "General": "You are a general environmental AI assistant for Bengaluru climate data. Provide helpful, accurate information about environmental conditions and recommendations."
    }
    context_prompt = context_prompts.get(stakeholder, context_prompts["General"])
    st.info(f"💬 **You are currently in the role of a {stakeholder}**. Ask me a question!")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm Terrabot, your AI climate assistant for Bengaluru. What would you like to know?"}
        ]
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about Bengaluru's climate..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response with context
        with st.chat_message("assistant"):
            with st.spinner("Analyzing environmental data..."):
                env_context = f"""
                Current Bengaluru Environmental Data:
                - Average Temperature: 32.5°C (above normal by 2.1°C)
                - Air Quality Index: 156 (Unhealthy)
                - Lake Health Index: 6.2/10 (declining)
                - Green Cover: 18.2% (decreased by 1.3%)
                - Major Pollution Sources: Traffic (40%), Industrial (25%), Construction (20%), Domestic (15%)
                - Water Quality Issues: Bellandur Lake (critical), Varthur Lake (poor)
                - High Growth Areas: Yelahanka (18.2%), Bannerghatta (15.7%), Electronic City (12.3%)
                - Flood Risk Areas: Silk Board (Very High), Electronic City (High), Majestic (High)
                """
                full_system_prompt = context_prompt + "\n\n" + env_context
                ai_response = generate_ai_content(full_system_prompt, prompt)
                st.markdown(ai_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # Data insights panel
    with st.expander("📊 Available Environmental Data"):
        st.markdown("""
        **Current Data Sources:**
        - 🛰️ NASA MODIS: Land surface temperature, vegetation indices
        - 🛰️ Landsat: High-resolution land use change
        - 🛰️ VIIRS: Night-time lights for urban growth tracking
        - 🛰️ TROPOMI: Air pollution (NO2, CO, aerosols)
        - 🛰️ GPM: Precipitation and flood risk
        - 🏢 Ground Stations: Real-time air quality, water quality
        - 👥 Citizen Reports: Local environmental observations
        
        **Analysis Capabilities:**
        - Heat island identification and intensity mapping
        - Water body health monitoring and pollution tracking
        - Air quality forecasting and source attribution
        - Urban growth pattern analysis
        - Flood risk assessment and early warning
        - Multi-stakeholder decision support
        """)

    # Clear chat history button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- Main App Logic for Streamlit ---
if 'stakeholder' not in st.session_state:
    st.session_state.stakeholder = "Citizens"
if 'env_data' not in st.session_state:
    st.session_state.env_data = {}

# Simple sidebar for selecting the stakeholder
st.sidebar.title("Select Stakeholder")
st.session_state.stakeholder = st.sidebar.selectbox(
    "Choose your user role:",
    ["Citizens", "BBMP (City Planning)", "BWSSB (Water Board)", "BESCOM (Electricity)", "Researchers", "General"]
)

create_chatbot(st.session_state.stakeholder, st.session_state.env_data)
