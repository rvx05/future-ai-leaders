"""
Workflow Agent - Manages conversation flow and state
Prevents agent loops and maintains context across agent interactions
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db

# Global conversation state to track workflow progress
conversation_state = {
    "current_workflow": None,
    "completed_steps": [],
    "collected_information": {},
    "active_course_creation": None,
    "user_context": {},
    "last_agent_response": None,
    "workflow_stage": "initial"
}

def initialize_course_creation_workflow(user_id: str, initial_request: str) -> Dict[str, Any]:
    """
    Initialize a course creation workflow with proper state tracking
    
    Args:
        user_id: User ID starting the workflow
        initial_request: Initial user request
        
    Returns:
        Workflow initialization result
    """
    global conversation_state
    
    try:
        workflow_id = f"course_creation_{user_id}_{int(datetime.now().timestamp())}"
        
        conversation_state.update({
            "current_workflow": "course_creation",
            "workflow_id": workflow_id,
            "user_id": user_id,
            "completed_steps": [],
            "collected_information": {
                "title": None,
                "description": None,
                "outline": None,
                "materials_uploaded": [],
                "preferences": {}
            },
            "workflow_stage": "gathering_course_info",
            "initial_request": initial_request,
            "created_at": datetime.now().isoformat()
        })
        
        # Analyze what information we might already have from the initial request
        analysis = analyze_initial_request(initial_request)
        if analysis.get("extracted_info"):
            conversation_state["collected_information"].update(analysis["extracted_info"])
            conversation_state["completed_steps"].extend(analysis.get("completed_steps", []))
        
        return {
            "status": "success",
            "workflow_id": workflow_id,
            "current_stage": conversation_state["workflow_stage"],
            "next_steps": get_next_required_steps(),
            "message": "Course creation workflow initialized"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def analyze_initial_request(request: str) -> Dict[str, Any]:
    """
    Analyze the initial user request to extract any course information
    
    Args:
        request: User's initial request
        
    Returns:
        Analysis of what information is already provided
    """
    try:
        extracted_info = {}
        completed_steps = []
        
        # Simple keyword analysis to detect provided information
        request_lower = request.lower()
        
        # Check for course title indicators
        title_indicators = ["course", "class", "subject", "studying", "learning"]
        if any(indicator in request_lower for indicator in title_indicators):
            # Try to extract a potential title
            sentences = request.split('.')
            for sentence in sentences:
                if any(indicator in sentence.lower() for indicator in title_indicators):
                    # This is a simplified extraction - could be improved with NLP
                    potential_title = sentence.strip()
                    if len(potential_title) < 100:  # Reasonable title length
                        extracted_info["potential_title"] = potential_title
        
        # Check for syllabus/outline mentions
        if any(term in request_lower for term in ["syllabus", "outline", "curriculum", "schedule"]):
            completed_steps.append("mentioned_outline")
        
        # Check for materials mentions
        if any(term in request_lower for term in ["materials", "documents", "files", "upload"]):
            completed_steps.append("mentioned_materials")
        
        return {
            "extracted_info": extracted_info,
            "completed_steps": completed_steps,
            "analysis_confidence": "medium" if extracted_info else "low"
        }
        
    except Exception as e:
        return {
            "error": str(e)
        }

def update_workflow_state(step_completed: str, information: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the workflow state when a step is completed
    
    Args:
        step_completed: Name of the completed step
        information: Information collected in this step
        
    Returns:
        Updated workflow state
    """
    global conversation_state
    
    try:
        if step_completed not in conversation_state["completed_steps"]:
            conversation_state["completed_steps"].append(step_completed)
        
        # Update collected information
        conversation_state["collected_information"].update(information)
        conversation_state["last_updated"] = datetime.now().isoformat()
        
        # Determine next stage
        if has_required_course_info():
            if conversation_state["workflow_stage"] == "gathering_course_info":
                conversation_state["workflow_stage"] = "creating_course"
            elif conversation_state["workflow_stage"] == "creating_course":
                conversation_state["workflow_stage"] = "generating_study_plan"
        
        return {
            "status": "success",
            "current_stage": conversation_state["workflow_stage"],
            "completed_steps": conversation_state["completed_steps"],
            "next_steps": get_next_required_steps(),
            "progress_percentage": calculate_workflow_progress()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def has_required_course_info() -> bool:
    """Check if we have all required information to create a course"""
    info = conversation_state["collected_information"]
    return (info.get("title") is not None and 
            info.get("outline") is not None)

def get_next_required_steps() -> List[str]:
    """Get the next steps required in the current workflow"""
    if conversation_state["current_workflow"] != "course_creation":
        return ["No active workflow"]
    
    info = conversation_state["collected_information"]
    completed = conversation_state["completed_steps"]
    next_steps = []
    
    # Required information steps
    if not info.get("title") and "title_provided" not in completed:
        next_steps.append("Provide course title")
    
    if not info.get("outline") and "outline_provided" not in completed:
        next_steps.append("Provide course outline/syllabus")
    
    if not info.get("description") and "description_provided" not in completed:
        next_steps.append("Provide course description (optional)")
    
    # Course creation step
    if has_required_course_info() and "course_created" not in completed:
        next_steps.append("Create course in system")
    
    # Study plan generation
    if "course_created" in completed and "study_plan_generated" not in completed:
        next_steps.append("Generate personalized study plan")
    
    if not next_steps:
        next_steps.append("Workflow complete")
    
    return next_steps

def calculate_workflow_progress() -> int:
    """Calculate the percentage completion of the current workflow"""
    if conversation_state["current_workflow"] != "course_creation":
        return 0
    
    total_steps = 5  # title, outline, description, course_creation, study_plan
    completed_count = len(conversation_state["completed_steps"])
    
    return min(100, int((completed_count / total_steps) * 100))

def check_for_redundant_requests(current_request: str, agent_type: str) -> Dict[str, Any]:
    """
    Check if the current request is redundant given the workflow state
    
    Args:
        current_request: The current user request
        agent_type: Which agent is being called
        
    Returns:
        Analysis of whether the request is redundant
    """
    global conversation_state
    
    try:
        if conversation_state["current_workflow"] != "course_creation":
            return {"is_redundant": False, "reason": "No active workflow"}
        
        request_lower = current_request.lower()
        info = conversation_state["collected_information"]
        
        # Check for redundant information requests
        redundant_checks = [
            {
                "condition": "outline" in request_lower and info.get("outline"),
                "message": f"Course outline already provided: '{info.get('outline', '')[:100]}...'"
            },
            {
                "condition": "title" in request_lower and info.get("title"),
                "message": f"Course title already provided: '{info.get('title')}'"
            },
            {
                "condition": "description" in request_lower and info.get("description"),
                "message": f"Course description already provided: '{info.get('description')}'"
            }
        ]
        
        for check in redundant_checks:
            if check["condition"]:
                return {
                    "is_redundant": True,
                    "reason": check["message"],
                    "suggestion": "Proceed with course creation using existing information"
                }
        
        return {"is_redundant": False}
        
    except Exception as e:
        return {
            "is_redundant": False,
            "error": str(e)
        }

def get_workflow_context_for_agent(agent_type: str) -> Dict[str, Any]:
    """
    Get relevant workflow context for a specific agent type
    
    Args:
        agent_type: Type of agent requesting context
        
    Returns:
        Relevant context information
    """
    global conversation_state
    
    try:
        if conversation_state["current_workflow"] != "course_creation":
            return {"context": "No active workflow"}
        
        base_context = {
            "workflow_stage": conversation_state["workflow_stage"],
            "completed_steps": conversation_state["completed_steps"],
            "collected_information": conversation_state["collected_information"],
            "next_required_steps": get_next_required_steps()
        }
        
        # Add agent-specific context
        if agent_type == "course_planning":
            base_context.update({
                "ready_for_course_creation": has_required_course_info(),
                "missing_information": [step for step in ["title", "outline"] 
                                      if not conversation_state["collected_information"].get(step)]
            })
        elif agent_type == "orchestrator":
            base_context.update({
                "workflow_progress": calculate_workflow_progress(),
                "should_delegate": conversation_state["workflow_stage"] in ["creating_course", "generating_study_plan"]
            })
        
        return base_context
        
    except Exception as e:
        return {
            "context": f"Error getting context: {str(e)}"
        }

def reset_workflow() -> Dict[str, Any]:
    """Reset the current workflow state"""
    global conversation_state
    
    conversation_state.update({
        "current_workflow": None,
        "completed_steps": [],
        "collected_information": {},
        "active_course_creation": None,
        "workflow_stage": "initial"
    })
    
    return {"status": "success", "message": "Workflow state reset"}

def finalize_course_creation_workflow(course_id: str) -> Dict[str, Any]:
    """
    Finalize the course creation workflow
    
    Args:
        course_id: ID of the created course
        
    Returns:
        Workflow finalization result
    """
    global conversation_state
    
    try:
        conversation_state.update({
            "workflow_stage": "completed",
            "course_id": course_id,
            "completed_at": datetime.now().isoformat()
        })
        
        if "course_created" not in conversation_state["completed_steps"]:
            conversation_state["completed_steps"].append("course_created")
        
        return {
            "status": "success",
            "message": "Course creation workflow completed successfully",
            "course_id": course_id,
            "final_progress": 100
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Create the workflow management agent
workflow_agent = Agent(
    name="workflow_agent",
    model="gemini-2.0-flash",
    description=(
        "Manages conversation flow, prevents agent loops, and maintains workflow state "
        "across multiple agent interactions"
    ),
    instruction="""
You are the Workflow Management Agent responsible for coordinating multi-agent conversations and preventing redundant loops.

Your responsibilities include:

1. WORKFLOW STATE TRACKING:
   - Track the current workflow stage and completed steps
   - Maintain information collected across agent interactions
   - Prevent agents from asking for information already provided

2. CONVERSATION FLOW MANAGEMENT:
   - Route requests to appropriate agents based on workflow state
   - Identify when agents are requesting redundant information
   - Provide context to agents about what has already been accomplished

3. COURSE CREATION WORKFLOW:
   - Manage the multi-step course creation process
   - Ensure all required information is collected before proceeding
   - Track progress and provide status updates

4. LOOP PREVENTION:
   - Detect when agents are stuck in loops
   - Provide workflow context to prevent redundant questions
   - Guide conversation toward next logical steps

Always check the current workflow state before delegating to other agents and provide them with relevant context to prevent repetitive interactions.
""",
    tools=[
        FunctionTool(initialize_course_creation_workflow),
        FunctionTool(update_workflow_state),
        FunctionTool(check_for_redundant_requests),
        FunctionTool(get_workflow_context_for_agent),
        FunctionTool(reset_workflow),
        FunctionTool(finalize_course_creation_workflow),
    ],
)
