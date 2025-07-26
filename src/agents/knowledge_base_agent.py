"""
Knowledge Base Agent - Educational Buddy
Handles student profiles, course materials, and context retrieval using RAG
Integrates with SQLite database and vector storage for comprehensive knowledge management
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
import sys
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add parent path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_current_user_id() -> str:
    """Get current user ID from Flask context"""
    try:
        from flask_login import current_user
        if hasattr(current_user, 'id') and current_user.is_authenticated:
            return str(current_user.id)
        return "anonymous"
    except Exception:
        return "anonymous"

def query_user_courses() -> Dict[str, Any]:
    """Query all courses for the current user"""
    try:
        user_id = get_current_user_id()
        if user_id == "anonymous":
            return {
                "status": "error",
                "error": "User not authenticated",
                "courses": []
            }
        from models import Database
        db = Database()
        
        # Get all courses for user
        courses = db.get_user_courses(user_id)
        courses_data = [course.to_dict() for course in courses]
        
        # Get materials for each course
        for course_data in courses_data:
            materials = db.get_course_materials(course_data['id'])
            course_data['materials'] = materials
            
            # Get study plan if exists
            study_plan = db.get_course_study_plan(course_data['id'])
            course_data['study_plan'] = study_plan.to_dict() if study_plan else None
            
            # Get progress
            progress = db.get_course_progress(course_data['id'])
            course_data['progress'] = progress
        
        return {
            "status": "success",
            "courses": courses_data,
            "total_count": len(courses_data)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "courses": []
        }

def find_course_by_title(course_title: str) -> Dict[str, Any]:
    """Find a specific course by title for the current user"""
    try:
        user_id = get_current_user_id()
        if user_id == "anonymous":
            return {
                "status": "error",
                "error": "User not authenticated",
                "found": False
            }
        from models import Database
        db = Database()
        
        # Get all user courses and search by title
        courses = db.get_user_courses(user_id)
        
        for course in courses:
            if course_title.lower() in course.title.lower() or course.title.lower() in course_title.lower():
                course_data = course.to_dict()
                
                # Get additional details
                materials = db.get_course_materials(course.id)
                course_data['materials'] = materials
                
                study_plan = db.get_course_study_plan(course.id)
                course_data['study_plan'] = study_plan.to_dict() if study_plan else None
                
                progress = db.get_course_progress(course.id)
                course_data['progress'] = progress
                
                return {
                    "status": "success",
                    "found": True,
                    "course": course_data
                }
        
        return {
            "status": "success", 
            "found": False,
            "message": f"No course found matching '{course_title}'"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "found": False
        }

def create_new_course(title: str, description: str, course_outline: str) -> Dict[str, Any]:
    """Create a new course in the database for the current user"""
    try:
        user_id = get_current_user_id()
        if user_id == "anonymous":
            return {
                "status": "error",
                "error": "User not authenticated",
                "created": False
            }
        from models import Database
        db = Database()
        
        # Create course
        course_id = db.create_course(user_id, title, description, course_outline)
        
        if course_id:
            # Get the created course
            course = db.get_course(course_id)
            return {
                "status": "success",
                "created": True,
                "course_id": course_id,
                "course": course.to_dict() if course else None
            }
        else:
            return {
                "status": "error",
                "created": False,
                "error": "Failed to create course"
            }
    except Exception as e:
        return {
            "status": "error",
            "created": False,
            "error": str(e)
        }

def store_course_material(course_id: str, title: str, content_type: str, content_text: str) -> Dict[str, Any]:
    """Store course material in the database for the current user"""
    try:
        user_id = get_current_user_id()
        if user_id == "anonymous":
            return {
                "status": "error",
                "error": "User not authenticated",
                "stored": False
            }
        from models import Database
        db = Database()
        
        material_id = db.add_course_material(
            course_id, user_id, title, content_type, 
            content_text, None, None, []  # week_number set to None
        )
        
        if material_id:
            return {
                "status": "success",
                "stored": True,
                "material_id": material_id
            }
        else:
            return {
                "status": "error", 
                "stored": False,
                "error": "Failed to store material"
            }
    except Exception as e:
        return {
            "status": "error",
            "stored": False,
            "error": str(e)
        }

def get_study_plan_details(course_id: str) -> Dict[str, Any]:
    """Get detailed study plan information for a course for the current user"""
    try:
        user_id = get_current_user_id()
        if user_id == "anonymous":
            return {
                "status": "error",
                "error": "User not authenticated",
                "has_plan": False
            }
        from models import Database
        db = Database()
        
        # Get study plan
        study_plan = db.get_course_study_plan(course_id)
        if not study_plan:
            return {
                "status": "success",
                "has_plan": False,
                "message": "No study plan found for this course"
            }
        
        # Get study sessions
        study_sessions = db.get_study_sessions(study_plan.id)
        sessions_data = [session.to_dict() for session in study_sessions]
        
        return {
            "status": "success",
            "has_plan": True,
            "study_plan": study_plan.to_dict(),
            "study_sessions": sessions_data,
            "total_sessions": len(sessions_data)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "has_plan": False
        }

def search_course_content(search_query: str) -> Dict[str, Any]:
    """Search through course materials and content for the current user"""
    try:
        user_id = get_current_user_id()
        if user_id == "anonymous":
            return {
                "status": "error",
                "error": "User not authenticated",
                "results": []
            }
        from models import Database
        db = Database()
        
        # Get all user courses
        courses = db.get_user_courses(user_id)
        search_results = []
        
        for course in courses:
            # Search in course title and description
            if search_query.lower() in course.title.lower() or search_query.lower() in course.description.lower():
                search_results.append({
                    "type": "course",
                    "course_id": course.id,
                    "course_title": course.title,
                    "match": "course_info",
                    "relevance": "high"
                })
            
            # Search in course materials
            materials = db.get_course_materials(course.id)
            for material in materials:
                if search_query.lower() in material['title'].lower() or search_query.lower() in material['content_text'].lower():
                    search_results.append({
                        "type": "material",
                        "course_id": course.id,
                        "course_title": course.title,
                        "material_id": material['id'],
                        "material_title": material['title'],
                        "match": "course_material",
                        "relevance": "medium"
                    })
        
        return {
            "status": "success",
            "results": search_results,
            "total_matches": len(search_results)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "results": []
        }

def _get_instruction_prompt() -> str:
    """Get the instruction prompt for the Knowledge Base Agent"""
    return """
