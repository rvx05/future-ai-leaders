"""
Legacy Agent Memory Module
This is a placeholder for backward compatibility
"""

class AgentMemory:
    def __init__(self):
        self.memory = {}
        print("AgentMemory initialized (legacy compatibility)")
    
    def store(self, key, value):
        """Store value in memory"""
        self.memory[key] = value
        return f"Stored {key}: {value}"
    
    def retrieve(self, key):
        """Retrieve value from memory"""
        return self.memory.get(key, None)
