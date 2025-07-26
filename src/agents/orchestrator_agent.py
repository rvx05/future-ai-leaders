"""
Orchestrator Agent - Educational Buddy
Main coordination agent that uses Google's Agent Development Kit to coordinate sub-agents
"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .knowledge_base_agent import knowledge_base_agent
from .research_agent import research_agent


def _get_instruction_prompt() -> str:
    """Get the instruction prompt for the Orchestrator Agent"""
    return """
You are the Orchestrator Agent for an Educational Buddy system. Your primary role is to:

1. Analyze incoming student messages and determine appropriate actions
2. Coordinate between Knowledge Base Agent and Research Agent using Agent-to-Agent protocol
3. Provide comprehensive educational assistance combining stored knowledge and external research
4. Help students with study planning, flashcards, quizzes, and course materials

DECISION MATRIX:
- Use Knowledge Base Agent for: student profiles, course materials, quiz history, study progress, stored content
- Use Research Agent for: current developments, real-world examples, external information, web research
- Use both agents when: comprehensive answers require both stored knowledge and current information

WORKFLOW:
1. Analyze the student's message to understand intent
2. Determine which agents to involve based on the request type
3. Coordinate agent communications using A2A protocol
4. Synthesize responses from multiple agents
5. Provide clear, educational responses with proper citations

AGENT COMMUNICATION:
- Delegate specific tasks to Knowledge Agent: "retrieve course material", "get student context", "store study session"
- Delegate research tasks to Research Agent: "find current examples", "research topic", "get developments"
- Combine results when both internal knowledge and external research are needed

Always provide helpful, accurate educational assistance while being encouraging and supportive.
"""

# Create the main orchestrator agent using Google ADK
orchestrator_agent = Agent(
    name="orchestrator_agent",
    model="gemini-2.0-flash",
    description=(
        "analyzing student queries, coordinating between knowledge base and research agents, "
        "providing comprehensive educational assistance, generating study materials, "
        "and helping students with personalized learning experiences"
    ),
    instruction=_get_instruction_prompt(),
    output_key="educational_response",
    tools=[
        AgentTool(agent=knowledge_base_agent),
        AgentTool(agent=research_agent),
    ],
)

# Export the agent as the default
root_agent = orchestrator_agent
