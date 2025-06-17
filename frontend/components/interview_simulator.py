import streamlit as st
from datetime import datetime
from typing import Dict, Any, List

class InterviewSimulatorComponent:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def render(self):
        """Render the interview simulator interface"""
        st.header("🎤 Interview Simulator")
        st.markdown("Practice technical interviews with AI-powered mock interviews")
        
        # Initialize session state
        if 'interview_session' not in st.session_state:
            st.session_state.interview_session = None
        if 'interview_history' not in st.session_state:
            st.session_state.interview_history = []
        
        # Main interface
        if not st.session_state.interview_session:
            self._display_interview_setup()
        else:
            self._display_active_interview()
    
    def _display_interview_setup(self):
        """Display interview setup interface"""
        st.markdown("### 🚀 Start New Interview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Interview Configuration")
            
            # Company selection
            companies = [
                "Google", "Amazon", "Microsoft", "Apple", "Facebook/Meta",
                "Netflix", "Uber", "Airbnb", "LinkedIn", "Twitter", "Generic Tech Company"
            ]
            selected_company = st.selectbox("Target Company", companies, index=10)
            
            # Difficulty level
            difficulty = st.selectbox(
                "Difficulty Level",
                ["Entry Level", "Mid Level", "Senior Level", "Staff/Principal"],
                index=1
            )
            
            # Interview type
            interview_type = st.selectbox(
                "Interview Type",
                ["Coding Round", "System Design", "Behavioral", "Mixed"],
                index=0
            )
            
            # Duration
            duration = st.selectbox(
                "Interview Duration",
                ["30 minutes", "45 minutes", "60 minutes", "90 minutes"],
                index=2
            )
        
        with col2:
            st.markdown("#### Focus Areas")
            
            # Topics selection
            topics = [
                "Arrays & Strings", "Linked Lists", "Trees & Graphs",
                "Dynamic Programming", "Sorting & Searching", "Hash Tables",
                "Stack & Queue", "Recursion", "Greedy Algorithms", "Two Pointers"
            ]
            selected_topics = st.multiselect("Select Topics", topics, default=topics[:3])
            
            # Additional preferences
            include_followup = st.checkbox("Include follow-up questions", value=True)
            include_hints = st.checkbox("Allow hints during interview", value=True)
            realistic_pressure = st.checkbox("Simulate time pressure", value=False)
        
        # Start interview button
        st.markdown("---")
        col_start, col_history = st.columns(2)
        
        with col_start:
            if st.button("🎯 Start Interview", use_container_width=True, type="primary"):
                self._start_interview(
                    company=selected_company,
                    difficulty=difficulty,
                    interview_type=interview_type,
                    duration=duration,
                    topics=selected_topics,
                    include_followup=include_followup,
                    include_hints=include_hints,
                    realistic_pressure=realistic_pressure
                )
        
        with col_history:
            if st.button("📜 View Interview History", use_container_width=True):
                self._display_interview_history()
    
    def _start_interview(self, **config):
        """Start a new interview session"""
        # Create interview session
        session = {
            'id': f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'config': config,
            'start_time': datetime.now(),
            'current_question': 0,
            'questions': [],
            'responses': [],
            'status': 'active'
        }
        
        # Generate first question
        with st.spinner("🤖 Preparing your interview questions..."):
            try:
                # Use the problem generator to create interview questions
                question = self.api_client.generate_problem(
                    user_id=st.session_state.get('user_id', 'anonymous'),
                    difficulty=config['difficulty'],
                    topics=config['topics']
                )
                
                if question:
                    # Format as interview question
                    interview_question = {
                        'id': 1,
                        'title': question.get('title', 'Interview Question 1'),
                        'statement': question.get('statement', question.get('description', '')),
                        'difficulty': question.get('difficulty', config['difficulty']),
                        'examples': question.get('examples', []),
                        'constraints': question.get('constraints', []),
                        'follow_ups': []
                    }
                    session['questions'] = [interview_question]
                    st.session_state.interview_session = session
                    st.success("✨ Interview started! Good luck!")
                    st.rerun()
                else:
                    st.error("Failed to generate interview question. Please try again.")
            except Exception as e:
                st.error(f"Error starting interview: {str(e)}")
    
    def _display_active_interview(self):
        """Display active interview interface"""
        session = st.session_state.interview_session
        config = session['config']
        
        # Interview header
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"### 🏢 {config['company']} - {config['interview_type']}")
        
        with col2:
            # Timer (simplified)
            elapsed = datetime.now() - session['start_time']
            st.metric("Time Elapsed", f"{elapsed.seconds // 60}m {elapsed.seconds % 60}s")
        
        with col3:
            if st.button("❌ End Interview", type="secondary"):
                self._end_interview()
                return
        
        # Current question
        if session['questions']:
            current_q = session['questions'][session['current_question']]
            
            st.markdown("---")
            st.markdown(f"### Question {session['current_question'] + 1}: {current_q['title']}")
            st.markdown(current_q['statement'])
            
            # Examples
            if current_q.get('examples'):
                st.markdown("**Examples:**")
                for i, example in enumerate(current_q['examples'], 1):
                    with st.expander(f"Example {i}"):
                        st.code(f"Input: {example.get('input', '')}")
                        st.code(f"Output: {example.get('output', '')}")
                        if example.get('explanation'):
                            st.markdown(f"**Explanation:** {example['explanation']}")
            
            # Constraints
            if current_q.get('constraints'):
                st.markdown("**Constraints:**")
                for constraint in current_q['constraints']:
                    st.markdown(f"- {constraint}")
            
            # Solution area
            st.markdown("### 💻 Your Solution")
            
            # Language selection
            language = st.selectbox(
                "Programming Language",
                ["Python", "Java", "C++", "JavaScript", "Go"],
                key="interview_language"
            )
            
            # Code editor
            solution_code = st.text_area(
                "Write your solution:",
                height=400,
                placeholder="Start coding your solution here...",
                key="interview_solution"
            )
            
            # Action buttons
            col_submit, col_hint, col_next = st.columns(3)
            
            with col_submit:
                if st.button("✅ Submit Solution", use_container_width=True):
                    self._submit_solution(solution_code, language)
            
            with col_hint:
                if config.get('include_hints') and st.button("💡 Request Hint", use_container_width=True):
                    self._request_interview_hint(current_q, solution_code)
            
            with col_next:
                if st.button("⏭️ Next Question", use_container_width=True):
                    self._next_question()
    
    def _submit_solution(self, code: str, language: str):
        """Submit solution for review"""
        if not code.strip():
            st.warning("Please write some code before submitting!")
            return
        
        with st.spinner("🔍 Reviewing your solution..."):
            try:
                # Use code review API
                review = self.api_client.review_code(
                    code=code,
                    language=language,
                    focus_areas=["correctness", "efficiency", "clarity"],
                    user_id=st.session_state.get('user_id', 'anonymous')
                )
                
                if review:
                    st.success("✅ Solution submitted!")
                    
                    # Display feedback
                    with st.expander("📊 Interview Feedback", expanded=True):
                        if review.get('overall_analysis'):
                            analysis = review['overall_analysis']
                            st.markdown(f"**Overall Assessment:** {analysis.get('summary', 'Good solution')}")
                            if analysis.get('time_complexity'):
                                st.markdown(f"**Time Complexity:** {analysis['time_complexity']}")
                            if analysis.get('space_complexity'):
                                st.markdown(f"**Space Complexity:** {analysis['space_complexity']}")
                        
                        # Show issues if any
                        if review.get('issues'):
                            st.markdown("**Areas for Improvement:**")
                            for issue in review['issues'][:3]:  # Limit to top 3
                                st.markdown(f"- {issue.get('description', 'Code issue found')}")
                else:
                    st.error("Failed to review solution. Please try again.")
            except Exception as e:
                st.error(f"Error reviewing solution: {str(e)}")
    
    def _request_interview_hint(self, question: Dict, current_code: str):
        """Request a hint during interview"""
        try:
            hint = self.api_client.get_progressive_hint(
                user_code=current_code,
                user_id=st.session_state.get('user_id', 'anonymous')
            )
            
            if hint:
                st.info(f"💡 **Hint:** {hint.get('hint', 'Try breaking down the problem into smaller steps.')}")
            else:
                st.info("💡 **Hint:** Consider the time and space complexity of your approach. Can you optimize it?")
        except Exception as e:
            st.info("💡 **Hint:** Think about edge cases and try to trace through your algorithm step by step.")
    
    def _next_question(self):
        """Move to next question or generate new one"""
        session = st.session_state.interview_session
        session['current_question'] += 1
        
        # If we need more questions, generate them
        if session['current_question'] >= len(session['questions']):
            # Generate next question
            with st.spinner("🤖 Preparing next question..."):
                try:
                    question = self.api_client.generate_problem(
                        user_id=st.session_state.get('user_id', 'anonymous'),
                        difficulty=session['config']['difficulty'],
                        topics=session['config']['topics']
                    )
                    
                    if question:
                        interview_question = {
                            'id': len(session['questions']) + 1,
                            'title': question.get('title', f'Interview Question {len(session["questions"]) + 1}'),
                            'statement': question.get('statement', question.get('description', '')),
                            'difficulty': question.get('difficulty', session['config']['difficulty']),
                            'examples': question.get('examples', []),
                            'constraints': question.get('constraints', [])
                        }
                        session['questions'].append(interview_question)
                        st.success("✨ Next question ready!")
                    else:
                        st.warning("Could not generate next question. Interview will continue with current questions.")
                        if session['current_question'] >= len(session['questions']):
                            self._end_interview()
                            return
                except Exception as e:
                    st.error(f"Error generating next question: {str(e)}")
                    if session['current_question'] >= len(session['questions']):
                        self._end_interview()
                        return
        
        st.rerun()
    
    def _end_interview(self):
        """End the current interview session"""
        session = st.session_state.interview_session
        session['end_time'] = datetime.now()
        session['status'] = 'completed'
        
        # Add to history
        st.session_state.interview_history.append(session)
        st.session_state.interview_session = None
        
        st.success("🎉 Interview completed! Thank you for practicing.")
        st.balloons()
        st.rerun()
    
    def _display_interview_history(self):
        """Display past interview sessions"""
        if not st.session_state.interview_history:
            st.info("📜 No interview history yet. Complete some interviews to see your progress!")
            return
        
        st.markdown("### 📜 Interview History")
        
        for i, session in enumerate(reversed(st.session_state.interview_history)):
            config = session['config']
            duration = session.get('end_time', datetime.now()) - session['start_time']
            
            with st.expander(f"🏢 {config['company']} - {session['start_time'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Type:** {config['interview_type']}")
                    st.markdown(f"**Difficulty:** {config['difficulty']}")
                    st.markdown(f"**Duration:** {duration.seconds // 60} minutes")
                
                with col2:
                    st.markdown(f"**Topics:** {', '.join(config['topics'][:3])}...")
                    st.markdown(f"**Questions:** {len(session['questions'])}")
                    st.markdown(f"**Status:** {session['status'].title()}")
