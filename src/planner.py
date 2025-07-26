"""
Planner Module Stub
Define task planning interface for Agentic AI.
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional

class AgentPlanner:
    """
    The Planner component of the agent. 
    It uses an LLM to break down a user's request into a series of steps (a plan).
    """
    def __init__(self, api_key: Optional[str] = None):
        """Initializes the planner, setting up the Gemini API client."""
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def create_plan(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generates a plan based on the user's input.
        For this MVP, it creates a simple, single-step plan if it detects a search intent.
        """
        prompt = f"""
        You are a helpful assistant that creates a plan to answer a user's request.
        The only tool you have available is a web search tool called 'search_web'.
        
        User Request: "{user_input}"
        
        Based on the user's request, should you use the 'search_web' tool? 
        If yes, what is the best query for the search?
        
        Respond with a JSON object containing two keys:
        1. "plan": A list of dictionaries, where each dictionary is a step in the plan.
        2. "reasoning": A brief explanation of your decision.
        
        A plan step should have the following keys:
        - "step": An integer representing the step number.
        - "tool": The name of the tool to use (e.g., "search_web").
        - "args": A dictionary of arguments for the tool. For 'search_web', the only argument is 'query'.
        
        If the search tool is not needed, return an empty list for the "plan".
        
        Example for a search-related request:
        User Request: "Search for the latest news on AI."
        {{
            "plan": [
                {{
                    "step": 1,
                    "tool": "search_web",
                    "args": {{"query": "latest news on AI"}}
                }}
            ],
            "reasoning": "The user explicitly asked to search for something, so I will use the search_web tool."
        }}

        Example for a non-search request:
        User Request: "Hello, how are you?"
        {{
            "plan": [],
            "reasoning": "The user is just greeting me, so no tools are needed."
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            # Simple parsing, assuming the model follows instructions.
            # For a production system, this would need more robust JSON parsing and error handling.
            import json
            plan_data = json.loads(response.text.strip('` \njson'))
            return plan_data.get('plan', [])
        except Exception as e:
            print(f"Error creating plan: {e}")
            return []

    def optimize_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        For this MVP, the plan is simple and doesn't require optimization.
        This is a placeholder for more complex future logic.
        """
        return plan

