import logging
from typing import Optional
from datetime import datetime
from shared.models import HintRequest, HintResponse, Hint, Problem
from backend.services.gemini_service import GeminiService

class HintService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service
        self.logger = logging.getLogger(__name__)
        self.max_hint_levels = 4
    
    def get_hint(self, request: HintRequest, problem: Problem, user_context: Optional[dict] = None) -> HintResponse:
        """Get the next level hint for a problem"""
        try:
            next_level = request.current_hint_level + 1
            
            if next_level > self.max_hint_levels:
                raise ValueError("Maximum hint level reached")
            
            prompt = self._create_hint_prompt(problem, next_level, request.user_approach)
            hint_content = self.gemini_service.generate_response(prompt, user_context)
            
            hint = Hint(
                level=next_level,
                content=hint_content,
                hint_type=self._get_hint_type(next_level),
                timestamp=datetime.now()
            )
            
            return HintResponse(
                hint=hint,
                next_available=next_level < self.max_hint_levels,
                total_levels=self.max_hint_levels
            )
            
        except Exception as e:
            self.logger.error(f"Error generating hint: {str(e)}")
            # Return fallback hint
            return self._get_fallback_hint(request.current_hint_level + 1)
    
    def get_personalized_hint(self, user_approach: str, problem: Problem, user_context: Optional[dict] = None) -> HintResponse:
        """Get a personalized hint based on user's current approach"""
        try:
            prompt = self._create_personalized_hint_prompt(problem, user_approach)
            hint_content = self.gemini_service.generate_response(prompt, user_context)
            
            hint = Hint(
                level=0,  # Personalized hints are level 0
                content=hint_content,
                hint_type="personalized",
                timestamp=datetime.now()
            )
            
            return HintResponse(
                hint=hint,
                next_available=True,
                total_levels=self.max_hint_levels
            )
            
        except Exception as e:
            self.logger.error(f"Error generating personalized hint: {str(e)}")
            return self._get_fallback_hint(0, hint_type="personalized")
    
    def get_stuck_help(self, problem: Problem, user_context: Optional[dict] = None) -> HintResponse:
        """Provide emergency guidance when user is completely stuck"""
        try:
            prompt = self._create_stuck_help_prompt(problem)
            hint_content = self.gemini_service.generate_response(prompt, user_context)
            
            hint = Hint(
                level=-1,  # Special level for stuck help
                content=hint_content,
                hint_type="emergency",
                timestamp=datetime.now()
            )
            
            return HintResponse(
                hint=hint,
                next_available=True,
                total_levels=self.max_hint_levels
            )
            
        except Exception as e:
            self.logger.error(f"Error generating stuck help: {str(e)}")
            return self._get_fallback_hint(-1, hint_type="emergency")
    
    def _create_hint_prompt(self, problem: Problem, hint_level: int, user_approach: Optional[str]) -> str:
        """Create appropriate prompt for each hint level"""
        problem_statement = problem.statement
        user_approach_text = f"\nUser's current approach: {user_approach}" if user_approach else ""
        
        base_prompt = f"""
        As DSA-COACH AI, provide a Level {hint_level} hint for this problem:
        
        Problem: {problem_statement}
        {user_approach_text}
        """
        
        if hint_level == 1:
            return base_prompt + """
            
            Provide Level 1 hint - CLARIFYING QUESTIONS:
            - Ask 2-3 thought-provoking questions to help understand the problem better
            - Guide them to identify key constraints and requirements
            - Help them think about edge cases
            - Don't reveal the algorithm or approach yet
            
            Focus on problem comprehension, not solution approach.
            """
        
        elif hint_level == 2:
            return base_prompt + """
            
            Provide Level 2 hint - ALGORITHM DIRECTION:
            - Suggest the general algorithmic approach (e.g., "Consider using two pointers")
            - Mention the data structure family that might be helpful
            - Explain WHY this approach fits the problem
            - Don't give implementation details yet
            
            Guide them toward the right algorithmic thinking.
            """
        
        elif hint_level == 3:
            return base_prompt + """
            
            Provide Level 3 hint - SOLUTION STRUCTURE:
            - Outline the high-level steps of the solution
            - Explain the overall structure and flow
            - Mention key variables or data structures needed
            - Still avoid specific code implementation
            
            Help them see the solution framework.
            """
        
        elif hint_level == 4:
            return base_prompt + """
            
            Provide Level 4 hint - IMPLEMENTATION HELP:
            - Give specific implementation guidance
            - Show pseudocode or key code snippets if needed
            - Address common implementation pitfalls
            - Help with the trickiest parts of coding
            
            Provide concrete implementation assistance while encouraging independent coding.
            """
        
        return base_prompt
    
    def _create_personalized_hint_prompt(self, problem: Problem, user_approach: str) -> str:
        """Create prompt for personalized hint based on user's approach"""
        return f"""
        As DSA-COACH AI, analyze the user's current approach and provide personalized guidance:
        
        Problem: {problem.statement}
        
        User's Current Approach: {user_approach}
        
        Please:
        1. Evaluate their approach - is it on the right track?
        2. If correct direction: Encourage and give next steps
        3. If incorrect: Gently redirect without discouraging
        4. Provide specific, actionable guidance based on their thinking
        5. Ask follow-up questions to guide their thought process
        
        Be supportive and build on their existing understanding.
        """
    
    def _create_stuck_help_prompt(self, problem: Problem) -> str:
        """Create prompt for emergency stuck help"""
        return f"""
        As DSA-COACH AI, the user is completely stuck on this problem. Provide emergency guidance:
        
        Problem: {problem.statement}
        
        The user needs immediate help to get unstuck. Please:
        1. Reassure them that being stuck is normal and part of learning
        2. Suggest a simpler version of the problem to start with
        3. Provide a concrete first step they can take
        4. Offer an analogy or real-world example to build intuition
        5. Suggest breaking the problem into smaller pieces
        
        Focus on getting them moving again with confidence.
        """
    
    def _get_hint_type(self, level: int) -> str:
        """Get hint type based on level"""
        hint_types = {
            1: "clarifying",
            2: "direction",
            3: "structure",
            4: "implementation"
        }
        return hint_types.get(level, "general")
    
    def _get_fallback_hint(self, level: int, hint_type: Optional[str] = None) -> HintResponse:
        """Provide fallback hint when AI generation fails"""
        fallback_hints = {
            1: "Let's start by understanding the problem better. What are the inputs and expected outputs? What constraints should we consider?",
            2: "Think about what data structures or algorithms might be helpful here. Consider the time complexity requirements.",
            3: "Try breaking the problem into smaller steps. What would be the main phases of your solution?",
            4: "Focus on implementing one part at a time. Start with the basic logic and handle edge cases later.",
            0: "Based on your approach, you're thinking in the right direction. What specific part would you like to explore further?",
            -1: "It's okay to feel stuck! Try starting with a simpler version of this problem. What would be the most basic case you could solve?"
        }
        
        content = fallback_hints.get(level, "Keep thinking through the problem step by step. You're making progress!")
        
        hint = Hint(
            level=level,
            content=content,
            hint_type=hint_type or self._get_hint_type(level),
            timestamp=datetime.now()
        )
        
        return HintResponse(
            hint=hint,
            next_available=level < self.max_hint_levels,
            total_levels=self.max_hint_levels
        )
