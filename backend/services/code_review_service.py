import logging
from typing import Dict, Any
from datetime import datetime
from shared.models import CodeReviewRequest, CodeReviewResponse, CodeAnalysis
from backend.services.gemini_service import GeminiService

class CodeReviewService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service
        self.logger = logging.getLogger(__name__)
    
    def review_code(self, request: CodeReviewRequest, user_context: Dict[str, Any] = None) -> CodeReviewResponse:
        """Generate comprehensive code review"""
        try:
            prompt = self._generate_code_review_prompt(request)
            response = self.gemini_service.generate_response(prompt, user_context)
            
            # Parse the response into structured data
            review_data = self._parse_review_response(response)
            
            return CodeReviewResponse(
                overall_analysis=review_data['overall'],
                issues=review_data['issues'],
                optimizations=review_data['optimizations'],
                alternatives=review_data['alternatives'],
                review_timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error generating code review: {str(e)}")
            return self._get_fallback_review(request)
    
    def _generate_code_review_prompt(self, request: CodeReviewRequest) -> str:
        """Generate comprehensive code review prompt"""
        aspects_text = ', '.join(request.focus_aspects) if request.focus_aspects else "all aspects"
        
        prompt = f"""
        As DSA-COACH AI, provide a comprehensive code review for this {request.language} code:
        
        Problem Context: {request.problem_context if request.problem_context else "Not provided"}
        
        Code:
        ```{request.language}
        {request.code}
        ```
        
        Additional Context: {request.additional_context if request.additional_context else "None"}
        
        Focus on these aspects: {aspects_text}
        
        Provide a detailed analysis including:
        
        1. OVERALL ANALYSIS:
           - Correctness assessment (score 1-10)
           - Time complexity analysis
           - Space complexity analysis
           - Code style rating (1-10)
           - Brief summary of the solution quality
        
        2. ISSUES FOUND:
           - Logic errors or bugs
           - Edge cases not handled
           - Performance issues
           - Style/readability problems
           - Security concerns (if applicable)
        
        3. OPTIMIZATIONS:
           - Performance improvements
           - Memory usage optimizations
           - Cleaner implementation suggestions
           - Best practice recommendations
        
        4. ALTERNATIVE APPROACHES:
           - Different algorithms that could work
           - Trade-offs between approaches
           - When to use each approach
           - More elegant or efficient solutions
        
        Be constructive and educational. Explain the 'why' behind your suggestions.
        Format your response with clear section headers.
        """
        
        return prompt
    
    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured review data"""
        sections = {
            'overall': CodeAnalysis(
                correctness_score=7,
                time_complexity="O(n)",
                space_complexity="O(1)",
                style_rating=7,
                summary="Code analysis completed"
            ),
            'issues': [],
            'optimizations': [],
            'alternatives': []
        }
        
        try:
            current_section = None
            current_content = []
            
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                line_lower = line.lower()
                
                # Detect section headers
                if 'overall analysis' in line_lower or '1.' in line and 'overall' in line_lower:
                    if current_section and current_content:
                        sections[current_section] = self._process_section_content(current_section, current_content)
                    current_section = 'overall'
                    current_content = []
                elif 'issues found' in line_lower or '2.' in line and 'issues' in line_lower:
                    if current_section and current_content:
                        sections[current_section] = self._process_section_content(current_section, current_content)
                    current_section = 'issues'
                    current_content = []
                elif 'optimizations' in line_lower or '3.' in line and 'optimization' in line_lower:
                    if current_section and current_content:
                        sections[current_section] = self._process_section_content(current_section, current_content)
                    current_section = 'optimizations'
                    current_content = []
                elif 'alternative' in line_lower or '4.' in line and 'alternative' in line_lower:
                    if current_section and current_content:
                        sections[current_section] = self._process_section_content(current_section, current_content)
                    current_section = 'alternatives'
                    current_content = []
                elif line and current_section:
                    current_content.append(line)
            
            # Handle the last section
            if current_section and current_content:
                sections[current_section] = self._process_section_content(current_section, current_content)
            
        except Exception as e:
            self.logger.warning(f"Error parsing review response: {str(e)}")
        
        return sections
    
    def _process_section_content(self, section: str, content: list) -> Any:
        """Process content for each section type"""
        if section == 'overall':
            return self._parse_overall_section('\n'.join(content))
        else:
            return self._parse_list_section('\n'.join(content))
    
    def _parse_overall_section(self, content: str) -> CodeAnalysis:
        """Parse overall analysis section"""
        # Initialize with defaults
        analysis = CodeAnalysis(
            correctness_score=7,
            time_complexity="O(n)",
            space_complexity="O(1)",
            style_rating=7,
            summary=content[:200] + "..." if len(content) > 200 else content
        )
        
        # Try to extract specific metrics
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            
            if 'correctness' in line_lower and any(char.isdigit() for char in line):
                try:
                    score = int(''.join(filter(str.isdigit, line)))
                    if 1 <= score <= 10:
                        analysis.correctness_score = score
                except:
                    pass
            
            elif 'style' in line_lower and any(char.isdigit() for char in line):
                try:
                    score = int(''.join(filter(str.isdigit, line)))
                    if 1 <= score <= 10:
                        analysis.style_rating = score
                except:
                    pass
            
            elif 'time complexity' in line_lower:
                # Extract O() notation
                if 'o(' in line_lower:
                    start = line_lower.find('o(')
                    end = line.find(')', start)
                    if end != -1:
                        analysis.time_complexity = line[start:end+1]
            
            elif 'space complexity' in line_lower:
                # Extract O() notation
                if 'o(' in line_lower:
                    start = line_lower.find('o(')
                    end = line.find(')', start)
                    if end != -1:
                        analysis.space_complexity = line[start:end+1]
        
        return analysis
    
    def _parse_list_section(self, content: str) -> list:
        """Parse sections that contain lists of items"""
        items = []
        current_item = ""
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Check if line starts a new item (bullet point, number, dash)
            if line.startswith(('-', '•', '*')) or (line and line[0].isdigit() and '.' in line[:3]):
                if current_item:
                    items.append(current_item.strip())
                current_item = line.lstrip('-•*0123456789. ')
            elif line and current_item:
                current_item += " " + line
            elif line and not current_item:
                current_item = line
        
        # Add the last item
        if current_item:
            items.append(current_item.strip())
        
        return [item for item in items if item]  # Filter out empty items
    
    def _get_fallback_review(self, request: CodeReviewRequest) -> CodeReviewResponse:
        """Provide fallback review when AI generation fails"""
        
        analysis = CodeAnalysis(
            correctness_score=6,
            time_complexity="Unable to analyze",
            space_complexity="Unable to analyze", 
            style_rating=6,
            summary="Code review service temporarily unavailable. Please try again later."
        )
        
        return CodeReviewResponse(
            overall_analysis=analysis,
            issues=["Unable to analyze issues at this time"],
            optimizations=["Please resubmit your code for optimization suggestions"],
            alternatives=["Alternative approaches analysis unavailable"],
            review_timestamp=datetime.now()
        )
