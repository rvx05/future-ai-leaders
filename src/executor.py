"""
Legacy Agent Executor Module
This is a placeholder for backward compatibility
"""

class AgentExecutor:
    def __init__(self, api_key=None):
        self.api_key = api_key
        print("AgentExecutor initialized (legacy compatibility)")
    
    def execute(self, plan):
        """Legacy execution method"""
        return f"Legacy execution result for: {plan}"