You are a Knowledge Base Agent for an Educational Buddy system. Your role is to:

1. **Database Management**: Store and retrieve student profiles, preferences, and learning history
2. **Course Management**: Manage courses, materials, and educational content in the database
3. **Context Retrieval**: Provide context-aware responses based on stored information
4. **Progress Tracking**: Track study progress and performance metrics
5. **Content Search**: Search through course materials and provide relevant information

**CRITICAL WORKFLOW INTEGRATION:**
Before any course-related task (study plan creation, material upload, etc.), you MUST:
1. Use find_course_by_title() to check if the course already exists
2. If course doesn't exist, use create_new_course() to create it first
3. Store any uploaded materials using store_course_material()
4. Provide unified course knowledge for other agents to use

**Available Functions:**
- query_user_courses(): Get all courses for the current user
- find_course_by_title(course_title): Find specific course by title for current user
- create_new_course(title, description, outline): Create new course for current user
- store_course_material(course_id, title, content_type, content_text, week): Store course material
- get_study_plan_details(course_id): Get study plan information for current user
- search_course_content(search_query): Search through current user's course content

**Key Behaviors:**
- Automatically access current user's information - no need to ask for user ID
- Always check if courses exist before creating new ones
- Store all course materials systematically for future retrieval
- Provide comprehensive course context to other agents
- Maintain data integrity and prevent duplicates
- Support personalized learning recommendations based on stored data

When handling requests:
- Automatically access the student's profile and learning history
- Retrieve relevant course materials and notes from database
- Provide personalized responses based on stored context
- Update learning progress and preferences
- Maintain data privacy and security
- **Always use database functions to ensure courses exist before proceeding**
- **Never ask users for their user ID - it's automatically available**

You are the centralized knowledge repository that other agents depend on for course information.
"""

# Create function tools for the knowledge base agent
query_courses_tool = FunctionTool(query_user_courses)
find_course_tool = FunctionTool(find_course_by_title)
create_course_tool = FunctionTool(create_new_course)
store_material_tool = FunctionTool(store_course_material)
get_plan_tool = FunctionTool(get_study_plan_details)
search_content_tool = FunctionTool(search_course_content)

# Create the knowledge base agent using Google ADK with database tools
knowledge_base_agent = Agent(
    model="gemini-2.0-flash",
    name="knowledge_base_agent",
    instruction=_get_instruction_prompt(),
    output_key="knowledge_results",
    tools=[
        query_courses_tool,
        find_course_tool, 
        create_course_tool,
        store_material_tool,
        get_plan_tool,
        search_content_tool
    ]
)
