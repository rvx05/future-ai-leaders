"""
Legacy Agent Executor Module
This is a placeholder for backward compatibility
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from . import tools
  # Import our tools module

class AgentExecutor:
    """
    The Executor component of the agent.
    It executes a plan and synthesizes the results into a final response.
    """
    def __init__(self, api_key: Optional[str] = None):
        """Initializes the executor, setting up the Gemini API client and available tools."""
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.available_tools = {
            "search_web": tools.search_web
        }

    def execute_plan(self, plan: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a plan step-by-step.
        """
        execution_results = []
        for step in plan:
            tool_name = step.get("tool")
            tool_args = step.get("args", {})
            
            if tool_name in self.available_tools:
                tool_function = self.available_tools[tool_name]
                try:
                    result = tool_function(**tool_args)
                    execution_results.append({"step": step["step"], "result": result})
                except Exception as e:
                    execution_results.append({"step": step["step"], "error": f"Error executing tool {tool_name}: {e}"})
            else:
                execution_results.append({"step": step["step"], "error": f"Tool '{tool_name}' not found."})
        
        return execution_results

    def synthesize_results(self, results: List[Dict[str, Any]], original_request: str) -> str:
        """
        Uses the LLM to synthesize the execution results into a final, user-friendly response.
        """
        prompt = f"""
        You are a helpful assistant. You have been given the results of a plan that was executed to answer a user's request.
        Synthesize these results into a clear and concise answer for the user.
        
        User Request: "{original_request}"
        Execution Results: {results}
        
        Based on the a final answer to the user's request.
        If the results contain an error, inform the user about the error in a helpful way.
        """
        
        try:
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error synthesizing results: {e}")
            return "I'm sorry, but I encountered an error while trying to generate a final response."
