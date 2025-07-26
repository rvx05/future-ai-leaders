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

  const sendMessage = useCallback(async (content: string, files?: File[]) => {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:5001";

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
      // Handle file uploads first if present
      if (files && files.length > 0) {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));

        const uploadResponse = await fetch(`${apiBaseUrl}/api/upload/chat`, {
          method: 'POST',
          credentials: 'include',
          body: formData,
        });

        if (!uploadResponse.ok) {
          throw new Error(`File upload failed: ${uploadResponse.status}`);
        }

        const uploadData = await uploadResponse.json();
        console.log('Files uploaded:', uploadData);
        
        // Update content to include file upload information
        content = `${content}\n\nFiles uploaded: ${files.map(f => f.name).join(', ')}`;
      }

      const response = await fetch(`${apiBaseUrl}/api/chat/orchestrator`, {
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

    } catch (err: any) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err.message || 'An unexpected error occurred.',
      }));

      // Add error message
      const errorMessage: Message = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: `I encountered an error: ${err.message || 'Unknown error'}`,
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

