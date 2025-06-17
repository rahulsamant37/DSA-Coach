import httpx
import streamlit as st
import logging
from typing import Dict, Any, Optional, List
from shared.config import API_URL
from shared.models import (
    UserProfile, ProblemGenerationRequest, HintRequest, 
    CodeReviewRequest, APIResponse
)

import os
from dotenv import load_dotenv
load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.timeout = 30.0
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make HTTP request to the API"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            st.error("Request timed out. Please try again.")
            logger.error(f"Timeout for {method} {endpoint}")
            return None
        except httpx.ConnectError:
            st.error("Cannot connect to the backend service. Please ensure the API server is running.")
            logger.error(f"Connection error for {method} {endpoint}")
            return None
        except httpx.HTTPStatusError as e:
            st.error(f"API request failed: {e.response.status_code}")
            logger.error(f"HTTP error {e.response.status_code} for {method} {endpoint}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected error for {method} {endpoint}: {str(e)}")
            return None
    
    # Health and Status
    def health_check(self) -> bool:
        """Check if API is healthy"""
        result = self._make_request("GET", "/health")
        return result is not None and result.get("status") == "healthy"
    
    def get_api_status(self) -> Optional[Dict[str, Any]]:
        """Get API and service status"""
        return self._make_request("GET", "/api/status")
    
    # User Profile
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        result = self._make_request("GET", f"/api/users/{user_id}/profile")
        
        if result and result.get("success") and result.get("data"):
            try:
                return UserProfile(**result["data"])
            except Exception as e:
                logger.error(f"Error parsing user profile: {str(e)}")
                return None
        return None
    
    def update_user_profile(self, user_id: str, profile: UserProfile) -> bool:
        """Update user profile"""
        result = self._make_request(
            "POST", 
            f"/api/users/{user_id}/profile",
            json=profile.model_dump()
        )
        
        return result is not None and result.get("success", False)
    
    # Problem Generation
    def generate_problem(self, user_id: str, request: ProblemGenerationRequest) -> Optional[List[Dict[str, Any]]]:
        """Generate problem variations"""
        result = self._make_request(
            "POST",
            "/api/problems/generate",
            json=request.model_dump(),
            params={"user_id": user_id}
        )
        
        if result and result.get("success") and result.get("data"):
            return result["data"].get("problems", [])
        return None
    
    def get_random_problem(self) -> Optional[Dict[str, Any]]:
        """Get a random practice problem"""
        result = self._make_request("GET", "/api/problems/random")
        
        if result and result.get("success") and result.get("data"):
            return result["data"]
        return None
    
    def get_recent_problems(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent problems"""
        result = self._make_request(
            "GET",
            f"/api/users/{user_id}/problems/recent",
            params={"limit": limit}
        )
        
        if result and result.get("success") and result.get("data"):
            return result["data"]
        return []
    
    # Hint System
    def get_next_hint(self, user_id: str, request: HintRequest) -> Optional[Dict[str, Any]]:
        """Get next level hint"""
        result = self._make_request(
            "POST",
            "/api/hints/next",
            json=request.model_dump(),
            params={"user_id": user_id}
        )
        
        if result and result.get("success") and result.get("data"):
            return result["data"]
        return None
    
    def get_personalized_hint(self, user_id: str, user_approach: str) -> Optional[Dict[str, Any]]:
        """Get personalized hint based on user approach"""
        result = self._make_request(
            "POST",
            "/api/hints/personalized",
            params={"user_id": user_id, "user_approach": user_approach}
        )
        
        if result and result.get("success") and result.get("data"):
            return result["data"]
        return None
      # Code Review
    def review_code(self, code: str, language: str, problem_context: str = "", 
                   focus_areas: List[str] = None, review_depth: str = "detailed",
                   include_suggestions: bool = True, user_id: str = "anonymous") -> Optional[Dict[str, Any]]:
        """Review submitted code with flexible parameters"""
        try:
            from shared.models import CodeReviewRequest
            
            # Create a CodeReviewRequest object
            request = CodeReviewRequest(
                code=code,
                language=language,
                focus_aspects=focus_areas or ["correctness", "efficiency", "style"]
            )
            
            result = self._make_request(
                "POST",
                "/api/code-review",
                json=request.model_dump(),
                params={"user_id": user_id}
            )
            
            if result and result.get("success") and result.get("data"):
                return result["data"]
            return None
        except Exception as e:
            logger.error(f"Error in review_code: {str(e)}")
            return None
    
    def get_code_review_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's code review history"""
        result = self._make_request(
            "GET",
            f"/api/users/{user_id}/code-reviews",
            params={"limit": limit}
        )
        
        if result and result.get("success") and result.get("data"):
            return result["data"]
        return []
    
    # User Progress
    def get_user_progress(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user progress data"""
        result = self._make_request("GET", f"/api/users/{user_id}/progress")
        
        if result and result.get("success") and result.get("data"):
            return result["data"]
        return None
    
    # System
    def get_system_stats(self) -> Optional[Dict[str, Any]]:
        """Get system statistics"""
        result = self._make_request("GET", "/api/system/stats")
        
        if result and result.get("success") and result.get("data"):
            return result["data"]
        return None
    
    # Additional methods for frontend components
    def generate_problem(self, difficulty: str = "Medium", topics: List[str] = None, 
                        patterns: List[str] = None, companies: List[str] = None, 
                        user_id: str = "anonymous") -> Optional[Dict[str, Any]]:
        """Generate a single problem based on criteria"""
        try:
            # Use the random problem endpoint as a starting point
            result = self.get_random_problem()
            
            if result:
                # Add the requested metadata
                result['difficulty'] = difficulty
                result['topics'] = topics or []
                result['patterns'] = patterns or []
                result['companies'] = companies or []
                
                # Generate a more detailed problem structure
                if not result.get('examples'):
                    result['examples'] = [
                        {
                            "input": "Example input",
                            "output": "Example output",
                            "explanation": "Explanation of the example"
                        }
                    ]
                
                if not result.get('constraints'):
                    result['constraints'] = ["1 <= n <= 10^5", "Time limit: 1 second"]
                
                result['id'] = f"problem_{user_id}_{difficulty.lower()}"
                
            return result
        except Exception as e:
            logger.error(f"Error generating problem: {str(e)}")
            return None
      def get_progressive_hint(self, problem_id: str = None, user_code: str = "", 
                           user_id: str = "anonymous") -> Optional[Dict[str, Any]]:
        """Get a progressive hint for the current problem"""
        try:
            # Create a hint request
            from shared.models import HintRequest
            
            hint_request = HintRequest(
                user_approach=user_code,
                current_hint_level=1,
                specific_question=""
            )
            
            return self.get_next_hint(user_id, hint_request)
        except Exception as e:
            logger.error(f"Error getting progressive hint: {str(e)}")
            return None
    
    def generate_problem_variations(self, problem_id: str = None, user_id: str = "anonymous", 
                                  problem_text: str = "", num_variations: int = 3, 
                                  difficulty_level: str = "Medium", context_options: List[str] = None,
                                  focus_areas: List[str] = None, include_hints: bool = True) -> Optional[Dict[str, Any]]:
        """Generate problem variations - supports both old and new interface"""
        try:
            from shared.models import ProblemGenerationRequest, DifficultyLevel
            
            # Convert string difficulty to enum
            difficulty_map = {
                "Easy": DifficultyLevel.EASY,
                "Medium": DifficultyLevel.MEDIUM, 
                "Hard": DifficultyLevel.HARD
            }
            difficulty_enum = difficulty_map.get(difficulty_level, DifficultyLevel.MEDIUM)
            
            # Create request object
            request = ProblemGenerationRequest(
                original_problem=problem_text or "Generate algorithm practice problems",
                num_variations=num_variations,
                difficulty_level=difficulty_enum,
                context_options=context_options or ["arrays", "strings", "trees"],
                focus_areas=focus_areas or [],
                include_hints=include_hints
            )
            
            # Use the generate problems endpoint
            problems = self.generate_problem(user_id=user_id, request=request)
            
            if problems:
                # Format as variations
                variations = []
                for i, problem in enumerate(problems[:num_variations]):
                    variation = {
                        'id': f"variation_{i+1}",
                        'title': problem.get('title', f'Variation {i+1}'),
                        'description': problem.get('statement', problem.get('description', '')),
                        'difficulty': problem.get('difficulty', difficulty_level),
                        'examples': problem.get('examples', []),
                        'constraints': problem.get('constraints', [])
                    }
                    variations.append(variation)
                
                return {
                    'success': True,
                    'variations': variations,
                    'count': len(variations)
                }
            
            return None
        except Exception as e:
            logger.error(f"Error generating problem variations: {str(e)}")
            return None
    
    def add_to_favorites(self, user_id: str, problem: Dict[str, Any]) -> bool:
        """Add problem to favorites"""
        result = self._make_request(
            "POST",
            f"/api/users/{user_id}/favorites",
            json=problem
        )
        
        return result is not None and result.get("success", False)
    
    def get_progressive_hint(self, user_id: str, hint_request: HintRequest) -> Optional[Dict[str, Any]]:
        """Get progressive hint"""
        result = self._make_request(
            "POST",
            "/api/hints/progressive",
            json=hint_request.model_dump(),
            params={"user_id": user_id}
        )
        
        return result
    
    def verify_solution(self, user_id: str, problem_statement: str, user_code: str, difficulty: str) -> Optional[Dict[str, Any]]:
        """Verify user solution"""
        data = {
            "problem_statement": problem_statement,
            "user_code": user_code,
            "difficulty": difficulty
        }
        
        result = self._make_request(
            "POST",
            "/api/solutions/verify",
            json=data,
            params={"user_id": user_id}
        )
        
        return result
    
    def get_solution_hint(self, user_id: str, problem_statement: str, user_code: str) -> Optional[Dict[str, Any]]:
        """Get solution specific hint"""
        data = {
            "problem_statement": problem_statement,
            "user_code": user_code
        }
        
        result = self._make_request(
            "POST",
            "/api/hints/solution",
            json=data,
            params={"user_id": user_id}
        )
        
        return result
    
    def get_full_solution(self, user_id: str, problem_statement: str) -> Optional[Dict[str, Any]]:
        """Get complete solution"""
        data = {
            "problem_statement": problem_statement
        }
        
        result = self._make_request(
            "POST",
            "/api/solutions/complete",
            json=data,
            params={"user_id": user_id}
        )
        
        return result
    
    def update_user_progress(self, user_id: str, problem_solved: Dict[str, Any], hints_used: int) -> bool:
        """Update user progress"""
        data = {
            "problem_solved": problem_solved,
            "hints_used": hints_used
        }
        
        result = self._make_request(
            "POST",
            f"/api/users/{user_id}/progress",
            json=data
        )
        
        return result is not None and result.get("success", False)
    
    def review_code(self, user_id: str, code: str, language: str, focus_areas: List[str]) -> Optional[Dict[str, Any]]:
        """Review code"""
        data = {
            "code": code,
            "language": language,
            "focus_areas": focus_areas
        }
        
        result = self._make_request(
            "POST",
            "/api/code/review",
            json=data,
            params={"user_id": user_id}
        )
        
        return result
    
    def save_code_review(self, user_id: str, review_data: Dict[str, Any]) -> bool:
        """Save code review"""
        result = self._make_request(
            "POST",
            f"/api/users/{user_id}/reviews",
            json=review_data
        )
        
        return result is not None and result.get("success", False)
    
    def update_user_goals(self, user_id: str, goals: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user goals"""
        result = self._make_request(
            "POST",
            f"/api/users/{user_id}/goals",
            json=goals
        )
        
        return result

# Global API client instance
api_client = APIClient()
