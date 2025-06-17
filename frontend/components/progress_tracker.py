import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List

class ProgressTrackerComponent:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def render(self):
        """Render the progress tracker interface"""
        st.header("📈 Progress Tracker")
        st.markdown("Track your DSA learning journey with detailed analytics and insights")
        
        # Load user progress data
        progress_data = self._load_progress_data()
        
        if not progress_data:
            self._display_no_data_message()
            return
        
        # Overview metrics
        self._display_overview_metrics(progress_data)
        
        # Recent activity
        self._display_recent_activity(progress_data)
    
    def _load_progress_data(self):
        """Load progress data from the API"""
        try:
            user_id = st.session_state.get('user_id', 'anonymous')
            response = self.api_client.get_user_progress(user_id)
            
            if response and response.get('success'):
                return response.get('data', {})
            else:
                return None
        except Exception as e:
            st.error(f"Error loading progress data: {str(e)}")
            return None
    
    def _display_no_data_message(self):
        """Display message when no progress data is available"""
        st.info("📊 No progress data available yet. Start solving problems to track your progress!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Generate Problem", use_container_width=True):
                st.info("Go to Problem Generator page to create problems")
        
        with col2:
            if st.button("💡 Get Hints", use_container_width=True):
                st.info("Go to Hint System page to get help")
        
        # Show sample dashboard
        st.markdown("### 📋 Sample Dashboard")
        with st.expander("Preview of your future dashboard", expanded=True):
            # Sample metrics
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            
            with col_s1:
                st.metric("Problems Solved", "42", "+3")
            with col_s2:
                st.metric("Average Score", "85%", "+5%")
            with col_s3:
                st.metric("Current Streak", "7 days", "+1")
            with col_s4:
                st.metric("Skills Mastered", "12", "+2")
    
    def _display_overview_metrics(self, progress_data: Dict[str, Any]):
        """Display overview metrics"""
        st.markdown("### 📊 Overview")
        
        # Extract metrics from progress data
        total_problems = progress_data.get('total_problems_solved', 0)
        avg_score = progress_data.get('average_score', 0)
        current_streak = progress_data.get('current_streak_days', 0)
        skills_mastered = len(progress_data.get('mastered_topics', []))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Problems Solved", total_problems)
        
        with col2:
            st.metric("Average Score", f"{avg_score:.1f}%")
        
        with col3:
            st.metric("Current Streak", f"{current_streak} days")
        
        with col4:
            st.metric("Skills Mastered", skills_mastered)
    
    def _display_recent_activity(self, progress_data: Dict[str, Any]):
        """Display recent activity"""
        st.markdown("### 🕐 Recent Activity")
        
        recent_activities = progress_data.get('recent_activities', [])
        
        if recent_activities:
            for activity in recent_activities[-5:]:  # Show last 5 activities
                activity_type = activity.get('type', 'Unknown')
                timestamp = activity.get('timestamp', 'Unknown')
                description = activity.get('description', '')
                
                # Choose icon based on activity type
                icon_map = {
                    'problem_solved': '✅',
                    'hint_used': '💡',
                    'code_reviewed': '📊',
                    'streak_milestone': '🔥',
                    'skill_mastered': '🏆',
                    'level_up': '⬆️'
                }
                
                icon = icon_map.get(activity_type, '📝')
                
                with st.container():
                    col_icon, col_content, col_time = st.columns([1, 6, 2])
                    
                    with col_icon:
                        st.markdown(f"### {icon}")
                    
                    with col_content:
                        st.markdown(f"**{description}**")
                        if activity.get('details'):
                            st.caption(activity['details'])
                    
                    with col_time:
                        st.caption(timestamp)
                    
                    st.divider()
        else:
            st.info("🕐 No recent activity. Start solving problems to see your activity here!")
