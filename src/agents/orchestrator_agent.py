"""
Orchestrator Agent - Educational Buddy
Main coordination agent that uses Google's Agent Development Kit to coordinate sub-agents
Enhanced with file processing and workflow management
"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.function_tool import FunctionTool
import sys
import os

# Add tools path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .knowledge_base_agent import knowledge_base_agent
from .research_agent import research_agent
from .course_planning_agent import course_planning_agent

# Import file processing tools
from tools.file_ingestion_tools import (
    process_uploaded_file,
    extract_text_from_pdf,
    extract_text_from_docx, 
    extract_text_from_txt,
    chunk_content_for_analysis,
    analyze_content_structure
)

# Simple state management to prevent loops
conversation_state = {
    "last_action": None,
    "collected_info": {},
    "file_contents": {},
    "current_workflow": None
}

def manage_conversation_state(action: str, info: dict = None) -> dict:
    """Simple function to manage conversation state and prevent loops"""
    global conversation_state
    
    if action == "store_file_content":
        if info and "filename" in info and "content" in info:
            conversation_state["file_contents"][info["filename"]] = info["content"]
            return {"status": "success", "message": f"Stored content for {info['filename']}"}
    
    elif action == "get_file_content":
        filename = info.get("filename") if info else None
        if filename and filename in conversation_state["file_contents"]:
            return {"status": "success", "content": conversation_state["file_contents"][filename]}
        return {"status": "error", "message": "File content not found"}
    
    elif action == "check_workflow":
        return {
            "current_workflow": conversation_state.get("current_workflow"),
            "collected_info": conversation_state.get("collected_info", {}),
            "last_action": conversation_state.get("last_action")
        }
    
    elif action == "update_workflow":
        if info:
            conversation_state["current_workflow"] = info.get("workflow")
            conversation_state["collected_info"].update(info.get("info", {}))
            conversation_state["last_action"] = info.get("action")
        return {"status": "success"}
    
    return {"status": "error", "message": "Unknown action"}


def _get_instruction_prompt() -> str:
    """Get the instruction prompt for the Orchestrator Agent"""
    return """
You are the Orchestrator Agent for an Educational Buddy system. Your primary role is to:

1. Analyze incoming student messages and determine appropriate actions
2. Coordinate between specialized agents using Agent-to-Agent protocol
3. Provide comprehensive educational assistance combining multiple agent capabilities
4. Guide students through course setup, study planning, and progress tracking
5. Process uploaded files and extract content for educational use
6. Manage conversation workflows to prevent redundant loops

AVAILABLE AGENTS:
- Course Planning Agent: Course analysis, study plan generation, session planning, content organization
- Knowledge Base Agent: Student profiles, course materials, quiz history, study progress, stored content
- Research Agent: Current developments, real-world examples, external information, web research

AVAILABLE FILE PROCESSING TOOLS:
- process_uploaded_file: Process any uploaded file and extract content (USE THIS FIRST when files are mentioned)
- extract_text_from_pdf: Extract text content from PDF files
- extract_text_from_docx: Extract text content from Word documents
- extract_text_from_txt: Extract text content from text files
- chunk_content_for_analysis: Split large content into manageable chunks
- analyze_content_structure: Analyze document structure and organization

AVAILABLE STATE MANAGEMENT TOOLS:
- manage_conversation_state: Store/retrieve file content and workflow state

CORE WORKFLOWS:

� FILE PROCESSING WORKFLOW (CRITICAL - DO THIS FIRST):
1. When user mentions uploaded files, IMMEDIATELY use process_uploaded_file to extract content
2. Store the extracted content using manage_conversation_state with action="store_file_content"
3. Use analyze_content_structure to understand document organization
4. If content is large, use chunk_content_for_analysis for manageable processing
5. Once processed, inform user about the file contents and ask how they want to use it

📚 COURSE SETUP WORKFLOW:
1. Check current workflow state using manage_conversation_state with action="check_workflow"
2. Collect required information (avoid asking for information already provided):
   - Course title
   - Course outline/syllabus  
   - Course description (optional)
3. Use Course Planning Agent to analyze and create course structure
4. Guide student through preference questions (study frequency, preferred times, etc.)
5. Generate comprehensive study plan with scheduled sessions

� RESEARCH WORKFLOW:
1. If user uploads research plans or documents, process them first with file tools
2. Extract research objectives and methodology from documents
3. Use Research Agent to conduct the research following the uploaded plan
4. Provide comprehensive research results with citations and examples

📊 STUDY SESSION WORKFLOW:
1. Student starts a study session
2. Use Course Planning Agent to provide detailed session guide
3. Track session completion and validation
4. Update progress and plan next sessions

CONVERSATION MANAGEMENT:
- Use manage_conversation_state to track workflow progress and avoid asking for information already provided
- When files are mentioned, ALWAYS process them first before proceeding
- Guide users through logical next steps without loops
- Check conversation state before asking questions

💬 AGENT DELEGATION RULES:
- Use Knowledge Base Agent for: storing/retrieving student data, course materials, progress tracking
- Use Research Agent for: current information, examples, explanations, conducting research
- Use Course Planning Agent for: anything related to courses, study plans, session guidance
- ALWAYS process uploaded files first before delegating to other agents

INTERACTION STYLE:
- Be conversational and encouraging
- Ask clarifying questions to understand student needs
- When files are uploaded, acknowledge them immediately and process them
- Provide step-by-step guidance for complex tasks
- Always explain what you're doing and why

CRITICAL FILE HANDLING:
- When user says "Files uploaded:" or mentions uploaded documents, IMMEDIATELY use process_uploaded_file
- Extract the content and store it before proceeding with any other actions
- Let the user know you've successfully processed their files and what you found

The system is designed around the concept that students receive course content periodically (e.g., every 2 weeks) and need adaptive study plans that account for both uploaded content and future content expectations.
"""

# Create the main orchestrator agent using Google ADK
orchestrator_agent = Agent(
    name="orchestrator_agent",
    model="gemini-2.0-flash",
    description=(
        "analyzing student queries, coordinating between specialized agents including course planning, "
        "knowledge management, and research agents to provide comprehensive educational assistance, "
        "study plan generation, and personalized learning experiences with file processing and workflow management"
    ),
    instruction=_get_instruction_prompt(),
    output_key="educational_response",
    tools=[
        # Agent coordination tools
        AgentTool(agent=course_planning_agent),
        AgentTool(agent=knowledge_base_agent),
        AgentTool(agent=research_agent),
        
        # State management tools
        FunctionTool(manage_conversation_state),
        
        # File processing tools
        FunctionTool(process_uploaded_file),
        FunctionTool(extract_text_from_pdf),
        FunctionTool(extract_text_from_docx),
        FunctionTool(extract_text_from_txt),
        FunctionTool(chunk_content_for_analysis),
        FunctionTool(analyze_content_structure),
    ],
)

# Export the agent as the default
root_agent = orchestrator_agent
