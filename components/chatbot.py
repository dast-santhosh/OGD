import streamlit as st
import json
import os
from openai import OpenAI

def create_chatbot(stakeholder, env_data):
    st.header("🤖 AI Environmental Assistant")
    
    # Initialize OpenRouter client
    OPENROUTER_API_KEY = "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"
    openai_client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Stakeholder-specific chatbot context
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
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
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
        
        # Generate AI response
        try:
            with st.chat_message("assistant"):
                with st.spinner("Analyzing environmental data..."):
                    response = openai_client.chat.completions.create(
                        model="openai/gpt-oss-120b:free",
                        messages=[
                            {"role": "system", "content": context_prompt + "\n\n" + env_context},
                            {"role": "user", "content": user_input}
                        ]
                    )
                    
                    ai_response = response.choices[0].message.content
                    st.write(ai_response)
                    
                    # Add AI response to history
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        except Exception as e:
            st.error(f"Sorry, I'm having trouble connecting to the AI service. Please try again later. Error: {str(e)}")
    
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
            if st.button(question, key=f"quick_q_{i}"):
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
