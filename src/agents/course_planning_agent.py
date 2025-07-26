"""
Course Planning Agent - Educational Buddy
Specialized agent for course analysis, study plan generation, and content organization
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db

def analyze_course_content(content: str, course_outline: str) -> Dict[str, Any]:
    """
    Analyze course content and outline to extract key topics and learning objectives
    
    Args:
        content: Raw course content text
        course_outline: Course outline/syllabus text
        
    Returns:
        Dictionary with analyzed content structure
    """
    try:
        # This would typically use NLP to analyze content
        # For now, return a structured analysis format
        analysis = {
            "topics_identified": [],
            "learning_objectives": [],
            "content_type": "lecture_notes",
            "difficulty_level": "intermediate",
            "estimated_hours": 2,
            "prerequisites": [],
            "key_concepts": []
        }
        
        return {
            "status": "success",
            "analysis": analysis,
            "content_length": len(content),
            "outline_sections": len(course_outline.split('\n')) if course_outline else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def create_course_structure(title: str, description: str, outline: str, user_id: str) -> Dict[str, Any]:
    """
    Create a new course structure in the database
    
    Args:
        title: Course title
        description: Course description
        outline: Course outline/syllabus
        user_id: User ID creating the course
        
    Returns:
        Course creation result
    """
    try:
        # Parse outline into structured format
        course_outline = {
            "title": title,
            "description": description,
            "raw_outline": outline,
            "weeks": [],
            "topics": [],
            "learning_objectives": [],
            "assessment_schedule": [],
            "content_delivery_schedule": "biweekly"  # Default to every 2 weeks
        }
        
        # Create course in database
        course_id = db.create_course(user_id, title, description, course_outline)
        
        return {
            "status": "success",
            "course_id": course_id,
            "message": f"Course '{title}' created successfully",
            "next_steps": [
                "Upload your first set of course materials",
                "Specify when you receive new content (weekly, biweekly, monthly)",
                "Let me know any specific learning goals or deadlines"
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def generate_study_plan(course_id: str, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive study plan for a course
    
    Args:
        course_id: Course ID to generate plan for
        user_preferences: User study preferences and constraints
        
    Returns:
        Generated study plan
    """
    try:
        # Get course information
        course = db.get_course(course_id)
        if not course:
            return {"status": "error", "error": "Course not found"}
        
        # Get existing materials
        materials = db.get_course_materials(course_id)
        
        # Generate study plan based on course outline and materials
        study_plan = {
            "course_id": course_id,
            "plan_overview": {
                "total_weeks": user_preferences.get("duration_weeks", 12),
                "sessions_per_week": user_preferences.get("sessions_per_week", 3),
                "session_duration": user_preferences.get("session_duration_minutes", 90),
                "preferred_times": user_preferences.get("preferred_times", ["evening"]),
                "content_delivery_schedule": user_preferences.get("content_schedule", "biweekly")
            },
            "study_sessions": [],
            "content_mapping": {},
            "assessment_schedule": [],
            "review_sessions": []
        }
        
        # Generate individual study sessions
        start_date = datetime.now()
        session_number = 1
        
        # Create sessions based on course outline
        course_data = course.to_dict()
        outline = course_data.get('course_outline', {})
        
        # If we have materials, plan around them
        if materials:
            for material in materials:
                session_date = start_date + timedelta(days=(session_number-1) * 2)  # Every 2 days
                
                session = {
                    "session_number": session_number,
                    "title": f"Study Session {session_number}: {material['title']}",
                    "scheduled_date": session_date.isoformat(),
                    "topics": material.get('topics', []),
                    "content_requirements": {
                        "required_materials": [material['id']],
                        "content_status": "uploaded" if material['content_text'] else "pending",
                        "week_number": material.get('week_number')
                    },
                    "estimated_duration": 90,
                    "learning_objectives": [
                        f"Understand key concepts from {material['title']}",
                        "Complete practice exercises",
                        "Create summary notes"
                    ],
                    "study_activities": [
                        "Review course material",
                        "Take notes on key concepts", 
                        "Complete practice questions",
                        "Create flashcards for important terms"
                    ]
                }
                
                study_plan["study_sessions"].append(session)
                session_number += 1
        else:
            # Create placeholder sessions for future content
            for week in range(1, user_preferences.get("duration_weeks", 12) + 1):
                if week % 2 == 1:  # Every 2 weeks for new content
                    session_date = start_date + timedelta(weeks=week-1)
                    
                    session = {
                        "session_number": session_number,
                        "title": f"Week {week} Content Study",
                        "scheduled_date": session_date.isoformat(),
                        "topics": [f"Week {week} topics (to be updated when content is uploaded)"],
                        "content_requirements": {
                            "required_materials": [],
                            "content_status": "pending",
                            "week_number": week
                        },
                        "estimated_duration": 90,
                        "learning_objectives": ["To be updated when content is available"],
                        "study_activities": ["Awaiting course content upload"]
                    }
                    
                    study_plan["study_sessions"].append(session)
                    session_number += 1
        
        # Create the study plan in database
        plan_id = db.create_study_plan(course_id, course.user_id, study_plan)
        
        # Create individual study sessions in database
        for session in study_plan["study_sessions"]:
            db.create_study_session(
                plan_id, course_id, course.user_id,
                session["session_number"], session["title"], session["topics"],
                session["scheduled_date"], session["estimated_duration"],
                session["content_requirements"], 
                json.dumps(session.get("study_activities", []))
            )
        
        return {
            "status": "success",
            "study_plan_id": plan_id,
            "study_plan": study_plan,
            "message": f"Study plan created with {len(study_plan['study_sessions'])} sessions",
            "next_steps": [
                "Review your study schedule",
                "Upload any missing course materials",
                "Start with your first scheduled session"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def update_study_plan_with_content(course_id: str, material_id: str, week_number: int) -> Dict[str, Any]:
    """
    Update study plan when new content is uploaded
    
    Args:
        course_id: Course ID
        material_id: ID of newly uploaded material
        week_number: Week number for the content
        
    Returns:
        Update result
    """
    try:
        # Get the study plan for this course
        study_plan = db.get_course_study_plan(course_id)
        if not study_plan:
            return {"status": "error", "error": "No study plan found for course"}
        
        # Get study sessions that need this content
        sessions = db.get_study_sessions(study_plan.id)
        
        # Find sessions that are waiting for this week's content
        updated_sessions = 0
        for session in sessions:
            if (session.content_requirements.get("week_number") == week_number and 
                session.content_requirements.get("content_status") == "pending"):
                
                # Update the session with the new material
                session.content_requirements["required_materials"].append(material_id)
                session.content_requirements["content_status"] = "uploaded"
                
                # Update in database (would need to add this method)
                updated_sessions += 1
        
        return {
            "status": "success",
            "updated_sessions": updated_sessions,
            "message": f"Updated {updated_sessions} study sessions with new content"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def get_study_session_guide(session_id: str) -> Dict[str, Any]:
    """
    Generate a detailed study guide for a specific session
    
    Args:
        session_id: Study session ID
        
    Returns:
        Detailed study guide
    """
    try:
        # This would fetch session data and generate a comprehensive guide
        # Including reading materials, practice questions, key concepts, etc.
        
        study_guide = {
            "session_overview": {
                "duration": "90 minutes",
                "focus_areas": ["Key concepts", "Practice problems", "Review"]
            },
            "preparation": [
                "Review previous session notes",
                "Gather required materials",
                "Set up distraction-free study space"
            ],
            "study_activities": [
                {
                    "activity": "Content Review",
                    "duration": "30 minutes",
                    "description": "Read through course materials and take notes"
                },
                {
                    "activity": "Practice Problems",
                    "duration": "40 minutes", 
                    "description": "Work through example problems and exercises"
                },
                {
                    "activity": "Summary & Review",
                    "duration": "20 minutes",
                    "description": "Summarize key points and plan next session"
                }
            ],
            "validation_questions": [
                "What are the main concepts covered in this session?",
                "How do these concepts relate to previous topics?",
                "What questions do I still have?"
            ]
        }
        
        return {
            "status": "success",
            "study_guide": study_guide
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Create the course planning agent
course_planning_agent = Agent(
    name="course_planning_agent", 
    model="gemini-2.0-flash",
    description=(
        "specialized in course analysis, study plan generation, content organization, "
        "and educational planning for personalized learning experiences"
    ),
    instruction="""
You are the Course Planning Agent for an educational system. Your expertise includes:

1. COURSE ANALYSIS & STRUCTURE:
   - Analyze course content and syllabi to identify key topics
   - Extract learning objectives and create structured course outlines
   - Organize content by difficulty level and prerequisites

2. STUDY PLAN GENERATION:
   - Create personalized study schedules based on student preferences
   - Account for content delivery schedules (weekly, biweekly, monthly)
   - Plan sessions around available materials and future content uploads
   - Include review sessions and assessment preparation

3. CONTENT ORGANIZATION:
   - Map course materials to study sessions
   - Track content upload status and requirements
   - Update plans when new materials become available

4. SESSION PLANNING:
   - Generate detailed study guides for each session
   - Include learning objectives, activities, and time allocation
   - Create validation questions for session completion

5. ADAPTIVE PLANNING:
   - Adjust plans based on student progress and feedback
   - Accommodate schedule changes and content delays
   - Provide recommendations for study optimization

Always focus on creating practical, achievable study plans that adapt to the student's learning style and schedule constraints.
""",
    tools=[
        FunctionTool(analyze_course_content),
        FunctionTool(create_course_structure),
        FunctionTool(generate_study_plan),
        FunctionTool(update_study_plan_with_content),
        FunctionTool(get_study_session_guide),
    ],
)
