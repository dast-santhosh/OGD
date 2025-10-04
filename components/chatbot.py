import streamlit as st
from typing import Dict, List, Optional
from services.gemini_service import GeminiService
from services.weather_service import WeatherService
from services.nasa_service import NASAService
from utils.data_utils import get_bengaluru_coordinates

def render_chatbot_interface(gemini_service: GeminiService, nasa_service: NASAService, weather_service: WeatherService):
    """Render the Terrabot AI chatbot interface"""
    
    st.header("🤖 Terrabot - AI Climate Assistant")
    st.markdown("*Ask me anything about Bengaluru's climate, air quality, water bodies, and urban environment!*")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm Terrabot, your AI climate assistant for Bengaluru. I can help you with questions about air quality, temperature, water bodies, urban heat islands, and climate data. What would you like to know?"}
        ]
    
    # Sample questions
    with st.expander("💡 Try these sample questions"):
        sample_questions = [
            "What's the current air quality in Whitefield?",
            "Which areas have the worst heat islands in Bengaluru?",
            "How is the health of Bellandur Lake?",
            "What's the weather forecast for tomorrow?",
            "Which parts of the city are best for outdoor activities today?",
            "How much green cover has Bengaluru lost in recent years?",
            "What are the main pollution sources affecting our lakes?",
            "Which areas should avoid outdoor activities due to air quality?"
        ]
        
        for i, question in enumerate(sample_questions):
            if st.button(question, key=f"sample_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                handle_user_query(question, gemini_service, nasa_service, weather_service)
                st.rerun()
    
    # Display chat messages
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
        
        # Handle the query and get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = handle_user_query(prompt, gemini_service, nasa_service, weather_service)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

def handle_user_query(query: str, gemini_service: GeminiService, nasa_service: NASAService, weather_service: WeatherService) -> str:
    """Handle user query and return AI response"""
    
    try:
        # Get current data for context
        lat, lon = get_bengaluru_coordinates()
        
        context_data = {}
        
        # Fetch relevant data based on query keywords
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['weather', 'temperature', 'hot', 'cold', 'humid']):
            weather_data = weather_service.get_current_weather(lat, lon)
            if weather_data:
                context_data['weather'] = weather_data
        
        if any(word in query_lower for word in ['air', 'quality', 'pollution', 'pm2.5', 'pm10']):
            air_quality_data = weather_service.get_air_quality(lat, lon)
            if air_quality_data:
                context_data['air_quality'] = air_quality_data
        
        if any(word in query_lower for word in ['heat', 'island', 'hotspot', 'cooling']):
            heat_data = nasa_service.get_urban_heat_analysis(lat, lon)
            if heat_data:
                context_data['heat_islands'] = heat_data
        
        if any(word in query_lower for word in ['lake', 'water', 'bellandur', 'ulsoor', 'sankey']):
            lakes_data = nasa_service.get_water_body_analysis([
                {"name": "Bellandur Lake", "area": 361},
                {"name": "Ulsoor Lake", "area": 50},
                {"name": "Sankey Tank", "area": 15}
            ])
            if lakes_data:
                context_data['lakes'] = lakes_data
        
        # Generate AI response with context
        response = gemini_service.generate_climate_response(query, context_data)
        
        # Add specific data points if relevant
        response = enhance_response_with_data(response, query_lower, context_data)
        
        return response
        
    except Exception as e:
        return f"I apologize, but I encountered an error while processing your question: {str(e)}. Please try asking something else!"

