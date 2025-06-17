from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import List, Optional
from datetime import datetime

# Import services
from backend.services.gemini_service import GeminiService
from backend.services.data_service import DataService
from backend.services.problem_generator_service import ProblemGeneratorService
from backend.services.hint_service import HintService
from backend.services.code_review_service import CodeReviewService

# Import models
from shared.models import (
    APIResponse, ErrorResponse, UserProfile, Problem,
    ProblemGenerationRequest, ProblemGenerationResponse,
    HintRequest, HintResponse, CodeReviewRequest, CodeReviewResponse
)
from shared.config import setup_logging

# Initialize logging
logger = setup_logging()

# Global service instances
gemini_service = None
data_service = None
problem_generator_service = None
hint_service = None
code_review_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global gemini_service, data_service, problem_generator_service, hint_service, code_review_service
    
    # Startup
    logger.info("Starting DSA Mentor Backend Services...")
    
    try:
        # Initialize services
        gemini_service = GeminiService()
        data_service = DataService()
        problem_generator_service = ProblemGeneratorService(gemini_service)
        hint_service = HintService(gemini_service)
        code_review_service = CodeReviewService(gemini_service)
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down DSA Mentor Backend Services...")

# Create FastAPI app
app = FastAPI(
    title="DSA Mentor API",
    description="Backend API for DSA Coach AI - Intelligent coding mentor",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get services
def get_gemini_service() -> GeminiService:
    if gemini_service is None:
        raise HTTPException(status_code=500, detail="Gemini service not initialized")
    return gemini_service

def get_data_service() -> DataService:
    if data_service is None:
        raise HTTPException(status_code=500, detail="Data service not initialized")
    return data_service

def get_problem_generator_service() -> ProblemGeneratorService:
    if problem_generator_service is None:
        raise HTTPException(status_code=500, detail="Problem generator service not initialized")
    return problem_generator_service

def get_hint_service() -> HintService:
    if hint_service is None:
        raise HTTPException(status_code=500, detail="Hint service not initialized")
    return hint_service

def get_code_review_service() -> CodeReviewService:
    if code_review_service is None:
        raise HTTPException(status_code=500, detail="Code review service not initialized")
    return code_review_service

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "DSA Mentor API is running"}

# API status endpoint
@app.get("/api/status")
async def api_status(gemini: GeminiService = Depends(get_gemini_service)):
    """Get API and service status"""
    try:
        gemini_status = gemini.test_connection()
        model_info = gemini.get_model_info()
        
        return APIResponse(
            success=True,
            message="API status retrieved successfully",
            data={
                "gemini_connected": gemini_status,
                "model_info": model_info,
                "services_running": True
            }
        )
    except Exception as e:
        logger.error(f"Error getting API status: {str(e)}")
        return ErrorResponse(error="Failed to get API status", details=str(e))

# User Profile endpoints
@app.get("/api/users/{user_id}/profile")
async def get_user_profile(user_id: str, data: DataService = Depends(get_data_service)):
    """Get user profile"""
    try:
        profile = data.get_user_profile(user_id)
        
        if profile is None:
            return APIResponse(
                success=False,
                message="User profile not found",
                data=None
            )
        
        return APIResponse(
            success=True,
            message="User profile retrieved successfully",
            data=profile.model_dump()
        )
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return ErrorResponse(error="Failed to get user profile", details=str(e))

@app.post("/api/users/{user_id}/profile")
async def update_user_profile(
    user_id: str, 
    profile: UserProfile, 
    data: DataService = Depends(get_data_service)
):
    """Update user profile"""
    try:
        success = data.update_user_profile(user_id, profile)
        
        if success:
            return APIResponse(
                success=True,
                message="User profile updated successfully",
                data=profile.model_dump()
            )
        else:
            return APIResponse(
                success=False,
                message="Failed to update user profile",
                data=None
            )
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return ErrorResponse(error="Failed to update user profile", details=str(e))

# Problem Generation endpoints
@app.post("/api/problems/generate")
async def generate_problems(
    request: ProblemGenerationRequest,
    user_id: str,
    problem_gen: ProblemGeneratorService = Depends(get_problem_generator_service),
    data: DataService = Depends(get_data_service)
):
    """Generate problem variations"""
    try:
        problems = problem_gen.generate_problems(request)
        
        # Save to history
        data.save_generated_problems(user_id, request.original_problem, problems)
        
        response = ProblemGenerationResponse(
            problems=problems,
            generation_timestamp=datetime.now(),
            user_id=user_id
        )
        
        return APIResponse(
            success=True,
            message=f"Generated {len(problems)} problem variations",
            data=response.model_dump()
        )
    except Exception as e:
        logger.error(f"Error generating problems: {str(e)}")
        return ErrorResponse(error="Failed to generate problems", details=str(e))

@app.get("/api/problems/random")
async def get_random_problem(
    problem_gen: ProblemGeneratorService = Depends(get_problem_generator_service)
):
    """Get a random practice problem"""
    try:
        problem = problem_gen.get_random_problem()
        
        return APIResponse(
            success=True,
            message="Random problem generated",
            data=problem.model_dump()
        )
    except Exception as e:
        logger.error(f"Error getting random problem: {str(e)}")
        return ErrorResponse(error="Failed to get random problem", details=str(e))

