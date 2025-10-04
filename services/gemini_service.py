import os
import json
from typing import Dict, List, Optional
from google import genai
from google.genai import types

class GeminiService:
    """Service for Gemini AI integration"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            print("Warning: GEMINI_API_KEY not found in environment variables")
    
    def generate_climate_response(self, query: str, context_data: Optional[Dict] = None) -> str:
        """Generate AI response for climate-related queries"""
        if not self.client:
            return "AI Assistant is currently unavailable. Please check API configuration."
        
        try:
            # Prepare context from available data
            context = self._prepare_context(context_data)
            
            system_prompt = """
            You are Terrabot, an AI climate assistant for Bengaluru's climate resilience dashboard.
            You have access to real-time NASA Earth observation data, weather information, and air quality data.
            
            Your role is to:
            1. Answer questions about climate conditions in Bengaluru
            2. Provide insights about air quality, temperature, water bodies, and urban heat islands
            3. Give actionable advice for citizens and policymakers
            4. Explain complex climate data in simple terms
            5. Suggest climate adaptation and mitigation strategies
            
            Always be helpful, accurate, and focused on Bengaluru's climate challenges.
            Use the provided context data to give specific, real-time answers when possible.
            """
            
            user_message = f"""
            Context Data: {context}
            
            User Query: {query}
            
            Please provide a helpful response based on the available data and your knowledge about Bengaluru's climate.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=user_message)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=1000
                )
            )
            
            return response.text if response.text else "I'm sorry, I couldn't generate a response at this time."
            
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def analyze_climate_trends(self, data: Dict) -> str:
        """Analyze climate trends and provide insights"""
        if not self.client:
            return "AI analysis is currently unavailable."
        
        try:
            prompt = f"""
            Analyze the following climate data for Bengaluru and provide insights:
            
            Data: {json.dumps(data, indent=2)}
            
            Please provide:
            1. Key trends and patterns
            2. Areas of concern
            3. Recommendations for improvement
            4. Comparison with normal values if applicable
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else "Unable to analyze trends at this time."
            
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def generate_recommendations(self, stakeholder: str, issue: str, data: Dict) -> str:
        """Generate stakeholder-specific recommendations"""
        if not self.client:
            return "Recommendations service is currently unavailable."
        
        try:
            prompt = f"""
            As Terrabot, provide specific recommendations for {stakeholder} regarding {issue} in Bengaluru.
            
            Available data: {json.dumps(data, indent=2)}
            
            Provide actionable, specific recommendations that this stakeholder can implement.
            Consider their role, authority, and resources.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3)
            )
            
            return response.text if response.text else "Unable to generate recommendations at this time."
            
        except Exception as e:
            return f"Recommendation error: {str(e)}"
    
    def explain_climate_data(self, data_type: str, value: float, context: str = "") -> str:
        """Explain climate data in simple terms"""
        if not self.client:
            return f"{data_type}: {value} - AI explanation unavailable."
        
        try:
            prompt = f"""
            Explain this climate data point in simple, easy-to-understand language for citizens:
            
            Data Type: {data_type}
            Value: {value}
            Context: {context}
            
            Explain what this means, whether it's good or bad, and what citizens should know or do about it.
            Keep it concise but informative.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else f"{data_type}: {value}"
            
        except Exception as e:
            return f"{data_type}: {value} - Explanation error: {str(e)}"
    
    def _prepare_context(self, context_data: Optional[Dict] = None) -> str:
        """Prepare context data for AI queries"""
        if not context_data:
            return "No specific data available."
        
        context_parts = []
        
        if "weather" in context_data:
            weather = context_data["weather"]
            context_parts.append(f"Current weather: {weather.get('temperature_2m', 'N/A')}°C, {weather.get('relative_humidity_2m', 'N/A')}% humidity")
        
        if "air_quality" in context_data:
            aq = context_data["air_quality"]
            context_parts.append(f"Air quality: PM2.5 {aq.get('pm2_5', 'N/A')} μg/m³, PM10 {aq.get('pm10', 'N/A')} μg/m³")
        
        if "heat_islands" in context_data:
            hi = context_data["heat_islands"]
            context_parts.append(f"Heat island intensity: {hi.get('heat_island_intensity', 'N/A')}°C above rural areas")
        
        return "; ".join(context_parts) if context_parts else "Limited data available."
    
    def get_daily_climate_summary(self, all_data: Dict) -> str:
        """Generate daily climate summary for Bengaluru"""
        if not self.client:
            return "Daily summary is currently unavailable."
        
        try:
            prompt = f"""
            Create a daily climate summary for Bengaluru citizens based on this data:
            
            {json.dumps(all_data, indent=2)}
            
            Include:
            1. Today's weather highlights
            2. Air quality status and recommendations
            3. Any climate alerts or concerns
            4. Tips for the day based on conditions
            
            Keep it informative but brief, suitable for a dashboard display.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else "Unable to generate daily summary."
            
        except Exception as e:
            return f"Summary generation error: {str(e)}"
