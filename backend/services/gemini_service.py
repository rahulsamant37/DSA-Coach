import os
import logging
import time
import google.generativeai as genai
from typing import Optional, Dict, Any
from shared.config import GEMINI_API_KEY, GEMINI_MODEL_NAME, MAX_RETRIES, RETRY_DELAY

class GeminiService:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model_name = GEMINI_MODEL_NAME
        self.model = None
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        
        self.logger = logging.getLogger(__name__)
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client"""
        try:
            if not self.api_key:
                self.logger.warning("Gemini API key not configured")
                return
            
            genai.configure(api_key=self.api_key)
            
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 4096,
            }
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            self.logger.info(f"Gemini client initialized with model: {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {str(e)}")
            self.model = None
    
    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response from Gemini model with retry logic"""
        if not self.model:
            raise Exception("Gemini client not initialized. Please check your API key.")
        
        enhanced_prompt = self._enhance_prompt_with_context(prompt, context or {})
        
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(enhanced_prompt)
                
                if response and hasattr(response, 'text') and response.text:
                    self.logger.info(f"Generated response successfully on attempt {attempt + 1}")
                    return response.text.strip()
                else:
                    raise Exception("Empty response from Gemini")
            
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    self.logger.error(f"All {self.max_retries} attempts failed")
                    raise Exception(f"Failed to generate response after {self.max_retries} attempts: {str(e)}")
    
    def _add_system_context(self, prompt: str) -> str:
        """Add system context to the prompt"""
        system_context = """
        You are DSA-COACH AI, an intelligent coding mentor specializing in Data Structures and Algorithms. Your role is to help students master DSA concepts through guided practice, avoiding solution dependency.

        Core principles:
        - Focus on understanding over memorization
        - Provide progressive hints without revealing complete solutions
        - Encourage independent thinking through guided questions
        - Be patient, encouraging, and adapt to the user's level
        - Connect new problems to previously learned concepts
        - Build intuition through analogies and examples

        Always maintain a supportive and educational tone. Guide users to discover solutions independently while building lasting DSA intuition.
        """
        
        return f"{system_context}\n\nUser Request: {prompt}"
    
    def _enhance_prompt_with_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt with conversation context"""
        enhanced_prompt = self._add_system_context(prompt)
        
        if context.get('conversation_history'):
            history = context['conversation_history'][-3:]  # Last 3 exchanges
            history_text = "\n".join([f"Previous: {item}" for item in history])
            enhanced_prompt += f"\n\nConversation History:\n{history_text}"
        
        if context.get('user_profile'):
            profile = context['user_profile']
            enhanced_prompt += f"\n\nUser Profile: Skill Level: {profile.get('skill_level', 'Unknown')}, Goal: {profile.get('target_goal', 'Unknown')}"
        
        if context.get('current_problem'):
            problem = context['current_problem']
            enhanced_prompt += f"\n\nCurrent Problem Context: {problem.get('title', 'N/A')} - {problem.get('difficulty', 'Unknown')} difficulty"
        
        return enhanced_prompt
    
    def test_connection(self) -> bool:
        """Test if the Gemini API connection is working"""
        try:
            if not self.model:
                return False
            
            test_response = self.model.generate_content("Hello, this is a test. Please respond with 'Test successful.'")
            return test_response and hasattr(test_response, 'text') and 'test successful' in test_response.text.lower()
        
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def update_api_key(self, new_api_key: str):
        """Update the API key and reinitialize the client"""
        self.api_key = new_api_key
        os.environ["GEMINI_API_KEY"] = new_api_key
        self._initialize_client()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_name": self.model_name,
            "api_key_configured": bool(self.api_key),
            "client_initialized": bool(self.model),
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay
        }
