import { useState, useCallback } from 'react';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export const useApi = <T>() => {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const callApi = useCallback(async (endpoint: string, options?: RequestInit) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const response = await fetch(`http://localhost:5000${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        credentials: 'include', // Include cookies for authentication
        ...options,
      });

      if (!response.ok) {
        if (response.status === 401) {
          setState({ data: null, loading: false, error: 'Authentication required' });
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      setState({ data: null, loading: false, error: (error as Error).message });
      throw error;
    }
  }, []);

  return { ...state, callApi };
};