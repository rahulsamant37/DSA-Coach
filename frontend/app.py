import streamlit as st
import os
from frontend.api_client import api_client
from frontend.components.problem_generator import ProblemGeneratorComponent
from frontend.components.hint_system import HintSystemComponent
from frontend.components.code_reviewer import CodeReviewerComponent
from frontend.components.progress_tracker import ProgressTrackerComponent
from shared.config import DEFAULT_USER_ID, setup_logging
from shared.models import UserProfile, SkillLevel, TargetGoal

# Setup logging
logger = setup_logging()

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = DEFAULT_USER_ID
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'current_problem' not in st.session_state:
        st.session_state.current_problem = None
    if 'hint_level' not in st.session_state:
        st.session_state.hint_level = 0
    if 'api_connected' not in st.session_state:
        st.session_state.api_connected = False

def check_api_connection():
    """Check if API is connected and working"""
    try:
        if api_client.health_check():
            st.session_state.api_connected = True
            return True
        else:
            st.session_state.api_connected = False
            return False
    except Exception as e:
        logger.error(f"API connection check failed: {str(e)}")
        st.session_state.api_connected = False
        return False

def render_api_status():
    """Render API connection status"""
    if not st.session_state.api_connected:
        st.error("⚠️ Backend API is not connected. Please ensure the API server is running on port 8000.")
        st.info("To start the backend server, run: `uvicorn backend.main:app --reload`")
        
        if st.button("🔄 Retry Connection"):
            if check_api_connection():
                st.success("✅ Connected to backend API!")
                st.rerun()
        return False
    return True

def render_sidebar():
    """Render sidebar with navigation and settings"""
    with st.sidebar:
        st.markdown("### 🚀 Navigation")
        
        # Feature selection
        feature_options = {
            "🎯 Problem Generator": "Create practice problems",
            "💡 Hint System": "Get progressive hints",
            "📝 Code Review": "Analyze and improve code",
            "📊 Progress Tracker": "Track learning journey",
            "🎤 Interview Simulator": "Practice mock interviews (Coming Soon)",
            "🐛 Code Debugger": "Debug problematic code (Coming Soon)",
            "🏛️ Memory Palace": "Create memory aids (Coming Soon)"
        }
        
        page = st.selectbox(
            "Choose a feature:",
            options=list(feature_options.keys()),
            format_func=lambda x: x,
            help="Select a feature to get started"
        )
        
        # Show feature description
        st.markdown(f"*{feature_options[page]}*")
        
        st.divider()
        
        # API Status
        st.markdown("### ⚙️ System Status")
        
        if st.session_state.api_connected:
            st.success("✅ API Connected")
            
            # Get API status
            try:
                status = api_client.get_api_status()
                if status and status.get("data"):
                    data = status["data"]
                    gemini_status = "✅ Connected" if data.get("gemini_connected") else "❌ Not configured"
                    st.markdown(f"**Gemini AI:** {gemini_status}")
            except Exception as e:
                logger.warning(f"Could not get detailed API status: {str(e)}")
        else:
            st.error("❌ API Disconnected")
        
        st.divider()
        
        # User Profile
        render_user_profile_sidebar()
        
        return page

def render_user_profile_sidebar():
    """Render user profile section in sidebar"""
    st.markdown("### 👤 User Profile")
    
    try:
        # Load existing profile
        existing_profile = api_client.get_user_profile(st.session_state.user_id)
        
        if existing_profile:
            st.success(f"**Level:** {existing_profile.skill_level.value}")
            st.info(f"**Goal:** {existing_profile.target_goal.value}")
            st.info(f"**Daily Target:** {existing_profile.daily_goal} problems")
        
        # Profile update form
        with st.expander("✏️ Update Profile", expanded=not existing_profile):
            with st.form("profile_form"):
                skill_level = st.selectbox(
                    "Skill Level",
                    options=[level.value for level in SkillLevel],
                    index=1 if not existing_profile else [level.value for level in SkillLevel].index(existing_profile.skill_level.value)
                )
                
                target_goal = st.selectbox(
                    "Target Goal",
                    options=[goal.value for goal in TargetGoal],
                    index=0 if not existing_profile else [goal.value for goal in TargetGoal].index(existing_profile.target_goal.value)
                )
                
                daily_goal = st.slider(
                    "Daily Problem Goal",
                    min_value=1,
                    max_value=20,
                    value=3 if not existing_profile else existing_profile.daily_goal
                )
                
                if st.form_submit_button("💾 Save Profile"):
                    profile = UserProfile(
                        skill_level=SkillLevel(skill_level),
                        target_goal=TargetGoal(target_goal),
                        daily_goal=daily_goal
                    )
                    
                    if api_client.update_user_profile(st.session_state.user_id, profile):
                        st.success("Profile updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update profile")
    
    except Exception as e:
        logger.error(f"Error in user profile sidebar: {str(e)}")
        st.error("Could not load user profile")

def render_welcome_section():
    """Render welcome section for new users"""
    if st.session_state.api_connected:
        return
    
    st.markdown("### 🎯 Welcome to DSA Coach AI")
    st.markdown("Your intelligent coding mentor for mastering Data Structures and Algorithms")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Generate Practice Problems", use_container_width=True):
            st.session_state.quick_nav = "🎯 Problem Generator"
            st.rerun()
    
    with col2:
        if st.button("💡 Get Smart Hints", use_container_width=True):
            st.session_state.quick_nav = "💡 Hint System"
            st.rerun()
    
    with col3:
        if st.button("📝 Review My Code", use_container_width=True):
            st.session_state.quick_nav = "📝 Code Review"
            st.rerun()

def main():
    """Main application function"""
    st.set_page_config(
        page_title="DSA Coach AI",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }
    .stSelectbox > div > div {
        background-color: #000000;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .feature-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button {
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Check API connection
    check_api_connection()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🧠 DSA Coach AI")
        st.markdown("### Your intelligent coding mentor for mastering Data Structures and Algorithms")
    
    # with col2:
    #     if st.session_state.api_connected:
    #         st.success("🟢 System Online")
    #     else:
    #         st.error("🔴 System Offline")
    
    # Render API status check
    if not render_api_status():
        return
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Handle quick navigation
    if st.session_state.get('quick_nav'):
        page = st.session_state.quick_nav
        st.session_state.quick_nav = None
    
    # Main content area
    try:
        if page == "🎯 Problem Generator":
            problem_generator = ProblemGeneratorComponent(api_client)
            problem_generator.render()
        
        elif page == "💡 Hint System":
            hint_system = HintSystemComponent(api_client)
            hint_system.render()
        
        elif page == "📝 Code Review":
            code_reviewer = CodeReviewerComponent(api_client)
            code_reviewer.render()
        
        elif page == "📊 Progress Tracker":
            progress_tracker = ProgressTrackerComponent(api_client)
            progress_tracker.render()
        
        else:
            st.info(f"🚧 {page.split(' ', 1)[1]} is coming soon! Please try other features.")
            render_welcome_section()
    
    except Exception as e:
        logger.error(f"Error rendering page {page}: {str(e)}")
        st.error("An error occurred while loading this feature. Please try again.")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💡 Tips:**")
        st.markdown("- Start with Problem Generator for practice")
        st.markdown("- Use hints progressively for learning")
    
    with col2:
        st.markdown("**🎯 Features:**")
        st.markdown("- AI-powered problem generation")
        st.markdown("- Progressive hint system")
    
    with col3:
        st.markdown("**📊 Progress:**")
        st.markdown("- Track your improvement")
        st.markdown("- Identify weak areas")

if __name__ == "__main__":
    main()
