import streamlit as st
import re
from typing import Dict, Any, List

class CodeDebuggerComponent:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def render(self):
        """Render the code debugger interface"""
        st.header("🐛 Code Debugger")
        st.markdown("Debug and fix problematic code with AI assistance")
        
        # Initialize session state
        if 'debug_code' not in st.session_state:
            st.session_state.debug_code = ""
        if 'debug_language' not in st.session_state:
            st.session_state.debug_language = "Python"
        if 'debug_results' not in st.session_state:
            st.session_state.debug_results = None
        
        # Main interface
        self._display_code_input()
        self._display_debug_controls()
        
        if st.session_state.debug_results:
            self._display_debug_results()
    
    def _display_code_input(self):
        """Display code input section"""
        st.markdown("### 💻 Paste Your Code")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Language selection
            languages = ["Python", "Java", "C++", "JavaScript", "C", "Go", "Rust"]
            selected_language = st.selectbox(
                "Programming Language",
                languages,
                index=0,
                key="debug_language_selector"
            )
            st.session_state.debug_language = selected_language
        
        with col2:
            # Quick examples
            if st.button("📝 Load Example"):
                example_code = self._get_example_code(selected_language)
                st.session_state.debug_code = example_code
                st.rerun()
        
        # Code editor
        try:
            from streamlit_ace import st_ace
            
            user_code = st_ace(
                value=st.session_state.debug_code,
                language=selected_language.lower(),
                theme='monokai',
                key='debug_code_editor',
                height=400,
                auto_update=False,
                wrap=True,
                annotations=None
            )
            
            if user_code != st.session_state.debug_code:
                st.session_state.debug_code = user_code
        except ImportError:
            # Fallback to text area
            user_code = st.text_area(
                "Paste your problematic code here:",
                value=st.session_state.debug_code,
                height=400,
                key="debug_code_textarea",
                placeholder="Paste the code that's not working as expected..."
            )
            st.session_state.debug_code = user_code
        
        # Additional context
        st.markdown("### 📋 Additional Context")
        
        col_error, col_expected = st.columns(2)
        
        with col_error:
            error_message = st.text_area(
                "Error Message (if any):",
                height=100,
                placeholder="Paste any error messages or stack traces here...",
                key="debug_error_message"
            )
        
        with col_expected:
            expected_behavior = st.text_area(
                "Expected Behavior:",
                height=100,
                placeholder="Describe what the code should do...",
                key="debug_expected_behavior"
            )
    
    def _display_debug_controls(self):
        """Display debugging control buttons"""
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Analyze Code", use_container_width=True, type="primary"):
                self._analyze_code()
        
        with col2:
            if st.button("🐛 Find Bugs", use_container_width=True):
                self._find_bugs()
        
        with col3:
            if st.button("⚡ Optimize", use_container_width=True):
                self._optimize_code()
        
        with col4:
            if st.button("🧪 Suggest Tests", use_container_width=True):
                self._suggest_tests()
    
    def _analyze_code(self):
        """Analyze the code for general issues"""
        if not st.session_state.debug_code.strip():
            st.warning("Please paste some code to analyze!")
            return
        
        with st.spinner("🔍 Analyzing your code..."):
            try:
                # Use code review API for analysis
                review = self.api_client.review_code(
                    code=st.session_state.debug_code,
                    language=st.session_state.debug_language,
                    focus_areas=["correctness", "efficiency", "style", "bugs"],
                    user_id=st.session_state.get('user_id', 'anonymous')
                )
                
                if review:
                    st.session_state.debug_results = {
                        'type': 'analysis',
                        'data': review
                    }
                    st.rerun()
                else:
                    st.error("Failed to analyze code. Please try again.")
            except Exception as e:
                st.error(f"Error analyzing code: {str(e)}")
    
    def _find_bugs(self):
        """Find potential bugs in the code"""
        if not st.session_state.debug_code.strip():
            st.warning("Please paste some code to debug!")
            return
        
        with st.spinner("🐛 Searching for bugs..."):
            try:
                # Create a specialized prompt for bug finding
                error_context = st.session_state.get('debug_error_message', '')
                expected_context = st.session_state.get('debug_expected_behavior', '')
                
                # Use a simplified approach for now
                bugs = self._detect_common_bugs(st.session_state.debug_code, st.session_state.debug_language)
                
                st.session_state.debug_results = {
                    'type': 'bugs',
                    'data': {
                        'bugs_found': bugs,
                        'error_context': error_context,
                        'expected_context': expected_context
                    }
                }
                st.rerun()
            except Exception as e:
                st.error(f"Error finding bugs: {str(e)}")
    
    def _optimize_code(self):
        """Suggest optimizations for the code"""
        if not st.session_state.debug_code.strip():
            st.warning("Please paste some code to optimize!")
            return
        
        with st.spinner("⚡ Finding optimization opportunities..."):
            try:
                # Use code review API focusing on efficiency
                review = self.api_client.review_code(
                    code=st.session_state.debug_code,
                    language=st.session_state.debug_language,
                    focus_areas=["efficiency", "performance"],
                    user_id=st.session_state.get('user_id', 'anonymous')
                )
                
                if review:
                    st.session_state.debug_results = {
                        'type': 'optimization',
                        'data': review
                    }
                    st.rerun()
                else:
                    st.error("Failed to optimize code. Please try again.")
            except Exception as e:
                st.error(f"Error optimizing code: {str(e)}")
    
    def _suggest_tests(self):
        """Suggest test cases for the code"""
        if not st.session_state.debug_code.strip():
            st.warning("Please paste some code to create tests for!")
            return
        
        with st.spinner("🧪 Generating test suggestions..."):
            try:
                # Generate test case suggestions
                tests = self._generate_test_suggestions(st.session_state.debug_code, st.session_state.debug_language)
                
                st.session_state.debug_results = {
                    'type': 'tests',
                    'data': {'test_suggestions': tests}
                }
                st.rerun()
            except Exception as e:
                st.error(f"Error generating tests: {str(e)}")
    
    def _display_debug_results(self):
        """Display debugging results"""
        results = st.session_state.debug_results
        result_type = results['type']
        data = results['data']
        
        st.markdown("---")
        st.markdown("### 📊 Debug Results")
        
        if result_type == 'analysis':
            self._display_analysis_results(data)
        elif result_type == 'bugs':
            self._display_bug_results(data)
        elif result_type == 'optimization':
            self._display_optimization_results(data)
        elif result_type == 'tests':
            self._display_test_results(data)
    
    def _display_analysis_results(self, data: Dict):
        """Display code analysis results"""
        st.markdown("#### 🔍 Code Analysis")
        
        if data.get('overall_analysis'):
            analysis = data['overall_analysis']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Overall Assessment:**")
                st.info(analysis.get('summary', 'Code analysis completed'))
                
                if analysis.get('time_complexity'):
                    st.markdown(f"**Time Complexity:** `{analysis['time_complexity']}`")
                if analysis.get('space_complexity'):
                    st.markdown(f"**Space Complexity:** `{analysis['space_complexity']}`")
            
            with col2:
                if analysis.get('strengths'):
                    st.markdown("**✅ Strengths:**")
                    for strength in analysis['strengths'][:3]:
                        st.markdown(f"- {strength}")
        
        # Display issues
        if data.get('issues'):
            st.markdown("**🐛 Issues Found:**")
            for i, issue in enumerate(data['issues'][:5], 1):
                with st.expander(f"Issue {i}: {issue.get('type', 'Code Issue')}"):
                    st.markdown(f"**Description:** {issue.get('description', 'Issue found')}")
                    if issue.get('suggestion'):
                        st.markdown(f"**Suggestion:** {issue['suggestion']}")
                    if issue.get('line_number'):
                        st.markdown(f"**Line:** {issue['line_number']}")
    
    def _display_bug_results(self, data: Dict):
        """Display bug detection results"""
        st.markdown("#### 🐛 Bug Detection")
        
        bugs = data.get('bugs_found', [])
        
        if bugs:
            for i, bug in enumerate(bugs, 1):
                with st.expander(f"🐛 Bug {i}: {bug['type']}"):
                    st.markdown(f"**Description:** {bug['description']}")
                    st.markdown(f"**Severity:** {bug.get('severity', 'Medium')}")
                    if bug.get('line'):
                        st.markdown(f"**Line:** {bug['line']}")
                    if bug.get('suggestion'):
                        st.markdown(f"**Fix Suggestion:** {bug['suggestion']}")
        else:
            st.success("✅ No obvious bugs detected! Your code looks good.")
            st.info("💡 If you're still experiencing issues, try the 'Analyze Code' feature for a deeper analysis.")
    
    def _display_optimization_results(self, data: Dict):
        """Display optimization suggestions"""
        st.markdown("#### ⚡ Optimization Suggestions")
        
        if data.get('optimizations'):
            for i, opt in enumerate(data['optimizations'][:3], 1):
                with st.expander(f"⚡ Optimization {i}: {opt.get('type', 'Performance Improvement')}"):
                    st.markdown(f"**Description:** {opt.get('description', 'Optimization opportunity')}")
                    if opt.get('impact'):
                        st.markdown(f"**Expected Impact:** {opt['impact']}")
                    if opt.get('suggestion'):
                        st.markdown(f"**Implementation:** {opt['suggestion']}")
        else:
            st.info("💡 Your code is already well-optimized!")
    
    def _display_test_results(self, data: Dict):
        """Display test suggestions"""
        st.markdown("#### 🧪 Test Case Suggestions")
        
        tests = data.get('test_suggestions', [])
        
        for i, test in enumerate(tests, 1):
            with st.expander(f"Test Case {i}: {test['name']}"):
                st.markdown(f"**Purpose:** {test['description']}")
                st.code(test['code'], language=st.session_state.debug_language.lower())
    
    def _detect_common_bugs(self, code: str, language: str) -> List[Dict]:
        """Detect common programming bugs"""
        bugs = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Common Python bugs
            if language.lower() == 'python':
                # Off-by-one errors
                if 'range(' in line and ')' in line:
                    if 'len(' in line and '+1' not in line and '-1' not in line:
                        bugs.append({
                            'type': 'Potential Off-by-One Error',
                            'description': 'Using len() in range might cause index out of bounds',
                            'line': i,
                            'severity': 'Medium',
                            'suggestion': 'Consider using range(len(array)) carefully or range(len(array)-1) if needed'
                        })
                
                # Mutable default arguments
                if 'def ' in line and '[]' in line:
                    bugs.append({
                        'type': 'Mutable Default Argument',
                        'description': 'Using mutable object as default argument can cause unexpected behavior',
                        'line': i,
                        'severity': 'High',
                        'suggestion': 'Use None as default and create the list inside the function'
                    })
                
                # Unreachable code after return
                if line_stripped.startswith('return') and i < len(lines):
                    next_line = lines[i].strip() if i < len(lines) else ''
                    if next_line and not next_line.startswith(('#', 'def ', 'class ', 'if ', 'else', 'elif')):
                        bugs.append({
                            'type': 'Unreachable Code',
                            'description': 'Code after return statement will never execute',
                            'line': i + 1,
                            'severity': 'Medium',
                            'suggestion': 'Remove unreachable code or restructure the logic'
                        })
            
            # Common logic errors for all languages
            if '=' in line and '==' not in line and '!=' not in line:
                if any(keyword in line for keyword in ['if ', 'while ', 'elif ']):
                    bugs.append({
                        'type': 'Assignment in Condition',
                        'description': 'Using assignment (=) instead of comparison (==) in condition',
                        'line': i,
                        'severity': 'High',
                        'suggestion': 'Use == for comparison or != for not equal'
                    })
        
        # If no specific bugs found, add general suggestions
        if not bugs:
            bugs.append({
                'type': 'General Check',
                'description': 'No obvious bugs detected, but consider edge cases',
                'line': 0,
                'severity': 'Low',
                'suggestion': 'Test with empty inputs, null values, and boundary conditions'
            })
        
        return bugs
    
    def _generate_test_suggestions(self, code: str, language: str) -> List[Dict]:
        """Generate test case suggestions"""
        tests = []
        
        # Basic test suggestions based on code analysis
        if 'def ' in code:  # Function detected
            tests.append({
                'name': 'Normal Case Test',
                'description': 'Test with typical valid inputs',
                'code': '# Test with normal, expected inputs\n# Example: assert function_name(input) == expected_output'
            })
            
            tests.append({
                'name': 'Edge Case Test',
                'description': 'Test with boundary conditions',
                'code': '# Test edge cases like empty inputs, single elements, etc.\n# Example: assert function_name([]) == expected_for_empty'
            })
            
            tests.append({
                'name': 'Error Case Test',
                'description': 'Test with invalid inputs',
                'code': '# Test error handling\n# Example: with pytest.raises(ValueError): function_name(invalid_input)'
            })
        
        if 'class ' in code:  # Class detected
            tests.append({
                'name': 'Object Creation Test',
                'description': 'Test object instantiation',
                'code': '# Test creating an instance of the class\n# obj = ClassName(params)\n# assert obj.property == expected'
            })
        
        return tests
    
    def _get_example_code(self, language: str) -> str:
        """Get example buggy code for demonstration"""
        examples = {
            'Python': '''def find_max(numbers):
    max_num = 0  # Bug: assumes all numbers are positive
    for i in range(len(numbers) + 1):  # Bug: off-by-one error
        if numbers[i] > max_num:
            max_num = numbers[i]
    return max_num

# Test case that might fail
result = find_max([-5, -2, -10])  # Should return -2, not 0
print(result)''',
            
            'Java': '''public class Calculator {
    public int divide(int a, int b) {
        return a / b;  // Bug: no check for division by zero
    }
    
    public boolean isEven(int n) {
        if (n % 2 = 0) {  // Bug: assignment instead of comparison
            return true;
        }
        return false;
    }
}''',
            
            'JavaScript': '''function processArray(arr) {
    for (var i = 0; i < arr.length; i++) {
        setTimeout(function() {
            console.log(arr[i]);  // Bug: closure issue with var
        }, 100);
    }
}

// Bug: will print undefined multiple times
processArray([1, 2, 3, 4, 5]);'''
        }
        
        return examples.get(language, '''// Paste your problematic code here
// The debugger will help you find and fix issues''')
