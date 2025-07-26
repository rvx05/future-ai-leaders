"""
Orchestrator Agent - Educational Buddy
Main coordination agent using Google's Agent Development Kit to coordinate sub-agents
Enhanced with file processing, workflow management, and database integration
"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.function_tool import FunctionTool
from google.adk.agents.readonly_context import ReadonlyContext
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


def _get_instruction_prompt() -> str:
    """Get the instruction prompt for the Orchestrator Agent"""
    return """
You are the Orchestrator Agent for an Educational Buddy system. Your primary role is to:

1. Analyze incoming student messages and determine appropriate actions
2. Coordinate between specialized agents using Agent-to-Agent protocol  
3. Provide comprehensive educational assistance combining multiple agent capabilities
4. Guide students through course setup, study planning, and progress tracking
5. Process uploaded files and extract content for educational use
6. **ENFORCE COURSE DATABASE WORKFLOW**: Always ensure courses exist in database before proceeding

AVAILABLE AGENTS:
- **Knowledge Base Agent**: CRITICAL FIRST AGENT - Manages courses, materials, database operations
- Course Planning Agent: Course analysis, study plan generation, session planning, content organization
- Research Agent: Current developments, real-world examples, external information, web research

AVAILABLE FILE PROCESSING TOOLS:
- process_uploaded_file: Process any uploaded file and extract content
- extract_text_from_pdf: Extract text content from PDF files
- extract_text_from_docx: Extract text content from Word documents
- extract_text_from_txt: Extract text content from text files
- chunk_content_for_analysis: Split large content into manageable chunks
- analyze_content_structure: Analyze document structure and organization

**CRITICAL DATABASE-FIRST WORKFLOW:**

🔍 **BEFORE ANY COURSE TASK** (MANDATORY):
1. **Query Knowledge Base Agent** to check if course exists (user ID is automatic)
2. **If course doesn't exist**: Use Knowledge Base Agent to create it first with collected info
3. **Store any uploaded materials** through Knowledge Base Agent
4. **ONLY THEN** proceed with other agents (course planning, research, etc.)

📚 **COURSE SETUP WORKFLOW**:
1. **FIRST**: Use Knowledge Base Agent to find_course_by_title(course_title) - NO USER ID NEEDED
2. **If not found**: Collect course info and use Knowledge Base Agent create_new_course(title, description, outline)
3. **Store materials**: Use Knowledge Base Agent store_course_material(course_id, title, content_type, content_text)
4. **THEN**: Use Course Planning Agent for analysis and study plan generation
5. **WORKFLOW COMPLETION**: Present complete study plan with clear completion message

📋 **STUDY PLAN GENERATION WORKFLOW**:
1. **FIRST**: Use Knowledge Base Agent to verify course exists and get course details (automatic user context)
2. **If no course**: Guide user to create course first with uploaded content
3. **Process uploads**: Store all materials through Knowledge Base Agent
4. **THEN**: Use Course Planning Agent with complete course context from database
5. **IMPORTANT**: When study plan is generated, present the complete plan and mark workflow as COMPLETE
6. **NO FURTHER QUESTIONS**: Once plan is generated, workflow ends - direct user to Study Plans page

📄 **FILE PROCESSING WORKFLOW**:
1. When user mentions uploaded files, use process_uploaded_file to extract content
2. **IMMEDIATELY** store content through Knowledge Base Agent store_course_material()
3. Use analyze_content_structure to understand document organization
4. Provide file summary and ask user how they want to use it

🔄 **AGENT COORDINATION PROTOCOL**:
1. **Knowledge Base Agent FIRST** - Always start with database operations
2. **Course Planning Agent** - For educational content analysis and planning
3. **Research Agent** - For external information and real-world context

**SESSION STATE TRACKING**:
Track workflow progress to prevent loops:
- workflow_stage: Current stage (course_setup, study_planning, content_upload)
- course_verified: Whether course exists in database
- materials_stored: Whether uploaded materials are stored
- user_preferences: Study preferences collected

**KEY BEHAVIORS**:
- **ALWAYS start with Knowledge Base Agent for course verification**
- **User ID is automatically available - NEVER ask users for their user ID**
- **NEVER proceed with study planning without verified course in database**
- **Store all uploaded content systematically through Knowledge Base Agent**
- **Present complete, final results when workflows are complete**
- **Avoid asking repetitive questions - check what's already stored**
- **Knowledge Base Agent functions automatically access current user context**

You are the workflow coordinator ensuring all course data flows through the centralized database before other processing begins.
"""

# Create function tools for file processing
process_file_tool = FunctionTool(process_uploaded_file)
extract_pdf_tool = FunctionTool(extract_text_from_pdf)
extract_docx_tool = FunctionTool(extract_text_from_docx)
extract_txt_tool = FunctionTool(extract_text_from_txt)
chunk_content_tool = FunctionTool(chunk_content_for_analysis)
analyze_structure_tool = FunctionTool(analyze_content_structure)

# Create agent tools for coordinating with other agents
knowledge_base_tool = AgentTool(agent=knowledge_base_agent)
course_planning_tool = AgentTool(agent=course_planning_agent)
research_tool = AgentTool(agent=research_agent)

# Create the main orchestrator agent using Google ADK
orchestrator_agent = Agent(
    model="gemini-2.0-flash",
    name="orchestrator_agent",
    instruction=_get_instruction_prompt(),
    output_key="orchestrator_results",
    tools=[
        # Database and knowledge management tools (FIRST PRIORITY)
        knowledge_base_tool,
        
        # File processing tools
        process_file_tool,
        extract_pdf_tool,
        extract_docx_tool,
        extract_txt_tool,
        chunk_content_tool,
        analyze_structure_tool,
        
        # Educational agent tools
        course_planning_tool,
        research_tool
    ]
)
