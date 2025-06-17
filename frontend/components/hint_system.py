import streamlit as st
from typing import Dict, Any, Optional

class HintSystemComponent:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def render(self):
        """Render the hint system interface"""
        st.header("💡 Progressive Hint System")
        
        # Initialize session state
        if 'current_problem' not in st.session_state:
            st.session_state.current_problem = None
        if 'user_code' not in st.session_state:
            st.session_state.user_code = ""
        if 'hints_received' not in st.session_state:
            st.session_state.hints_received = []
        if 'hint_level' not in st.session_state:
            st.session_state.hint_level = 0
        
        # Check if we have a problem to work with
        if not st.session_state.current_problem:
            self._display_no_problem_message()
            return
        
        # Display current problem
        self._display_current_problem()
        
        # Code input section
        self._display_code_input()
        
        # Hint system
        self._display_hint_system()
        
        # Progress tracking
        self._display_progress()
    
    def _display_no_problem_message(self):
        """Display message when no problem is selected"""
        st.info("🎯 No problem selected. Please go to the Problem Generator to select or generate a problem first.")
        
        if st.button("🔗 Go to Problem Generator"):
            st.switch_page("Problem_Generator")
        
        # Show sample problem for demo
        st.markdown("### 📝 Sample Problem (for demo)")
        with st.expander("Two Sum Problem", expanded=True):
            st.markdown("""
            **Problem:** Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.
            
            **Example:**
            ```
            Input: nums = [2,7,11,15], target = 9
            Output: [0,1]
            Explanation: nums[0] + nums[1] = 2 + 7 = 9
            ```
            """)
            
            if st.button("Use This Problem for Demo"):
                st.session_state.current_problem = {
                    'id': 'demo_two_sum',
                    'title': 'Two Sum',
                    'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                    'difficulty': 'Easy',
                    'topics': ['Arrays', 'Hash Table'],
                    'examples': [
                        {
                            'input': 'nums = [2,7,11,15], target = 9',
                            'output': '[0,1]',
                            'explanation': 'nums[0] + nums[1] = 2 + 7 = 9'
                        }
                    ]
                }
                st.rerun()
    
    def _display_current_problem(self):
        """Display the current problem"""
        problem = st.session_state.current_problem
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"📝 {problem.get('title', 'Current Problem')}")
            
            with col2:
                difficulty = problem.get('difficulty', 'Medium')
                difficulty_color = {
                    "Easy": "green",
                    "Medium": "orange",
                    "Hard": "red"
                }
                st.markdown(f"**Difficulty:** :{difficulty_color.get(difficulty, 'blue')}[{difficulty}]")
        
        with st.expander("Problem Details", expanded=False):
            st.markdown(problem.get('description', 'No description available'))
            
            if problem.get('examples'):
                st.markdown("**Examples:**")
                for i, example in enumerate(problem['examples'], 1):
                    st.markdown(f"*Example {i}:*")
                    st.code(example.get('input', ''), language='text')
                    st.markdown(f"Output: `{example.get('output', '')}`")
                    if example.get('explanation'):
                        st.markdown(f"*{example['explanation']}*")
    
    def _display_code_input(self):
        """Display the code input section"""
        st.markdown("### 💻 Your Solution")
        
        # Language selection
        languages = ["Python", "Java", "C++", "JavaScript", "Go", "Rust"]
        selected_language = st.selectbox(
            "Programming Language", 
            languages, 
            index=0,
            key="hint_language_selector"
        )
        
        # Code editor
        try:
            from streamlit_ace import st_ace
            
            user_code = st_ace(
                value=st.session_state.user_code,
                language=selected_language.lower(),
                theme='monokai',
                key='hint_code_editor',
                height=250,
                auto_update=False,
                wrap=True,
                annotations=None
            )
            
            if user_code != st.session_state.user_code:
                st.session_state.user_code = user_code
        except ImportError:
            # Fallback to text area if ace editor not available
            user_code = st.text_area(
                "Enter your solution:",
                value=st.session_state.user_code,
                height=250,
                key="hint_code_textarea",
                placeholder="Start typing your solution here..."
            )
            st.session_state.user_code = user_code
        
        # Code stats
        if st.session_state.user_code:
            lines = len(st.session_state.user_code.split('\n'))
            chars = len(st.session_state.user_code)
            st.caption(f"📊 Lines: {lines} | Characters: {chars}")
    
    def _display_hint_system(self):
        """Display the hint system"""
        st.markdown("### 💡 Progressive Hints")
        
        # Hint level indicator
        max_hints = 5
        current_level = st.session_state.hint_level
        
        # Progress bar for hint levels
        progress = current_level / max_hints
        st.progress(progress, text=f"Hint Level: {current_level}/{max_hints}")
        
        # Hint request section
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            hint_types = [
                "General Approach",
                "Data Structure Suggestion", 
                "Algorithm Hint",
                "Implementation Detail",
                "Edge Case Consideration"
            ]
            
            selected_hint_type = st.selectbox(
                "Hint Type:",
                hint_types,
                index=0
            )
        
        with col2:
            if st.button("🔍 Get Hint", use_container_width=True):
                self._request_hint(selected_hint_type)
        
        with col3:
            if st.button("🔄 Reset Hints", use_container_width=True):
                self._reset_hints()
        
        # Display received hints
        if st.session_state.hints_received:
            st.markdown("#### 📋 Hints Received")
            
            for i, hint_data in enumerate(st.session_state.hints_received, 1):
                with st.container():
                    col_hint1, col_hint2 = st.columns([1, 10])
                    
                    with col_hint1:
                        st.markdown(f"**#{i}**")
                    
                    with col_hint2:
                        # Hint type badge
                        hint_type = hint_data.get('type', 'General')
                        st.markdown(f"*{hint_type}*")
                        
                        # Hint content
                        if hint_data.get('level', 0) <= 2:
                            st.info(hint_data.get('content', 'No hint available'))
                        elif hint_data.get('level', 0) <= 4:
                            st.warning(hint_data.get('content', 'No hint available'))
                        else:
                            st.error(hint_data.get('content', 'No hint available'))
                        
                        # Additional info
                        if hint_data.get('code_example'):
                            with st.expander("📝 Code Example"):
                                st.code(hint_data['code_example'], language='python')
                        
                        if hint_data.get('complexity_hint'):
                            st.caption(f"💡 Complexity: {hint_data['complexity_hint']}")
                    
                    st.divider()
        else:
            st.info("💭 No hints requested yet. Click 'Get Hint' to receive your first hint!")
        
        # Hint guidelines
        with st.expander("📚 How Progressive Hints Work"):
            st.markdown("""
            **Progressive Hint System:**
            
            1. **Level 1-2**: High-level approach and direction
            2. **Level 3-4**: Specific algorithms and data structures  
            3. **Level 5**: Detailed implementation guidance
            
            **Tips:**
            - Start with general hints and progress to specific ones
            - Try implementing between hints to reinforce learning
            - Use different hint types to explore various aspects
            - Reset hints to practice the problem fresh
            """)
    
    def _request_hint(self, hint_type: str):
        """Request a hint from the API"""
        if not st.session_state.user_code.strip():
            st.warning("💭 Please write some code first to get a more personalized hint!")
            return
        
        with st.spinner("🤔 Analyzing your code and generating hint..."):
            try:
                response = self.api_client.get_progressive_hint(
                    user_code=st.session_state.user_code,
                    user_id=st.session_state.get('user_id', 'anonymous')
                )
                
                if response:
                    # Add hint to received hints
                    hint_data = {
                        'type': hint_type,
                        'content': response.get('hint', 'No hint available'),
                        'level': response.get('level', st.session_state.hint_level + 1),
                        'code_example': response.get('code_example'),
                        'complexity_hint': response.get('complexity_hint'),
                        'timestamp': response.get('timestamp')
                    }
                    
                    st.session_state.hints_received.append(hint_data)
                    st.session_state.hint_level = min(st.session_state.hint_level + 1, 5)
                    
                    st.success(f"💡 Hint #{len(st.session_state.hints_received)} received!")
                    st.rerun()
                else:
                    st.error("Failed to generate hint. Please try again.")
            
            except Exception as e:
                st.error(f"Error getting hint: {str(e)}")
    
    def _reset_hints(self):
        """Reset all hints and start fresh"""
        st.session_state.hints_received = []
        st.session_state.hint_level = 0
        st.success("🔄 Hints reset! You can start fresh now.")
        st.rerun()
    
    def _display_progress(self):
        """Display progress and statistics"""
        st.markdown("### 📊 Your Progress")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Hints Used", len(st.session_state.hints_received))
        
        with col2:
            st.metric("Current Level", f"{st.session_state.hint_level}/5")
        
        with col3:
            code_completion = min(len(st.session_state.user_code) / 100, 1.0) * 100
            st.metric("Code Progress", f"{code_completion:.0f}%")
        
        with col4:
            if st.session_state.hints_received:
                avg_level = sum(h.get('level', 0) for h in st.session_state.hints_received) / len(st.session_state.hints_received)
                st.metric("Avg Hint Level", f"{avg_level:.1f}")
            else:
                st.metric("Avg Hint Level", "0.0")
        
        # Recommendation system
        if st.session_state.hints_received:
            self._display_recommendations()
    
    def _display_recommendations(self):
        """Display personalized recommendations"""
        st.markdown("#### 🎯 Recommendations")
        
        hint_count = len(st.session_state.hints_received)
        code_length = len(st.session_state.user_code)
        
        recommendations = []
        
        if hint_count >= 3 and code_length < 50:
            recommendations.append("💭 Try implementing some code based on the hints received")
        
        if hint_count >= 4:
            recommendations.append("📚 Consider reviewing similar problems to strengthen understanding")
        
        if st.session_state.hint_level >= 4:
            recommendations.append("🎯 You're getting close! Focus on implementation details")
        
        if not recommendations:
            recommendations.append("✨ You're doing great! Keep working on the solution")
        
        for rec in recommendations:
            st.info(rec)
        
        # Action buttons
        col_rec1, col_rec2 = st.columns(2)
        
        with col_rec1:
            if st.button("📊 Review Code", use_container_width=True):
                if st.session_state.user_code.strip():
                    self._trigger_code_review()
                else:
                    st.warning("Please write some code first!")
        
        with col_rec2:
            if st.button("🎲 Generate Similar Problems", use_container_width=True):
                self._trigger_problem_generation()
    
    def _trigger_code_review(self):
        """Trigger code review (redirect to code review component)"""
        st.info("🔄 Redirecting to Code Review component...")
        # Store current state for code review
        st.session_state.review_code = st.session_state.user_code
        st.session_state.review_problem = st.session_state.current_problem
        # Would redirect to code review page in a real implementation
        st.success("💡 Use the Code Review component to analyze your solution!")
    
    def _trigger_problem_generation(self):
        """Trigger problem generation (redirect to problem generator)"""
        st.info("🔄 Generating similar problems...")
        # Would redirect to problem generator with current problem context
        st.success("💡 Use the Problem Generator to create variations of this problem!")
