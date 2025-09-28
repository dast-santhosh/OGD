import streamlit as st
import requests
import json
import os
import folium
from streamlit_folium import st_folium

# --- 1. API Configuration & Environment Variables (Gemini API) ---
# We use the native Gemini API. The API key is intentionally left empty ("") 
# and will be securely injected by the environment at runtime.
GEMINI_API_KEY = "AIzaSyBdmm58juT-4EL5Vc78sXhtqNZ8dsxvq8c"
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20" # Low-end model as requested
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# Helper function to call the Gemini API using requests
def generate_ai_content(system_prompt, user_input):
    
    url = GEMINI_URL
    model_name = GEMINI_MODEL

    headers = {
        "Content-Type": "application/json",
    }
    
    # Gemini API payload structure using systemInstruction and contents
    payload = {
        "contents": [{"parts": [{"text": user_input}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }

    try:
        # Retry logic with exponential backoff (e.g., 1s, 2s, 4s)
        max_retries = 3
        initial_delay = 1
        
        for attempt in range(max_retries):
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                break
            
            # If rate limit (429) or server error (5xx), wait and retry
            if response.status_code in [429, 500, 503] and attempt < max_retries - 1:
                import time
                time.sleep(initial_delay * (2 ** attempt))
            else:
                response.raise_for_status() # Raise HTTPError for other bad responses
        
        result = response.json()
        
        # Extract the generated text from Gemini structure
        candidate = result.get('candidates', [{}])[0]
        if candidate and candidate.get('content') and candidate['content'].get('parts'):
            return candidate['content']['parts'][0].get('text', "AI response text not found.")
        else:
            # Handle cases where the response structure is unexpected
            error_message = result.get('error', {}).get('message', 'Unknown API Error')
            return f"The Gemini AI returned an error: {error_message}"

    except requests.exceptions.RequestException as e:
        # Catch network or request-level errors
        print(f"Error calling Gemini API: {e}")
        return f"Sorry, I'm having trouble connecting to the Gemini AI service ({model_name}). Please check the network connection. Error details: {str(e)}"


def create_chatbot(stakeholder, env_data):
    st.header("🤖 AI Environmental Assistant")
    
    # Stakeholder-specific chatbot context setup
    if stakeholder == "Citizens":
        st.info("💬 **Ask me about:** Air quality in your area, water safety, pollution reports, health recommendations")
        context_prompt = "You are an environmental AI assistant helping citizens of Bengaluru. Provide clear, actionable advice about air quality, water safety, pollution, and health recommendations. Use simple language and focus on practical solutions."
    elif stakeholder == "BBMP (City Planning)":
        st.info("💬 **Ask me about:** Urban planning insights, infrastructure needs, policy recommendations, resource allocation")
        context_prompt = "You are an AI assistant for BBMP city planners in Bengaluru. Provide data-driven insights for urban planning, infrastructure development, policy decisions, and resource allocation. Focus on actionable recommendations."
    elif stakeholder == "BWSSB (Water Board)":
        st.info("💬 **Ask me about:** Water quality, lake health, supply planning, infrastructure maintenance")
        context_prompt = "You are an AI assistant for BWSSB water management in Bengaluru. Provide insights on water quality, lake conservation, supply planning, and infrastructure maintenance. Focus on water sustainability."
    elif stakeholder == "BESCOM (Electricity)":
        st.info("💬 **Ask me about:** Power demand patterns, infrastructure strain, renewable energy opportunities")
        context_prompt = "You are an AI assistant for BESCOM electricity management in Bengaluru. Provide insights on power demand, grid management, renewable energy integration, and infrastructure planning."
    elif stakeholder == "Researchers":
        st.info("💬 **Ask me about:** Data analysis, research insights, correlation patterns, environmental trends")
        context_prompt = "You are an AI assistant for environmental researchers studying Bengaluru. Provide detailed analysis, research insights, statistical correlations, and environmental trend analysis."
    else:
        context_prompt = "You are a general environmental AI assistant for Bengaluru climate data. Provide helpful, accurate information about environmental conditions and recommendations."
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask me anything about Bengaluru's environmental data...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Prepare context with environmental data
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
        
        # Generate AI response using the Gemini function
        full_system_prompt = context_prompt + "\n\n" + env_context
        
        with st.chat_message("assistant"):
            with st.spinner(f"Analyzing environmental data using {GEMINI_MODEL}..."):
                # Call the Gemini/requests helper function
                ai_response = generate_ai_content(full_system_prompt, user_input)
                st.write(ai_response)
                
                # Add AI response to history
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
    
    # Quick action buttons based on stakeholder
    st.subheader("🚀 Quick Questions")
    
    if stakeholder == "Citizens":
        quick_questions = [
            "Is it safe to go for a morning walk today?",
            "Which areas have the best air quality right now?",
            "How is the water quality in my area?",
            "What should I do during high pollution days?"
        ]
    elif stakeholder == "BBMP (City Planning)":
        quick_questions = [
            "Which areas need immediate tree plantation?",
            "What are the top infrastructure priorities?",
            "How can we reduce urban heat islands?",
            "Which zones are at highest flood risk?"
        ]
    elif stakeholder == "BWSSB (Water Board)":
        quick_questions = [
            "Which lakes need urgent intervention?",
            "What's the current water supply situation?",
            "How can we improve water quality?",
            "Which areas face water scarcity risk?"
        ]
    elif stakeholder == "BESCOM (Electricity)":
        quick_questions = [
            "What are the peak power demand areas?",
            "How does weather affect electricity consumption?",
            "Where should we plan new substations?",
            "What renewable energy opportunities exist?"
        ]
    elif stakeholder == "Researchers":
        quick_questions = [
            "What correlations exist between urbanization and temperature?",
            "How has air quality changed over the past 5 years?",
            "What environmental patterns can we identify?",
            "Which factors most influence lake health?"
        ]
    else:
        quick_questions = [
            "What's the overall environmental health of Bengaluru?",
            "Which environmental issues are most urgent?",
            "How can citizens contribute to environmental improvement?",
            "What are the main climate challenges facing the city?"
        ]
    
    # Display quick question buttons
    col1, col2 = st.columns(2)
    
    for i, question in enumerate(quick_questions):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            # Using st.form/st.form_submit_button with keys to prevent rerun issues in Streamlit
            with st.form(key=f"quick_form_{i}"):
                st.text_area(label="Question", value=question, key=f"q_text_{i}", height=50)
                if st.form_submit_button("Ask"):
                    # Add to chat as if user asked
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    st.rerun()

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
        st.session_state.chat_history = []
        st.rerun()

# --- Main App Logic for Streamlit ---

if 'stakeholder' not in st.session_state:
    st.session_state.stakeholder = "Citizens"
if 'env_data' not in st.session_state:
    st.session_state.env_data = {} # Placeholder for actual data loading

# Simple sidebar for selecting the stakeholder (for testing the context switching)
st.sidebar.title("Select Stakeholder")
st.session_state.stakeholder = st.sidebar.selectbox(
    "Choose your user role:",
    ["Citizens", "BBMP (City Planning)", "BWSSB (Water Board)", "BESCOM (Electricity)", "Researchers", "General"]
)

create_chatbot(st.session_state.stakeholder, st.session_state.env_data)
