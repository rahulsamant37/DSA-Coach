import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from shared.models import UserProfile, UserProgress, Problem
from shared.config import DATA_DIR, USER_PROGRESS_FILE, PROBLEMS_HISTORY_FILE

class DataService:
    def __init__(self):
        self.data_dir = Path(DATA_DIR)
        self.data_dir.mkdir(exist_ok=True)
        
        # Data file paths
        self.user_progress_file = self.data_dir / USER_PROGRESS_FILE
        self.problems_history_file = self.data_dir / PROBLEMS_HISTORY_FILE
        
        self.logger = logging.getLogger(__name__)
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """Initialize data files with empty structures if they don't exist"""
        try:
            if not self.user_progress_file.exists():
                initial_progress = {}
                self._save_json(self.user_progress_file, initial_progress)
            
            if not self.problems_history_file.exists():
                initial_problems = {}
                self._save_json(self.problems_history_file, initial_problems)
                
            self.logger.info("Data files initialized successfully")
        
        except Exception as e:
            self.logger.error(f"Error initializing data files: {str(e)}")
            raise
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {str(e)}")
            return {}
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Save JSON data to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {str(e)}")
            raise
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp as string"""
        return datetime.now().isoformat()
    
    # User Profile Management
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile data"""
        try:
            progress_data = self._load_json(self.user_progress_file)
            profile_data = progress_data.get(user_id, {}).get('profile', {})
            
            if profile_data:
                return UserProfile(**profile_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting user profile for {user_id}: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: str, profile: UserProfile) -> bool:
        """Update user profile"""
        try:
            progress_data = self._load_json(self.user_progress_file)
            
            if user_id not in progress_data:
                progress_data[user_id] = {}
            
            profile.updated_at = datetime.now()
            if not profile.created_at:
                profile.created_at = datetime.now()
            
            progress_data[user_id]['profile'] = profile.model_dump()
            progress_data[user_id]['last_updated'] = self.get_current_timestamp()
            
            self._save_json(self.user_progress_file, progress_data)
            self.logger.info(f"Updated profile for user {user_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error updating user profile for {user_id}: {str(e)}")
            return False
    
    # Problem Generation History
    def save_generated_problems(self, user_id: str, original_problem: str, problems: List[Problem]) -> bool:
        """Save generated problem variations"""
        try:
            problems_data = self._load_json(self.problems_history_file)
            
            if user_id not in problems_data:
                problems_data[user_id] = []
            
            problem_session = {
                'timestamp': self.get_current_timestamp(),
                'original_problem': original_problem,
                'variations': [problem.model_dump() for problem in problems],
                'session_id': len(problems_data[user_id]) + 1
            }
            
            problems_data[user_id].append(problem_session)
            
            # Keep only last 50 sessions per user
            if len(problems_data[user_id]) > 50:
                problems_data[user_id] = problems_data[user_id][-50:]
            
            self._save_json(self.problems_history_file, problems_data)
            self.logger.info(f"Saved {len(problems)} problems for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving problems for {user_id}: {str(e)}")
            return False
    
    def get_recent_problems(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent problem generations"""
        try:
            problems_data = self._load_json(self.problems_history_file)
            user_problems = problems_data.get(user_id, [])
            
            # Return most recent sessions
            return sorted(user_problems, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
        except Exception as e:
            self.logger.error(f"Error getting recent problems for {user_id}: {str(e)}")
            return []
    
    def add_to_favorites(self, user_id: str, problem: Problem) -> bool:
        """Add problem to user's favorites"""
        try:
            progress_data = self._load_json(self.user_progress_file)
            
            if user_id not in progress_data:
                progress_data[user_id] = {}
            
            if 'favorites' not in progress_data[user_id]:
                progress_data[user_id]['favorites'] = []
            
            problem_data = problem.model_dump()
            problem_data['favorited_at'] = self.get_current_timestamp()
            
            progress_data[user_id]['favorites'].append(problem_data)
            
            # Keep only last 100 favorites
            if len(progress_data[user_id]['favorites']) > 100:
                progress_data[user_id]['favorites'] = progress_data[user_id]['favorites'][-100:]
            
            self._save_json(self.user_progress_file, progress_data)
            self.logger.info(f"Added problem to favorites for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding to favorites for {user_id}: {str(e)}")
            return False
    
    # Hint System
    def save_hint_interaction(self, user_id: str, problem: Problem, hint_data: Dict[str, Any]) -> bool:
        """Save hint interaction"""
        try:
            progress_data = self._load_json(self.user_progress_file)
            
            if user_id not in progress_data:
                progress_data[user_id] = {}
            
            if 'hint_history' not in progress_data[user_id]:
                progress_data[user_id]['hint_history'] = []
            
            interaction = {
                'timestamp': self.get_current_timestamp(),
                'problem_title': problem.title if problem else 'Unknown',
                'hint_level': hint_data.get('level', 0),
                'hint_content': hint_data.get('content', ''),
                'user_approach': hint_data.get('user_approach', ''),
                'feedback': hint_data.get('feedback', '')
            }
            
            progress_data[user_id]['hint_history'].append(interaction)
            
            # Keep only last 200 interactions
            if len(progress_data[user_id]['hint_history']) > 200:
                progress_data[user_id]['hint_history'] = progress_data[user_id]['hint_history'][-200:]
            
            self._save_json(self.user_progress_file, progress_data)
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving hint interaction for {user_id}: {str(e)}")
            return False
    
    # Code Review
    def save_code_review(self, user_id: str, review_data: Dict[str, Any]) -> bool:
        """Save code review session"""
        try:
            progress_data = self._load_json(self.user_progress_file)
            
            if user_id not in progress_data:
                progress_data[user_id] = {}
            
            if 'code_reviews' not in progress_data[user_id]:
                progress_data[user_id]['code_reviews'] = []
            
            review_session = {
                'timestamp': self.get_current_timestamp(),
                'language': review_data.get('language', ''),
                'code_length': len(review_data.get('code', '')),
                'focus_aspects': review_data.get('focus_aspects', []),
                'overall_score': review_data.get('overall_analysis', {}).get('correctness_score', 0),
                'issues_count': len(review_data.get('issues', [])),
                'optimizations_count': len(review_data.get('optimizations', []))
            }
            
            progress_data[user_id]['code_reviews'].append(review_session)
            
            # Keep only last 100 reviews
            if len(progress_data[user_id]['code_reviews']) > 100:
                progress_data[user_id]['code_reviews'] = progress_data[user_id]['code_reviews'][-100:]
            
            self._save_json(self.user_progress_file, progress_data)
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving code review for {user_id}: {str(e)}")
            return False
    
    def get_code_review_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get code review history"""
        try:
            progress_data = self._load_json(self.user_progress_file)
            code_reviews = progress_data.get(user_id, {}).get('code_reviews', [])
            
            return sorted(code_reviews, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
        except Exception as e:
            self.logger.error(f"Error getting code review history for {user_id}: {str(e)}")
            return []
    
    # Progress Tracking
    def get_user_progress(self, user_id: str) -> Optional[UserProgress]:
        """Get comprehensive user progress data"""
        try:
            progress_data = self._load_json(self.user_progress_file)
            user_data = progress_data.get(user_id, {})
            
            if not user_data:
                return None
            
            # Calculate progress metrics
            total_problems = len(user_data.get('hint_history', []))
            total_hints = sum(1 for h in user_data.get('hint_history', []) if h.get('hint_level', 0) > 0)
            
            # Get profile
            profile_data = user_data.get('profile', {})
            if not profile_data:
                return None
            
            profile = UserProfile(**profile_data)
            
            progress = UserProgress(
                user_id=user_id,
                profile=profile,
                total_problems_solved=total_problems,
                total_hints_used=total_hints,
                last_activity=datetime.fromisoformat(user_data.get('last_updated', datetime.now().isoformat())),
                topic_performance=self._analyze_topic_performance(user_data),
                achievements=self._calculate_achievements(user_data)
            )
            
            return progress
            
        except Exception as e:
            self.logger.error(f"Error getting user progress for {user_id}: {str(e)}")
            return None
    
    def _analyze_topic_performance(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance by topic/concept"""
        # This is a simplified implementation
        # In a real system, you'd track performance metrics per topic
        return {
            "arrays": {"score": 75, "problems_solved": 10},
            "trees": {"score": 60, "problems_solved": 5},
            "graphs": {"score": 80, "problems_solved": 8}
        }
    
    def _calculate_achievements(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate user achievements"""
        achievements = []
        
        # Problem solving achievements
        problems_solved = len(user_data.get('hint_history', []))
        if problems_solved >= 10:
            achievements.append({
                "id": "first_10_problems",
                "title": "Problem Solver",
                "description": "Solved 10 problems",
                "earned_at": self.get_current_timestamp()
            })
        
        # Code review achievements
        reviews_count = len(user_data.get('code_reviews', []))
        if reviews_count >= 5:
            achievements.append({
                "id": "code_reviewer",
                "title": "Code Reviewer",
                "description": "Completed 5 code reviews",
                "earned_at": self.get_current_timestamp()
            })
        
        return achievements
    
    # Export functionality
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data"""
        try:
            progress_data = self._load_json(self.user_progress_file)
            problems_data = self._load_json(self.problems_history_file)
            
            return {
                "user_progress": progress_data.get(user_id, {}),
                "problems_history": problems_data.get(user_id, []),
                "exported_at": self.get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Error exporting data for {user_id}: {str(e)}")
            return {}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        try:
            progress_data = self._load_json(self.user_progress_file)
            problems_data = self._load_json(self.problems_history_file)
            
            total_users = len(progress_data)
            total_problems_generated = sum(len(sessions) for sessions in problems_data.values())
            
            return {
                "total_users": total_users,
                "total_problems_generated": total_problems_generated,
                "last_updated": self.get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system stats: {str(e)}")
            return {}
