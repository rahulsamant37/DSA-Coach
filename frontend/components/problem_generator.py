import streamlit as st
import json
from typing import Dict, Any, Optional

class ProblemGeneratorComponent:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def render(self):
        """Render the problem generator interface"""
        st.header("🧠 DSA Problem Generator")
        
        # Initialize session state
        if 'current_problem' not in st.session_state:
            st.session_state.current_problem = None
        if 'user_solution' not in st.session_state:
            st.session_state.user_solution = ""
        if 'problem_variations' not in st.session_state:
            st.session_state.problem_variations = []
        
        # Sidebar for problem generation controls
        with st.sidebar:
            st.subheader("Problem Settings")
            
            # Difficulty selection
            difficulty = st.selectbox(
                "Difficulty Level",
                ["Easy", "Medium", "Hard"],
                index=1
            )
            
            # Topic selection
            topics = [
                "Arrays", "Strings", "Linked Lists", "Stacks", "Queues",
                "Trees", "Graphs", "Dynamic Programming", "Recursion",
                "Sorting", "Searching", "Greedy", "Backtracking",
                "Two Pointers", "Sliding Window", "Hash Tables"
            ]
            
            selected_topics = st.multiselect(
                "Topics (leave empty for any)",
                topics
            )
            
            # Pattern selection
            patterns = [
                "Two Pointers", "Sliding Window", "Fast & Slow Pointers",
                "Merge Intervals", "Cyclic Sort", "In-place Reversal",
                "Tree BFS", "Tree DFS", "Two Heaps", "Subsets",
                "Modified Binary Search", "Top K Elements", "K-way Merge",
                "Topological Sort", "0/1 Knapsack", "Fibonacci Numbers"
            ]
            
            selected_patterns = st.multiselect(
                "Patterns (leave empty for any)",
                patterns
            )
            
            # Company selection
            companies = [
                "Google", "Amazon", "Microsoft", "Apple", "Facebook",
                "Netflix", "Tesla", "Uber", "LinkedIn", "Twitter"
            ]
            
            selected_companies = st.multiselect(
                "Companies (leave empty for any)",
                companies
            )
            
            # Generate button
            if st.button("🎯 Generate New Problem", use_container_width=True):
                self._generate_problem(difficulty, selected_topics, selected_patterns, selected_companies)
        
        # Main content area
        if st.session_state.current_problem:
            self._display_problem()
            self._display_solution_interface()
            self._display_variations()
        else:
            self._display_welcome_message()
    
    def _generate_problem(self, difficulty: str, topics: list, patterns: list, companies: list):
        """Generate a new problem using the API"""
        with st.spinner("🤖 Generating your personalized DSA problem..."):
            try:
                response = self.api_client.generate_problem(
                    difficulty=difficulty,
                    topics=topics,
                    patterns=patterns,
                    companies=companies,
                    user_id=st.session_state.get('user_id', 'anonymous')
                )
                
                if response:
                    st.session_state.current_problem = response
                    st.session_state.user_solution = ""
                    st.session_state.problem_variations = []
                    st.success("✨ New problem generated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to generate problem. Please try again.")
            except Exception as e:
                st.error(f"Error generating problem: {str(e)}")
    
    def _display_problem(self):
        """Display the current problem"""
        problem = st.session_state.current_problem
        
        # Problem header
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(f"📝 {problem.get('title', 'Problem')}")
        with col2:
            difficulty_color = {
                "Easy": "green",
                "Medium": "orange", 
                "Hard": "red"
            }
            difficulty = problem.get('difficulty', 'Medium')
            st.markdown(f"**Difficulty:** :{difficulty_color.get(difficulty, 'blue')}[{difficulty}]")
        with col3:
            if problem.get('topics'):
                st.markdown(f"**Topics:** {', '.join(problem['topics'])}")
        
        # Problem description
        st.markdown("### Problem Description")
        st.markdown(problem.get('description', 'No description available'))
        
        # Examples
        if problem.get('examples'):
            st.markdown("### Examples")
            for i, example in enumerate(problem['examples'], 1):
                with st.expander(f"Example {i}"):
                    st.code(example.get('input', ''), language='text')
                    st.markdown(f"**Output:** `{example.get('output', '')}`")
                    if example.get('explanation'):
                        st.markdown(f"**Explanation:** {example['explanation']}")
        
        # Constraints
        if problem.get('constraints'):
            st.markdown("### Constraints")
            for constraint in problem['constraints']:
                st.markdown(f"• {constraint}")
        
        # Companies
        if problem.get('companies'):
            st.markdown("### 🏢 Asked By")
            companies_str = " • ".join([f"`{company}`" for company in problem['companies']])
            st.markdown(companies_str)
        
        # Patterns
        if problem.get('patterns'):
            st.markdown("### 🔍 Patterns")
            patterns_str = " • ".join([f"`{pattern}`" for pattern in problem['patterns']])
            st.markdown(patterns_str)
    
    def _display_solution_interface(self):
        """Display the solution input interface"""
        st.markdown("### 💻 Your Solution")
        
        # Language selection
        languages = ["Python", "Java", "C++", "JavaScript", "Go", "Rust"]
        selected_language = st.selectbox("Programming Language", languages, index=0)
        
        # Code editor
        try:
            from streamlit_ace import st_ace
            
            user_code = st_ace(
                value=st.session_state.user_solution,
                language=selected_language.lower(),
                theme='monokai',
                key='solution_editor',
                height=300,
                auto_update=False,
                wrap=True,
                annotations=None
            )
            
            if user_code != st.session_state.user_solution:
                st.session_state.user_solution = user_code
        except ImportError:
            # Fallback to text area if ace editor not available
            user_code = st.text_area(
                "Enter your solution:",
                value=st.session_state.user_solution,
                height=300,
                key="solution_textarea"
            )
            st.session_state.user_solution = user_code
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Get Hint", use_container_width=True):
                if st.session_state.user_solution.strip():
                    self._get_hint()
                else:
                    st.warning("Please write some code first to get a hint!")
        
        with col2:
            if st.button("📊 Review Code", use_container_width=True):
                if st.session_state.user_solution.strip():
                    self._review_code(selected_language)
                else:
                    st.warning("Please write some code first for review!")
        
        with col3:
            if st.button("🎯 Generate Variations", use_container_width=True):
                self._generate_variations()
    
    def _get_hint(self):
        """Get a hint for the current problem"""
        with st.spinner("🤔 Analyzing your code and generating hint..."):
            try:
                response = self.api_client.get_progressive_hint(
                    problem_id=st.session_state.current_problem.get('id'),
                    user_code=st.session_state.user_solution,
                    user_id=st.session_state.get('user_id', 'anonymous')
                )
                
                if response:
                    st.info(f"💡 **Hint:** {response.get('hint', 'No hint available')}")
                    
                    if response.get('level'):
                        st.caption(f"Hint Level: {response['level']}")
                else:
                    st.error("Failed to generate hint. Please try again.")
            except Exception as e:
                st.error(f"Error getting hint: {str(e)}")
    
    def _review_code(self, language: str):
        """Review the user's code"""
        with st.spinner("🔎 Reviewing your code..."):
            try:
                response = self.api_client.review_code(
                    code=st.session_state.user_solution,
                    language=language,
                    problem_context=st.session_state.current_problem.get('description', ''),
                    user_id=st.session_state.get('user_id', 'anonymous')
                )
                
                if response:
                    st.success("📊 Code Review Complete!")
                    
                    with st.expander("📋 Review Results", expanded=True):
                        if response.get('correctness'):
                            st.markdown(f"**Correctness:** {response['correctness']}")
                        
                        if response.get('time_complexity'):
                            st.markdown(f"**Time Complexity:** {response['time_complexity']}")
                        
                        if response.get('space_complexity'):
                            st.markdown(f"**Space Complexity:** {response['space_complexity']}")
                        
                        if response.get('suggestions'):
                            st.markdown("**Suggestions:**")
                            for suggestion in response['suggestions']:
                                st.markdown(f"• {suggestion}")
                        
                        if response.get('score'):
                            st.metric("Overall Score", f"{response['score']}/100")
                else:
                    st.error("Failed to review code. Please try again.")
            except Exception as e:
                st.error(f"Error reviewing code: {str(e)}")
    
    def _generate_variations(self):
        """Generate variations of the current problem"""
        with st.spinner("🎲 Generating problem variations..."):
            try:
                response = self.api_client.generate_problem_variations(
                    problem_id=st.session_state.current_problem.get('id'),
                    user_id=st.session_state.get('user_id', 'anonymous')
                )
                
                if response and response.get('variations'):
                    st.session_state.problem_variations = response['variations']
                    st.success(f"✨ Generated {len(response['variations'])} variations!")
                    st.rerun()
                else:
                    st.error("Failed to generate variations. Please try again.")
            except Exception as e:
                st.error(f"Error generating variations: {str(e)}")
    
    def _display_variations(self):
        """Display problem variations"""
        if st.session_state.problem_variations:
            st.markdown("### 🎲 Problem Variations")
            
            for i, variation in enumerate(st.session_state.problem_variations, 1):
                with st.expander(f"Variation {i}: {variation.get('title', 'Untitled')}"):
                    st.markdown(f"**Difficulty:** {variation.get('difficulty', 'Medium')}")
                    st.markdown(variation.get('description', 'No description'))
                    
                    if variation.get('examples'):
                        st.markdown("**Example:**")
                        example = variation['examples'][0]
                        st.code(example.get('input', ''), language='text')
                        st.markdown(f"**Output:** `{example.get('output', '')}`")
                    
                    if st.button(f"Use Variation {i}", key=f"use_variation_{i}"):
                        st.session_state.current_problem = variation
                        st.session_state.user_solution = ""
                        st.session_state.problem_variations = []
                        st.rerun()
    
    def _display_welcome_message(self):
        """Display welcome message when no problem is loaded"""
        st.markdown("""
        ### Welcome to DSA Problem Generator! 🎯
        
        Use the sidebar to customize your problem preferences:
        
        🎚️ **Difficulty Level**: Choose Easy, Medium, or Hard
        📚 **Topics**: Select specific data structures or algorithms
        🔍 **Patterns**: Focus on particular problem-solving patterns
        🏢 **Companies**: Practice problems from specific companies
        
        Click **"Generate New Problem"** to get started!
        
        ### Features Available:
        - 💡 **Smart Hints**: Get progressive hints based on your code
        - 📊 **Code Review**: Receive detailed feedback on your solution
        - 🎲 **Problem Variations**: Generate similar problems for practice
        - 📈 **Progress Tracking**: Monitor your improvement over time
        """)
        
        # Quick start buttons
        st.markdown("### Quick Start")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🟢 Easy Problem", use_container_width=True):
                self._generate_problem("Easy", [], [], [])
        
        with col2:
            if st.button("🟡 Medium Problem", use_container_width=True):
                self._generate_problem("Medium", [], [], [])
        
        with col3:
            if st.button("🔴 Hard Problem", use_container_width=True):
                self._generate_problem("Hard", [], [], [])
