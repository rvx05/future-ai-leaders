"""
Agent Memory Module
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class AgentMemory:
    """
    Handles memory storage and retrieval for the agentic AI.
    Stores conversation history and provides context for new interactions.
    """

    def __init__(self, memory_file: str = "agent_memory.json"):
        """Initialize memory with optional persistent storage."""
        self.memory_file = memory_file
        self.history = []
        self._load_memory()

    def _load_memory(self):
        """Load memory from the specified JSON file if it exists."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load memory file. Starting fresh. Error: {e}")
                self.history = []

    def _save_memory(self):
        """Save the current memory state to the JSON file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save memory file. Error: {e}")

    def store_interaction(self, user_input: str, agent_response: str,
                          plan: Optional[List[Dict[str, Any]]] = None,
                          execution_results: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Store a complete user-agent interaction in memory and save it.
        """
        interaction = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_input': user_input,
            'agent_response': agent_response,
            'plan': plan or [],
            'execution_results': execution_results or []
        }
        self.history.append(interaction)
        self._save_memory()

    def get_relevant_context(self, user_input: str, max_items: int = 5) -> Dict[str, Any]:
        """
        Retrieve the most recent interactions to serve as context.
        For a true MVP, this is a simple 'last N' retrieval.
        """
        # The user_input is not used in this simple implementation,
        # but is kept for future, more advanced semantic search.
        recent_history = self.history[-max_items:]
        return {
            "conversation_history": recent_history
        }

    def get_memory_summary(self) -> Dict[str, Any]:
        """Return a high-level summary of the memory's state."""
        return {
            "total_interactions": len(self.history),
            "last_interaction_timestamp": self.history[-1]['timestamp'] if self.history else None
        }

    def clear_session_memory(self) -> None:
        """
        Reset the in-memory history and clears the memory file.
        """
        self.history = []
        self._save_memory()
