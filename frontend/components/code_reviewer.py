import streamlit as st
from typing import Dict, Any, Optional

class CodeReviewerComponent:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def render(self):
        """Render the code reviewer interface"""
        st.header("📊 Code Reviewer")
        st.markdown("Get detailed feedback on your code including correctness, complexity, and optimization suggestions")
        
        # Initialize session state
        if 'review_code' not in st.session_state:
            st.session_state.review_code = ""
        if 'review_results' not in st.session_state:
            st.session_state.review_results = None
        if 'review_history' not in st.session_state:
            st.session_state.review_history = []
        
        # Code input section
        self._display_code_input()
        
        # Review configuration
        self._display_review_configuration()
        
        # Review results
        if st.session_state.review_results:
            self._display_review_results()
        
        # Review history
        self._display_review_history()
    
    def _display_code_input(self):
        """Display the code input section"""
        st.markdown("### 💻 Code to Review")
        
        # Check if there's code from hint system
        if st.session_state.get('user_code') and not st.session_state.review_code:
            if st.button("📥 Import code from Hint System"):
                st.session_state.review_code = st.session_state.user_code
                st.rerun()
          # Language selection
        languages = ["Python", "Java", "C++", "JavaScript", "TypeScript", "Go", "Rust", "C#"]
        selected_language = st.selectbox(
            "Programming Language",
            languages,
            index=0,
            key="review_language_selector"
        )
        
        # Store in session state for use in other methods
        st.session_state.selected_language = selected_language
        
        # Code editor
        try:
            from streamlit_ace import st_ace
            
            user_code = st_ace(
                value=st.session_state.review_code,
                language=selected_language.lower(),
                theme='github',
                key='review_code_editor',
                height=400,
                auto_update=False,
                wrap=True,
                font_size=14,
                show_gutter=True,
                show_print_margin=True,
                annotations=None
            )
            
            if user_code != st.session_state.review_code:
                st.session_state.review_code = user_code
        except ImportError:
            # Fallback to text area if ace editor not available
            user_code = st.text_area(
                "Paste your code here:",
                value=st.session_state.review_code,
                height=400,
                key="review_code_textarea",
                placeholder="Paste your solution here for detailed review..."
            )
            st.session_state.review_code = user_code
        
        # Code statistics
        if st.session_state.review_code:
            lines = len(st.session_state.review_code.split('\n'))
            chars = len(st.session_state.review_code)
            words = len(st.session_state.review_code.split())
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Lines", lines)
            with col2:
                st.metric("Characters", chars)
            with col3:
                st.metric("Words", words)
            with col4:
                # Estimate complexity based on keywords
                complexity_keywords = ['for', 'while', 'if', 'def', 'class', 'function']
                complexity_count = sum(st.session_state.review_code.lower().count(keyword) for keyword in complexity_keywords)
                st.metric("Complexity Score", complexity_count)
    
    def _display_review_configuration(self):
        """Display review configuration options"""
        st.markdown("### ⚙️ Review Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Review focus areas
            focus_areas = st.multiselect(
                "Focus Areas",
                [
                    "Correctness",
                    "Time Complexity", 
                    "Space Complexity",
                    "Code Style",
                    "Best Practices",
                    "Security",
                    "Performance",
                    "Readability"
                ],
                default=["Correctness", "Time Complexity", "Space Complexity"],
                help="Select specific areas to focus the review on"
            )
        
        with col2:
            # Review depth
            review_depth = st.selectbox(
                "Review Depth",
                ["Quick Scan", "Standard Review", "Deep Analysis"],
                index=1,
                help="Choose how detailed the review should be"
            )
            
            # Include suggestions
            include_suggestions = st.checkbox(
                "Include Optimization Suggestions",
                value=True,
                help="Get specific suggestions for improving your code"
            )
        
        # Problem context (optional)
        with st.expander("🎯 Problem Context (Optional)"):
            st.markdown("Providing problem context helps generate more accurate feedback")
            
            problem_description = ""
            if st.session_state.get('current_problem'):
                problem_description = st.session_state.current_problem.get('description', '')
                st.info("✅ Problem context loaded from current session")
            
            problem_context = st.text_area(
                "Problem Description",
                value=problem_description,
                height=100,
                placeholder="Describe the problem your code is solving...",
                help="This helps the reviewer understand the intended functionality"
            )
        
        # Review button
        review_disabled = not st.session_state.review_code.strip()
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        
        with col_btn2:
            if st.button(
                "🔍 Review Code",
                type="primary",
                disabled=review_disabled,
                use_container_width=True,
                help="Analyze your code and get detailed feedback" if not review_disabled else "Please enter some code first"
            ):                self._perform_code_review(
                    st.session_state.review_code,
                    st.session_state.get('selected_language', 'Python'),
                    focus_areas,
                    review_depth,
                    include_suggestions,
                    problem_context
                )
    
    def _perform_code_review(self, code: str, language: str, focus_areas: list, 
                           review_depth: str, include_suggestions: bool, problem_context: str):
        """Perform the code review using the API"""
        with st.spinner("🔎 Analyzing your code... This may take a moment"):
            try:
                response = self.api_client.review_code(
                    code=code,
                    language=language,
                    focus_areas=focus_areas,
                    review_depth=review_depth,
                    include_suggestions=include_suggestions,
                    problem_context=problem_context,
                    user_id=st.session_state.get('user_id', 'anonymous')
                )
                
                if response:
                    st.session_state.review_results = response
                    
                    # Add to history
                    review_entry = {
                        'timestamp': response.get('timestamp'),
                        'language': language,
                        'code_length': len(code),
                        'score': response.get('overall_score', 0),
                        'focus_areas': focus_areas
                    }
                    st.session_state.review_history.append(review_entry)
                    
                    st.success("✅ Code review completed!")
                    st.rerun()
                else:
                    st.error("❌ Failed to analyze code. Please try again.")
            
            except Exception as e:
                st.error(f"❌ Error during code review: {str(e)}")
    
    def _display_review_results(self):
        """Display the code review results"""
        results = st.session_state.review_results
        
        st.markdown("### 📋 Review Results")
        
        # Overall score and summary
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            score = results.get('overall_score', 0)
            score_color = "green" if score >= 80 else "orange" if score >= 60 else "red"
            st.metric(
                "Overall Score",
                f"{score}/100",
                delta=None,
                help="Composite score based on all review criteria"
            )
        
        with col2:
            st.markdown("#### 📝 Summary")
            summary = results.get('summary', 'No summary available')
            st.info(summary)
        
        with col3:
            # Code grade
            if score >= 90:
                grade = "A+"
            elif score >= 80:
                grade = "A"
            elif score >= 70:
                grade = "B"
            elif score >= 60:
                grade = "C"
            else:
                grade = "D"
            
            st.metric("Grade", grade)
        
        # Detailed analysis
        st.markdown("#### 🔍 Detailed Analysis")
        
        # Correctness
        if results.get('correctness'):
            with st.expander("✅ Correctness Analysis", expanded=True):
                correctness = results['correctness']
                
                if correctness.get('is_correct'):
                    st.success("✅ Code appears to be functionally correct")
                else:
                    st.error("❌ Potential correctness issues detected")
                
                if correctness.get('issues'):
                    st.markdown("**Issues Found:**")
                    for issue in correctness['issues']:
                        st.markdown(f"• {issue}")
                
                if correctness.get('test_cases'):
                    st.markdown("**Test Case Analysis:**")
                    for test in correctness['test_cases']:
                        status = "✅" if test.get('passed') else "❌"
                        st.markdown(f"{status} {test.get('description', 'Test case')}")
        
        # Complexity Analysis
        if results.get('complexity'):
            with st.expander("⏱️ Complexity Analysis"):
                complexity = results['complexity']
                
                col_time, col_space = st.columns(2)
                
                with col_time:
                    st.markdown("**Time Complexity**")
                    time_comp = complexity.get('time_complexity', 'Unknown')
                    st.code(time_comp, language=None)
                    
                    if complexity.get('time_explanation'):
                        st.caption(complexity['time_explanation'])
                
                with col_space:
                    st.markdown("**Space Complexity**")
                    space_comp = complexity.get('space_complexity', 'Unknown')
                    st.code(space_comp, language=None)
                    
                    if complexity.get('space_explanation'):
                        st.caption(complexity['space_explanation'])
        
        # Code Quality
        if results.get('code_quality'):
            with st.expander("📏 Code Quality"):
                quality = results['code_quality']
                
                # Quality metrics
                metrics = quality.get('metrics', {})
                if metrics:
                    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
                    
                    with col_q1:
                        st.metric("Readability", f"{metrics.get('readability', 0)}/10")
                    with col_q2:
                        st.metric("Maintainability", f"{metrics.get('maintainability', 0)}/10")
                    with col_q3:
                        st.metric("Performance", f"{metrics.get('performance', 0)}/10")
                    with col_q4:
                        st.metric("Style", f"{metrics.get('style', 0)}/10")
                
                # Quality issues
                if quality.get('issues'):
                    st.markdown("**Code Quality Issues:**")
                    for issue in quality['issues']:
                        severity = issue.get('severity', 'info')
                        icon = "🔴" if severity == "error" else "🟡" if severity == "warning" else "🔵"
                        st.markdown(f"{icon} **{issue.get('type', 'Issue')}**: {issue.get('message', '')}")
                        
                        if issue.get('line'):
                            st.caption(f"Line {issue['line']}")
        
        # Suggestions
        if results.get('suggestions'):
            with st.expander("💡 Optimization Suggestions", expanded=True):
                suggestions = results['suggestions']
                
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"**{i}. {suggestion.get('title', 'Suggestion')}**")
                    st.markdown(suggestion.get('description', ''))
                    
                    if suggestion.get('code_example'):
                        st.markdown("*Example:*")
                        st.code(suggestion['code_example'], language='python')
                    
                    if suggestion.get('impact'):
                        impact = suggestion['impact']
                        impact_color = "green" if impact == "High" else "orange" if impact == "Medium" else "blue"
                        st.markdown(f"**Impact:** :{impact_color}[{impact}]")
                    
                    st.divider()
        
        # Security Analysis (if applicable)
        if results.get('security'):
            with st.expander("🔒 Security Analysis"):
                security = results['security']
                
                if security.get('vulnerabilities'):
                    st.warning("⚠️ Potential security issues found")
                    for vuln in security['vulnerabilities']:
                        st.markdown(f"• **{vuln.get('type', 'Issue')}**: {vuln.get('description', '')}")
                        if vuln.get('severity'):
                            st.caption(f"Severity: {vuln['severity']}")
                else:
                    st.success("✅ No obvious security issues detected")
        
        # Action buttons
        st.markdown("#### 🎯 Next Steps")
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("📥 Export Report", use_container_width=True):
                self._export_review_report()
        
        with col_action2:
            if st.button("🔄 Review Again", use_container_width=True):
                st.session_state.review_results = None
                st.rerun()
        
        with col_action3:
            if st.button("💾 Save to History", use_container_width=True):
                st.success("✅ Review saved to history")
    
    def _display_review_history(self):
        """Display review history"""
        if not st.session_state.review_history:
            return
        
        st.markdown("### 📊 Review History")
        
        # Summary stats
        total_reviews = len(st.session_state.review_history)
        avg_score = sum(r.get('score', 0) for r in st.session_state.review_history) / total_reviews
        
        col_hist1, col_hist2, col_hist3 = st.columns(3)
        
        with col_hist1:
            st.metric("Total Reviews", total_reviews)
        with col_hist2:
            st.metric("Average Score", f"{avg_score:.1f}/100")
        with col_hist3:
            latest_score = st.session_state.review_history[-1].get('score', 0)
            if len(st.session_state.review_history) > 1:
                prev_score = st.session_state.review_history[-2].get('score', 0)
                delta = latest_score - prev_score
            else:
                delta = None
            st.metric("Latest Score", f"{latest_score}/100", delta=delta)
        
        # History table
        with st.expander("📋 Review History Details"):
            for i, review in enumerate(reversed(st.session_state.review_history), 1):
                col_r1, col_r2, col_r3, col_r4 = st.columns([1, 2, 1, 1])
                
                with col_r1:
                    st.markdown(f"**#{len(st.session_state.review_history) - i + 1}**")
                
                with col_r2:
                    timestamp = review.get('timestamp', 'Unknown')
                    st.markdown(f"*{timestamp}*")
                
                with col_r3:
                    st.markdown(f"**Score:** {review.get('score', 0)}/100")
                
                with col_r4:
                    st.markdown(f"**Language:** {review.get('language', 'Unknown')}")
                
                st.divider()
    
    def _export_review_report(self):
        """Export the review report"""
        results = st.session_state.review_results
        
        report = f"""
# Code Review Report

## Overall Score: {results.get('overall_score', 0)}/100

## Summary
{results.get('summary', 'No summary available')}

## Correctness
{results.get('correctness', {}).get('is_correct', 'Unknown')}

## Complexity Analysis
- **Time Complexity:** {results.get('complexity', {}).get('time_complexity', 'Unknown')}
- **Space Complexity:** {results.get('complexity', {}).get('space_complexity', 'Unknown')}

## Suggestions
"""
        
        if results.get('suggestions'):
            for i, suggestion in enumerate(results['suggestions'], 1):
                report += f"\n{i}. {suggestion.get('title', 'Suggestion')}\n"
                report += f"   {suggestion.get('description', '')}\n"
        
        st.download_button(
            label="📄 Download Report",
            data=report,
            file_name="code_review_report.md",
            mime="text/markdown"
        )
