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
        # Analyze content structure and extract key information
        content_lines = content.split('\n') if content else []
        outline_lines = course_outline.split('\n') if course_outline else []
        
        # Extract topics by looking for headers, bullet points, and numbered items
        topics_identified = []
        learning_objectives = []
        key_concepts = []
        prerequisites = []
        
        # Simple analysis - in production this would use more sophisticated NLP
        for line in content_lines + outline_lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for topic indicators
            if any(keyword in line.lower() for keyword in ['chapter', 'unit', 'topic', 'lesson', 'week']):
                topics_identified.append(line)
            elif any(keyword in line.lower() for keyword in ['objective', 'goal', 'aim', 'learn', 'understand']):
                learning_objectives.append(line)
            elif any(keyword in line.lower() for keyword in ['concept', 'principle', 'theory', 'definition']):
                key_concepts.append(line)
            elif any(keyword in line.lower() for keyword in ['prerequisite', 'required', 'background', 'prior']):
                prerequisites.append(line)
        
        # Estimate difficulty and time requirements
        difficulty_indicators = ['advanced', 'complex', 'intermediate', 'basic', 'introduction']
        difficulty_level = "intermediate"  # Default
        
        for indicator in difficulty_indicators:
            if indicator in content.lower() or indicator in course_outline.lower():
                difficulty_level = indicator
                break
        
        # Estimate study time based on content length
        words_count = len(content.split()) + len(course_outline.split())
        estimated_hours = max(2, min(8, words_count // 500))  # Rough estimate
        
        analysis = {
            "topics_identified": topics_identified[:10],  # Limit to most relevant
            "learning_objectives": learning_objectives[:8],
            "content_type": "comprehensive_course_material",
            "difficulty_level": difficulty_level,
            "estimated_hours": estimated_hours,
            "prerequisites": prerequisites[:5],
            "key_concepts": key_concepts[:15],
            "content_structure": {
                "total_lines": len(content_lines) + len(outline_lines),
                "content_sections": len([line for line in content_lines if line.strip() and not line.startswith(' ')]),
                "outline_sections": len([line for line in outline_lines if line.strip() and not line.startswith(' ')])
            },
            "study_recommendations": [
                f"Allocate approximately {estimated_hours} hours for this material",
                f"Difficulty level: {difficulty_level.title()}",
                "Break content into multiple study sessions",
                "Create summary notes for key concepts"
            ]
        }
        
        return {
            "status": "success",
            "analysis": analysis,
            "content_length": len(content),
            "outline_sections": len(course_outline.split('\n')) if course_outline else 0,
            "analysis_summary": f"Identified {len(topics_identified)} topics, {len(learning_objectives)} learning objectives, and {len(key_concepts)} key concepts. Estimated {estimated_hours} hours of study time at {difficulty_level} difficulty level."
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "analysis": {
                "topics_identified": [],
                "learning_objectives": [],
                "content_type": "unknown",
                "difficulty_level": "intermediate",
                "estimated_hours": 2,
                "prerequisites": [],
                "key_concepts": []
            }
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
    Generate a comprehensive study plan for a course with detailed session guides
    
    Args:
        course_id: Course ID to generate plan for
        user_preferences: User study preferences and constraints
        
    Returns:
        Complete study plan with detailed session guides and calendar
    """
    try:
        # Get course information
        course = db.get_course(course_id)
        if not course:
            return {"status": "error", "error": "Course not found"}
        
        # Get existing materials
        materials = db.get_course_materials(course_id)
        
        # Extract course details
        course_data = course.to_dict()
        course_title = course_data.get('title', 'Course')
        course_outline = course_data.get('course_outline', {})
        
        # Generate comprehensive study plan with detailed structure
        study_plan = {
            "course_id": course_id,
            "course_title": course_title,
            "plan_overview": {
                "total_weeks": user_preferences.get("duration_weeks", 12),
                "sessions_per_week": user_preferences.get("sessions_per_week", 3),
                "session_duration": user_preferences.get("session_duration_minutes", 90),
                "preferred_times": user_preferences.get("preferred_times", ["evening"]),
                "content_delivery_schedule": user_preferences.get("content_schedule", "biweekly"),
                "total_sessions": 0,  # Will be calculated
                "start_date": datetime.now().isoformat(),
                "estimated_completion": None  # Will be calculated
            },
            "study_sessions": [],
            "calendar_events": [],
            "content_mapping": {},
            "assessment_schedule": [],
            "review_sessions": [],
            "weekly_breakdown": {}
        }
        
        # Generate individual study sessions with detailed guides
        start_date = datetime.now()
        session_number = 1
        sessions_per_week = user_preferences.get("sessions_per_week", 3)
        preferred_times = user_preferences.get("preferred_times", ["evening"])
        
        # Helper function to create detailed session guide
        def create_session_guide(session_title, material_content=None, week_number=1):
            return {
                "session_overview": {
                    "duration": f"{user_preferences.get('session_duration_minutes', 90)} minutes",
                    "focus_areas": ["Content Review", "Practice & Application", "Summary & Reflection"],
                    "difficulty_level": "Moderate",
                    "preparation_time": "15 minutes"
                },
                "pre_session_preparation": [
                    "Review previous session notes and key concepts",
                    "Gather all required materials and resources",
                    "Set up a distraction-free study environment",
                    "Have note-taking materials ready"
                ],
                "detailed_activities": [
                    {
                        "phase": "Warm-up & Review",
                        "duration": "15 minutes",
                        "activities": [
                            "Quick review of previous session's key points",
                            "Connect new material to prior knowledge",
                            "Set learning objectives for this session"
                        ]
                    },
                    {
                        "phase": "Content Study",
                        "duration": "45 minutes", 
                        "activities": [
                            "Read through new course material carefully",
                            "Take detailed notes using preferred method",
                            "Identify key concepts and terminology",
                            "Create visual aids or diagrams if helpful"
                        ]
                    },
                    {
                        "phase": "Practice & Application",
                        "duration": "20 minutes",
                        "activities": [
                            "Work through practice problems or exercises",
                            "Apply concepts to real-world examples",
                            "Test understanding with self-quiz",
                            "Identify areas needing more review"
                        ]
                    },
                    {
                        "phase": "Summary & Planning",
                        "duration": "10 minutes",
                        "activities": [
                            "Summarize key learning points",
                            "Update study notes and flashcards",
                            "Plan review schedule for this material",
                            "Prepare for next session"
                        ]
                    }
                ],
                "learning_objectives": [
                    f"Master key concepts from {session_title}",
                    "Apply learned concepts to practice problems",
                    "Connect new knowledge to existing understanding",
                    "Identify areas for further study or clarification"
                ],
                "success_criteria": [
                    "Can explain main concepts in own words",
                    "Successfully completed practice exercises",
                    "Created comprehensive study notes",
                    "Identified next steps for learning"
                ],
                "resources_needed": [
                    "Course materials and textbook",
                    "Note-taking supplies or digital tools",
                    "Practice problems or exercises",
                    "Quiet study environment"
                ],
                "homework_assignments": [
                    "Review and organize session notes",
                    "Complete any assigned practice problems",
                    "Prepare questions for next session",
                    "Create flashcards for new terminology"
                ]
            }
        
        # Create sessions based on available materials or course structure
        if materials:
            # Generate sessions based on uploaded materials
            for material in materials:
                # Calculate session date based on preferences
                days_offset = ((session_number - 1) // sessions_per_week) * 7
                if session_number % sessions_per_week == 1:
                    weekday_offset = 0  # Monday
                elif session_number % sessions_per_week == 2:
                    weekday_offset = 2  # Wednesday 
                else:
                    weekday_offset = 4  # Friday
                
                session_date = start_date + timedelta(days=days_offset + weekday_offset)
                
                session = {
                    "session_id": f"session_{session_number}",
                    "session_number": session_number,
                    "title": f"Session {session_number}: {material['title']}",
                    "scheduled_date": session_date.isoformat(),
                    "scheduled_time": preferred_times[0] if preferred_times else "evening",
                    "week_number": ((session_number - 1) // sessions_per_week) + 1,
                    "topics": material.get('topics', [f"Topics from {material['title']}"]),
                    "content_requirements": {
                        "required_materials": [material['id']],
                        "content_status": "uploaded" if material.get('content_text') else "pending",
                        "material_title": material['title'],
                        "estimated_reading_time": "30-45 minutes"
                    },
                    "estimated_duration": user_preferences.get('session_duration_minutes', 90),
                    "session_guide": create_session_guide(material['title'], material.get('content_text'), ((session_number - 1) // sessions_per_week) + 1),
                    "status": "scheduled",
                    "completion_date": None,
                    "notes": "",
                    "calendar_event": {
                        "title": f"Study Session: {material['title']}",
                        "start_time": session_date.replace(hour=19 if "evening" in preferred_times else 9).isoformat(),
                        "duration_minutes": user_preferences.get('session_duration_minutes', 90),
                        "description": f"Study session for {course_title} - {material['title']}"
                    }
                }
                
                study_plan["study_sessions"].append(session)
                study_plan["calendar_events"].append(session["calendar_event"])
                session_number += 1
        else:
            # Create placeholder sessions for future content based on expected delivery schedule
            total_weeks = user_preferences.get("duration_weeks", 12)
            content_delivery_weeks = user_preferences.get("content_schedule", "biweekly")
            
            # Determine how often content is delivered
            if content_delivery_weeks == "weekly":
                delivery_interval = 1
            elif content_delivery_weeks == "biweekly":
                delivery_interval = 2
            else:  # monthly
                delivery_interval = 4
            
            for week in range(1, total_weeks + 1, delivery_interval):
                # Create sessions for each content delivery period
                for session_in_period in range(sessions_per_week):
                    days_offset = (week - 1) * 7 + (session_in_period * 2)
                    session_date = start_date + timedelta(days=days_offset)
                    
                    session = {
                        "session_id": f"session_{session_number}",
                        "session_number": session_number,
                        "title": f"Session {session_number}: Week {week} Content",
                        "scheduled_date": session_date.isoformat(),
                        "scheduled_time": preferred_times[session_in_period % len(preferred_times)] if preferred_times else "evening",
                        "week_number": week,
                        "topics": [f"Week {week} topics (to be updated when content is uploaded)"],
                        "content_requirements": {
                            "required_materials": [],
                            "content_status": "pending",
                            "week_number": week,
                            "expected_content": f"Week {week} course materials"
                        },
                        "estimated_duration": user_preferences.get('session_duration_minutes', 90),
                        "session_guide": create_session_guide(f"Week {week} Content", None, week),
                        "status": "awaiting_content",
                        "completion_date": None,
                        "notes": "Waiting for course content to be uploaded",
                        "calendar_event": {
                            "title": f"Study Session: Week {week} Content",
                            "start_time": session_date.replace(hour=19 if "evening" in preferred_times else 9).isoformat(),
                            "duration_minutes": user_preferences.get('session_duration_minutes', 90),
                            "description": f"Study session for {course_title} - Week {week} content"
                        }
                    }
                    
                    study_plan["study_sessions"].append(session)
                    study_plan["calendar_events"].append(session["calendar_event"])
                    session_number += 1
                    
                    if session_number > total_weeks * sessions_per_week:
                        break
        
        # Finalize plan overview with calculated values
        study_plan["plan_overview"]["total_sessions"] = len(study_plan["study_sessions"])
        if study_plan["study_sessions"]:
            last_session_date = study_plan["study_sessions"][-1]["scheduled_date"]
            study_plan["plan_overview"]["estimated_completion"] = last_session_date
        
        # Create weekly breakdown for calendar view
        for session in study_plan["study_sessions"]:
            week_num = session["week_number"]
            if week_num not in study_plan["weekly_breakdown"]:
                study_plan["weekly_breakdown"][week_num] = {
                    "week_number": week_num,
                    "sessions": [],
                    "total_study_time": 0,
                    "content_status": "pending",
                    "topics_covered": []
                }
            
            study_plan["weekly_breakdown"][week_num]["sessions"].append({
                "session_id": session["session_id"],
                "title": session["title"],
                "scheduled_date": session["scheduled_date"],
                "duration": session["estimated_duration"]
            })
            study_plan["weekly_breakdown"][week_num]["total_study_time"] += session["estimated_duration"]
            study_plan["weekly_breakdown"][week_num]["topics_covered"].extend(session["topics"])
            
            if session["content_requirements"]["content_status"] == "uploaded":
                study_plan["weekly_breakdown"][week_num]["content_status"] = "ready"
        
        # Add assessment and review schedule
        study_plan["assessment_schedule"] = [
            {
                "week": 4,
                "type": "Mid-term Review",
                "description": "Comprehensive review of weeks 1-4",
                "estimated_duration": 120
            },
            {
                "week": 8,
                "type": "Progress Assessment",
                "description": "Skills assessment and knowledge check",
                "estimated_duration": 90
            },
            {
                "week": study_plan["plan_overview"]["total_weeks"],
                "type": "Final Review",
                "description": "Complete course review and preparation",
                "estimated_duration": 180
            }
        ]
        
        # Create the study plan in database
        plan_id = db.create_study_plan(course_id, course.user_id, study_plan)
        
        # Create individual study sessions in database
        for session in study_plan["study_sessions"]:
            db.create_study_session(
                plan_id, course_id, course.user_id,
                session["session_number"], session["title"], session["topics"],
                session["scheduled_date"], session["estimated_duration"],
                session["content_requirements"], 
                json.dumps(session.get("session_guide", {}).get("detailed_activities", []))
            )
        
        # Return comprehensive study plan ready for display
        return {
            "status": "success",
            "study_plan_id": plan_id,
            "study_plan": study_plan,
            "summary": {
                "course_title": course_title,
                "total_sessions": study_plan["plan_overview"]["total_sessions"],
                "total_weeks": study_plan["plan_overview"]["total_weeks"],
                "sessions_per_week": study_plan["plan_overview"]["sessions_per_week"],
                "estimated_total_hours": (study_plan["plan_overview"]["total_sessions"] * 
                                        study_plan["plan_overview"]["session_duration"]) / 60,
                "start_date": study_plan["plan_overview"]["start_date"],
                "completion_date": study_plan["plan_overview"]["estimated_completion"],
                "content_delivery_schedule": study_plan["plan_overview"]["content_delivery_schedule"]
            },
            "display_message": f"""
📚 **{course_title} Study Plan Created Successfully!**

📊 **Plan Overview:**
• **Total Sessions:** {study_plan["plan_overview"]["total_sessions"]} sessions
• **Duration:** {study_plan["plan_overview"]["total_weeks"]} weeks
• **Schedule:** {study_plan["plan_overview"]["sessions_per_week"]} sessions per week
• **Session Length:** {study_plan["plan_overview"]["session_duration"]} minutes each
• **Total Study Time:** {(study_plan["plan_overview"]["total_sessions"] * study_plan["plan_overview"]["session_duration"]) / 60:.1f} hours

🗓️ **Schedule:**
• **Start Date:** {datetime.fromisoformat(study_plan["plan_overview"]["start_date"]).strftime("%B %d, %Y")}
• **Preferred Times:** {", ".join(study_plan["plan_overview"]["preferred_times"])}
• **Content Delivery:** {study_plan["plan_overview"]["content_delivery_schedule"]}

✅ **What's Included:**
• Detailed study guides for each session
• Calendar events with reminders
• Progress tracking and assessments
• Review sessions and milestone checkpoints
• Adaptive scheduling for new content uploads

🎯 **Ready to Start!**
Your personalized study plan is now available in the Study Plans section. Each session includes detailed guides with activities, learning objectives, and success criteria.
            """.strip(),
            "next_steps": [
                "📖 Review your complete study plan in the Study Plans page",
                "📅 Add calendar events to your personal calendar",
                "📚 Start with Session 1 when you're ready",
                "📤 Upload any additional course materials as they become available"
            ],
            "workflow_complete": True
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