def enhance_response_with_data(response: str, query_lower: str, context_data: Dict) -> str:
    """Enhance AI response with specific data points"""
    
    enhancements = []
    
    # Add current weather if asked about weather
    if 'weather' in context_data and any(word in query_lower for word in ['weather', 'temperature']):
        weather = context_data['weather']
        temp = weather.get('temperature_2m')
        humidity = weather.get('relative_humidity_2m')
        if temp is not None:
            enhancements.append(f"\n\n📊 **Current Data**: Temperature is {temp}°C with {humidity}% humidity.")
    
    # Add air quality data if relevant
    if 'air_quality' in context_data and any(word in query_lower for word in ['air', 'quality', 'pollution']):
        aq = context_data['air_quality']
        pm25 = aq.get('pm2_5')
        if pm25 is not None:
            quality_level = "Good" if pm25 <= 25 else "Moderate" if pm25 <= 50 else "Poor"
            enhancements.append(f"\n\n🌬️ **Current Air Quality**: PM2.5 is {pm25} μg/m³ ({quality_level})")
    
    # Add heat island information
    if 'heat_islands' in context_data and any(word in query_lower for word in ['heat', 'island', 'hot']):
        hi = context_data['heat_islands']
        intensity = hi.get('heat_island_intensity')
        if intensity:
            enhancements.append(f"\n\n🌡️ **Heat Island Effect**: Urban areas are {intensity}°C warmer than rural areas.")
            
            if 'hotspots' in hi and hi['hotspots']:
                top_hotspot = hi['hotspots'][0]
                enhancements.append(f"The biggest hotspot is {top_hotspot['name']} with +{top_hotspot['intensity']}°C.")
    
    # Add lake information if asked about water bodies
    if 'lakes' in context_data and any(word in query_lower for word in ['lake', 'water']):
        lakes = context_data['lakes']
        if lakes:
            # Find specific lake if mentioned
            mentioned_lake = None
            for lake in lakes:
                if lake['name'].lower().split()[0] in query_lower:  # Check first word of lake name
                    mentioned_lake = lake
                    break
            
            if mentioned_lake:
                enhancements.append(f"\n\n💧 **{mentioned_lake['name']} Status**: Health score {mentioned_lake['water_quality_index']}/100, Algal bloom risk: {mentioned_lake['algal_bloom_risk']}")
    
    return response + "".join(enhancements)

def render_chatbot(gemini_service: GeminiService, nasa_service: NASAService, weather_service: WeatherService):
    """Wrapper function for chatbot rendering"""
    
    # Quick stats sidebar
    with st.sidebar:
        st.subheader("🤖 Terrabot Stats")
        
        # Get current data for display
        try:
            lat, lon = get_bengaluru_coordinates()
            weather_data = weather_service.get_current_weather(lat, lon)
            air_quality_data = weather_service.get_air_quality(lat, lon)
            
            if weather_data:
                temp = weather_data.get('temperature_2m', 'N/A')
                st.write(f"🌡️ Current: {temp}°C")
            
            if air_quality_data:
                pm25 = air_quality_data.get('pm2_5', 'N/A')
                st.write(f"🌬️ PM2.5: {pm25} μg/m³")
            
        except Exception as e:
            st.write("📊 Data loading...")
        
        st.write("🎯 **I can help with:**")
        st.write("• Current weather & air quality")
        st.write("• Heat island hotspots") 
        st.write("• Lake health status")
        st.write("• Urban climate patterns")
        st.write("• Health recommendations")
        st.write("• Climate trends analysis")
    
    # Main chatbot interface
    render_chatbot_interface(gemini_service, nasa_service, weather_service)

def get_contextual_suggestions(query: str) -> List[str]:
    """Get contextual follow-up suggestions based on the query"""
    
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['air', 'quality', 'pollution']):
        return [
            "Which areas have the cleanest air?",
            "What causes air pollution in Bengaluru?",
            "When is the best time for outdoor exercise?"
        ]
    elif any(word in query_lower for word in ['temperature', 'weather', 'hot']):
        return [
            "What's the heat index like today?",
            "Which areas are coolest in the city?",
            "How does weather affect air quality?"
        ]
    elif any(word in query_lower for word in ['lake', 'water']):
        return [
            "Which lakes are safe for recreational activities?",
            "What's being done to restore lake health?",
            "How do lakes affect local climate?"
        ]
    else:
        return [
            "What's the overall climate situation today?",
            "Are there any climate alerts for the city?",
            "What can citizens do to help with climate issues?"
        ]
