import { useState, useCallback } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  plan?: any[];
  execution_results?: any[];
}

interface AgenticAIState {
  messages: Message[];
  loading: boolean;
  error: string | null;
}

export const useAgenticAI = () => {
  const [state, setState] = useState<AgenticAIState>({
    messages: [],
    loading: false,
    error: null,
  });

  const sendMessage = useCallback(async (content: string) => {
    setState(prev => ({
      ...prev,
      loading: true,
      error: null,
    }));

    // Add user message immediately
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
    }));

    try {
      const response = await fetch('http://localhost:5000/api/chat/orchestrator', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          message: content,
          user_id: 'current_user', // This should come from auth context
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Please log in to continue');
        }
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: data.response || 'I apologize, but I couldn\'t generate a response.',
        timestamp: new Date(),
        plan: data.intent_analysis ? [data.intent_analysis] : undefined,
        execution_results: data.agent_responses ? Object.entries(data.agent_responses).map(([agent, response]) => ({
          task_id: agent,
          status: 'completed',
          result: response,
        })) : undefined,
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        loading: false,
        error: null,
      }));

    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'An unknown error occurred',
      }));

      // Add error message
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: `I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
      }));
    }
  }, []);

  const clearMessages = useCallback(() => {
    setState(prev => ({
      ...prev,
      messages: [],
      error: null,
    }));
  }, []);

  return {
    messages: state.messages,
    loading: state.loading,
    error: state.error,
    sendMessage,
    clearMessages,
  };
};
