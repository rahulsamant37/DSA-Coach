import logging
from typing import List, Dict, Any
from shared.models import Problem, ProblemGenerationRequest, DifficultyLevel
from backend.services.gemini_service import GeminiService

class ProblemGeneratorService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service
        self.logger = logging.getLogger(__name__)
    
    def generate_problems(self, request: ProblemGenerationRequest) -> List[Problem]:
        """Generate problem variations based on the request"""
        try:
            prompt = self._create_generation_prompt(request)
            response = self.gemini_service.generate_response(prompt)
            
            problems = self._parse_generated_problems(response)
            
            if not problems:
                # Fallback with simpler approach
                self.logger.warning("Failed to parse AI response, using fallback")
                problems = self._generate_fallback_problems(request)
            
            return problems
            
        except Exception as e:
            self.logger.error(f"Error generating problems: {str(e)}")
            return self._generate_fallback_problems(request)
    
    def _create_generation_prompt(self, request: ProblemGenerationRequest) -> str:
        """Create a detailed prompt for problem generation"""
        focus_text = ""
        if request.focus_areas:
            focus_text = f"Focus specifically on: {', '.join(request.focus_areas)}"
        
        hint_instruction = "Include a high-level approach hint for each variation." if request.include_hints else "Do not include solution hints."
        
        prompt = f"""
        As DSA-COACH AI, analyze the following coding problem and generate {request.num_variations} similar problem variations.

        Original Problem:
        {request.original_problem}

        Requirements:
        1. Generate {request.num_variations} variations that practice the same core algorithmic concept
        2. Difficulty level: {request.difficulty_level.value}
        3. Include these context variations: {', '.join(request.context_options)}
        4. {focus_text}
        5. {hint_instruction}
        6. Each variation should have:
           - A clear problem title
           - Complete problem statement with examples
           - Same core algorithmic pattern but different context
           - Appropriate constraints
           - Estimated solve time
           - Expected time/space complexity

        For each variation, provide:
        - Title: Brief descriptive title
        - Difficulty: Easy/Medium/Hard
        - Core Concept: Main algorithmic concept being practiced
        - Statement: Complete problem description with examples and constraints
        - Context: How it differs from the original
        - Estimated Time: Expected solve time (e.g., "15-20 min")
        - Complexity: Expected time complexity (e.g., "O(n)")
        - Approach Hint: High-level approach (only if requested)

        Format your response as a structured list with clear sections for each problem.
        Make sure each variation is significantly different but tests the same core concept.
        """
        return prompt
    
    def _parse_generated_problems(self, response: str) -> List[Problem]:
        """Parse the AI response into structured problem data"""
        try:
            problems = []
            sections = response.split("Problem")
            
            for i, section in enumerate(sections[1:], 1):
                try:
                    problem = self._parse_problem_section(section, i)
                    if problem:
                        problems.append(problem)
                except Exception as e:
                    self.logger.warning(f"Failed to parse problem {i}: {str(e)}")
                    continue
            
            return problems
        
        except Exception as e:
            self.logger.error(f"Error parsing problems: {str(e)}")
            return []
    
    def _parse_problem_section(self, section: str, problem_num: int) -> Problem:
        """Parse a single problem section"""
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        
        # Initialize with defaults
        title = f"Generated Problem {problem_num}"
        statement = ""
        difficulty = DifficultyLevel.MEDIUM
        core_concept = "Algorithm Practice"
        context = "Generated variation"
        estimated_time = "15-20 min"
        complexity = "O(n)"
        approach_hint = None
        
        current_field = None
        for line in lines:
            line_lower = line.lower()
            
            if line_lower.startswith(('title:', '- title:')):
                title = line.split(':', 1)[1].strip()
                current_field = 'title'
            elif line_lower.startswith(('difficulty:', '- difficulty:')):
                diff_text = line.split(':', 1)[1].strip().lower()
                if 'easy' in diff_text:
                    difficulty = DifficultyLevel.EASY
                elif 'hard' in diff_text:
                    difficulty = DifficultyLevel.HARD
                else:
                    difficulty = DifficultyLevel.MEDIUM
                current_field = 'difficulty'
            elif line_lower.startswith(('statement:', '- statement:', 'description:')):
                statement = line.split(':', 1)[1].strip()
                current_field = 'statement'
            elif line_lower.startswith(('core concept:', '- core concept:', 'concept:')):
                core_concept = line.split(':', 1)[1].strip()
                current_field = 'concept'
            elif line_lower.startswith(('context:', '- context:')):
                context = line.split(':', 1)[1].strip()
                current_field = 'context'
            elif line_lower.startswith(('estimated time:', '- estimated time:', 'time:')):
                estimated_time = line.split(':', 1)[1].strip()
                current_field = 'time'
            elif line_lower.startswith(('complexity:', '- complexity:')):
                complexity = line.split(':', 1)[1].strip()
                current_field = 'complexity'
            elif line_lower.startswith(('hint:', '- hint:', 'approach hint:')):
                approach_hint = line.split(':', 1)[1].strip()
                current_field = 'hint'
            elif current_field == 'statement' and not line.startswith(('-', 'title:', 'difficulty:')):
                # Continue statement on next lines
                statement += " " + line
        
        return Problem(
            title=title,
            statement=statement or f"Practice problem {problem_num} focusing on {core_concept}",
            difficulty=difficulty,
            core_concept=core_concept,
            context=context,
            estimated_time=estimated_time,
            complexity=complexity,
            approach_hint=approach_hint
        )
    
    def _generate_fallback_problems(self, request: ProblemGenerationRequest) -> List[Problem]:
        """Generate fallback problems when AI parsing fails"""
        fallback_problems = [
            {
                "title": "Array Sum Variation",
                "statement": "Find the maximum sum of any contiguous subarray in the given array.",
                "core_concept": "Dynamic Programming",
                "context": "Classic subarray problem"
            },
            {
                "title": "Tree Traversal Challenge",
                "statement": "Implement an iterative in-order traversal of a binary tree.",
                "core_concept": "Tree Traversal",
                "context": "Iterative approach"
            },
            {
                "title": "Hash Table Lookup",
                "statement": "Find two numbers in an array that add up to a target sum.",
                "core_concept": "Hash Tables",
                "context": "Two-sum variation"
            }
        ]
        
        problems = []
        for i, prob_data in enumerate(fallback_problems[:request.num_variations]):
            problem = Problem(
                title=prob_data["title"],
                statement=prob_data["statement"],
                difficulty=request.difficulty_level,
                core_concept=prob_data["core_concept"],
                context=prob_data["context"],
                estimated_time="15-20 min",
                complexity="O(n)",
                approach_hint="Think about the most efficient data structure for this problem." if request.include_hints else None
            )
            problems.append(problem)
        
        return problems
    
    def get_random_problem(self) -> Problem:
        """Generate a random practice problem"""
        random_problems = [
            {
                "title": "Maximum Subarray Sum",
                "statement": "Given an array of integers, find the maximum sum of a contiguous subarray.",
                "core_concept": "Dynamic Programming",
                "context": "Kadane's Algorithm variation"
            },
            {
                "title": "Binary Tree Balance Check",
                "statement": "Implement a function to check if a binary tree is balanced.",
                "core_concept": "Tree Algorithms",
                "context": "Tree property verification"
            },
            {
                "title": "Longest Substring Without Repeating Characters",
                "statement": "Find the length of the longest substring without repeating characters.",
                "core_concept": "Sliding Window",
                "context": "String processing with hash set"
            },
            {
                "title": "Linked List Cycle Detection",
                "statement": "Determine if a linked list has a cycle using Floyd's algorithm.",
                "core_concept": "Two Pointers",
                "context": "Fast and slow pointer technique"
            }
        ]
        
        import random
        selected = random.choice(random_problems)
        
        return Problem(
            title=selected["title"],
            statement=selected["statement"],
            difficulty=DifficultyLevel.MEDIUM,
            core_concept=selected["core_concept"],
            context=selected["context"],
            estimated_time="20-25 min",
            complexity="O(n)",
            approach_hint="Consider the most efficient approach for this problem pattern."
        )