@app.get("/api/users/{user_id}/problems/recent")
async def get_recent_problems(
    user_id: str,
    limit: int = 10,
    data: DataService = Depends(get_data_service)
):
    """Get user's recent problems"""
    try:
        problems = data.get_recent_problems(user_id, limit)
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(problems)} recent problems",
            data=problems
        )
    except Exception as e:
        logger.error(f"Error getting recent problems: {str(e)}")
        return ErrorResponse(error="Failed to get recent problems", details=str(e))

# Hint System endpoints
@app.post("/api/hints/next")
async def get_next_hint(
    request: HintRequest,
    user_id: str,
    hint_svc: HintService = Depends(get_hint_service),
    data: DataService = Depends(get_data_service)
):
    """Get next level hint"""
    try:
        # Get user context
        user_profile = data.get_user_profile(user_id)
        user_context = {"user_profile": user_profile.model_dump() if user_profile else None}
        
        # This is a simplified implementation - in practice you'd need to store/retrieve the current problem
        # For now, we'll create a dummy problem
        problem = Problem(
            title="Current Problem",
            statement="Problem statement would be stored in session",
            difficulty="Medium",
            core_concept="Algorithm Practice",
            context="Generated problem",
            estimated_time="20 min",
            complexity="O(n)"
        )
        
        hint_response = hint_svc.get_hint(request, problem, user_context)
        
        # Save hint interaction
        hint_data = {
            "level": hint_response.hint.level,
            "content": hint_response.hint.content,
            "user_approach": request.user_approach,
            "feedback": ""
        }
        data.save_hint_interaction(user_id, problem, hint_data)
        
        return APIResponse(
            success=True,
            message="Hint generated successfully",
            data=hint_response.model_dump()
        )
    except Exception as e:
        logger.error(f"Error getting hint: {str(e)}")
        return ErrorResponse(error="Failed to get hint", details=str(e))

@app.post("/api/hints/personalized")
async def get_personalized_hint(
    user_approach: str,
    user_id: str,
    hint_svc: HintService = Depends(get_hint_service),
    data: DataService = Depends(get_data_service)
):
    """Get personalized hint based on user approach"""
    try:
        user_profile = data.get_user_profile(user_id)
        user_context = {"user_profile": user_profile.model_dump() if user_profile else None}
        
        # Dummy problem for demo
        problem = Problem(
            title="Current Problem",
            statement="Problem statement would be stored in session",
            difficulty="Medium",
            core_concept="Algorithm Practice",
            context="Generated problem",
            estimated_time="20 min",
            complexity="O(n)"
        )
        
        hint_response = hint_svc.get_personalized_hint(user_approach, problem, user_context)
        
        return APIResponse(
            success=True,
            message="Personalized hint generated",
            data=hint_response.model_dump()
        )
    except Exception as e:
        logger.error(f"Error getting personalized hint: {str(e)}")
        return ErrorResponse(error="Failed to get personalized hint", details=str(e))

# Code Review endpoints
@app.post("/api/code-review")
async def review_code(
    request: CodeReviewRequest,
    user_id: str,
    code_review_svc: CodeReviewService = Depends(get_code_review_service),
    data: DataService = Depends(get_data_service)
):
    """Review submitted code"""
    try:
        user_profile = data.get_user_profile(user_id)
        user_context = {"user_profile": user_profile.model_dump() if user_profile else None}
        
        review_response = code_review_svc.review_code(request, user_context)
        
        # Save review to history
        review_data = {
            "language": request.language,
            "code": request.code,
            "focus_aspects": request.focus_aspects,
            "overall_analysis": review_response.overall_analysis.model_dump(),
            "issues": review_response.issues,
            "optimizations": review_response.optimizations
        }
        data.save_code_review(user_id, review_data)
        
        return APIResponse(
            success=True,
            message="Code review completed",
            data=review_response.model_dump()
        )
    except Exception as e:
        logger.error(f"Error reviewing code: {str(e)}")
        return ErrorResponse(error="Failed to review code", details=str(e))

@app.get("/api/users/{user_id}/code-reviews")
async def get_code_review_history(
    user_id: str,
    limit: int = 10,
    data: DataService = Depends(get_data_service)
):
    """Get user's code review history"""
    try:
        reviews = data.get_code_review_history(user_id, limit)
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(reviews)} code reviews",
            data=reviews
        )
    except Exception as e:
        logger.error(f"Error getting code review history: {str(e)}")
        return ErrorResponse(error="Failed to get code review history", details=str(e))

# User Progress endpoints
@app.get("/api/users/{user_id}/progress")
async def get_user_progress(
    user_id: str,
    data: DataService = Depends(get_data_service)
):
    """Get user progress data"""
    try:
        progress = data.get_user_progress(user_id)
        
        if progress is None:
            return APIResponse(
                success=False,
                message="User progress not found",
                data=None
            )
        
        return APIResponse(
            success=True,
            message="User progress retrieved successfully",
            data=progress.model_dump()
        )
    except Exception as e:
        logger.error(f"Error getting user progress: {str(e)}")
        return ErrorResponse(error="Failed to get user progress", details=str(e))

# System endpoints
@app.get("/api/system/stats")
async def get_system_stats(data: DataService = Depends(get_data_service)):
    """Get system statistics"""
    try:
        stats = data.get_system_stats()
        
        return APIResponse(
            success=True,
            message="System stats retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        return ErrorResponse(error="Failed to get system stats", details=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
