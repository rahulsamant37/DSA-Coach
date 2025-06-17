from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class SkillLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class TargetGoal(str, Enum):
    TECHNICAL_INTERVIEWS = "Technical Interviews"
    COMPETITIVE_PROGRAMMING = "Competitive Programming"
    GENERAL_IMPROVEMENT = "General Improvement"

# User Models
class UserProfile(BaseModel):
    skill_level: SkillLevel
    target_goal: TargetGoal
    daily_goal: int = Field(ge=1, le=20)
    focus_areas: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserProgress(BaseModel):
    user_id: str
    profile: UserProfile
    total_problems_solved: int = 0
    current_streak: int = 0
    total_hints_used: int = 0
    last_activity: Optional[datetime] = None
    topic_performance: Dict[str, Any] = {}
    achievements: List[Dict[str, Any]] = []

# Problem Models
class Problem(BaseModel):
    id: Optional[str] = None
    title: str
    statement: str
    difficulty: DifficultyLevel
    core_concept: str
    context: str
    estimated_time: str
    complexity: str
    approach_hint: Optional[str] = None
    examples: List[str] = []
    constraints: List[str] = []
    created_at: Optional[datetime] = None

class ProblemGenerationRequest(BaseModel):
    original_problem: str
    num_variations: int = Field(ge=1, le=10, default=3)
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    context_options: List[str] = []
    focus_areas: List[str] = []
    include_hints: bool = True

class ProblemGenerationResponse(BaseModel):
    problems: List[Problem]
    generation_timestamp: datetime
    user_id: str

# Hint System Models
class HintRequest(BaseModel):
    problem_id: str
    current_hint_level: int = 0
    user_approach: Optional[str] = None

class Hint(BaseModel):
    level: int
    content: str
    hint_type: str  # "clarifying", "direction", "structure", "implementation"
    timestamp: datetime

class HintResponse(BaseModel):
    hint: Hint
    next_available: bool
    total_levels: int

# Code Review Models
class CodeReviewRequest(BaseModel):
    code: str
    language: str
    problem_context: Optional[str] = None
    focus_aspects: List[str] = []
    additional_context: Optional[str] = None

class CodeAnalysis(BaseModel):
    correctness_score: int = Field(ge=1, le=10)
    time_complexity: str
    space_complexity: str
    style_rating: int = Field(ge=1, le=10)
    summary: str

class CodeReviewResponse(BaseModel):
    overall_analysis: CodeAnalysis
    issues: List[str]
    optimizations: List[str]
    alternatives: List[str]
    review_timestamp: datetime

# Debug Models
class DebugRequest(BaseModel):
    code: str
    language: str
    problem_description: str
    expected_behavior: str
    actual_behavior: str
    error_message: Optional[str] = None
    debug_focus: List[str] = []

class DebugResponse(BaseModel):
    bug_analysis: Dict[str, Any]
    fix_suggestions: List[str]
    testing_guidance: Dict[str, Any]
    learning_points: List[str]
    debug_timestamp: datetime

# Interview Models
class InterviewConfig(BaseModel):
    interview_type: str
    duration: int  # minutes
    difficulty: DifficultyLevel
    focus_areas: List[str]
    style: str

class InterviewSession(BaseModel):
    config: InterviewConfig
    start_time: datetime
    end_time: Optional[datetime] = None
    current_phase: str = "introduction"
    problems: List[Problem] = []
    responses: List[Dict[str, Any]] = []
    feedback: Optional[Dict[str, Any]] = None

# Memory Palace Models
class MemoryAidRequest(BaseModel):
    concept_type: str
    concept_name: str
    description: str
    difficulty: DifficultyLevel
    learning_style: str
    aid_types: List[str]

class MemoryAid(BaseModel):
    concept_name: str
    mnemonics: List[str] = []
    visual_analogies: List[str] = []
    stories: List[str] = []
    mental_models: List[str] = []
    pattern_frameworks: List[str] = []
    rhythms: List[str] = []
    created_at: datetime
    practice_count: int = 0

# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
