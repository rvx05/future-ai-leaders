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
      // Mock API calls for development
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      let mockData: any;
      
      switch (endpoint) {
        case '/api/plan':
          mockData = {
            schedule: [
              { date: '2025-01-15', topic: 'Introduction to React', duration: 2 },
              { date: '2025-01-16', topic: 'TypeScript Basics', duration: 1.5 },
              { date: '2025-01-17', topic: 'Component Architecture', duration: 2.5 },
            ],
            totalHours: 20,
            examDate: '2025-02-01',
          };
          break;
        case '/api/flashcards':
          mockData = [
            { id: 1, front: 'What is React?', back: 'A JavaScript library for building user interfaces' },
            { id: 2, front: 'What is JSX?', back: 'A syntax extension for JavaScript that allows HTML-like markup' },
            { id: 3, front: 'What are React Hooks?', back: 'Functions that let you use state and other React features in functional components' },
          ];
          break;
        case '/api/exam':
          mockData = {
            questions: [
              {
                id: 1,
                question: 'What is the virtual DOM in React?',
                options: ['A copy of the real DOM', 'A JavaScript object representation of the DOM', 'A browser API', 'A CSS framework'],
                correct: 1,
                explanation: 'The virtual DOM is a JavaScript representation of the actual DOM that React uses for efficient updates.',
              },
              {
                id: 2,
                question: 'Which hook is used for managing component state?',
                options: ['useEffect', 'useState', 'useContext', 'useCallback'],
                correct: 1,
                explanation: 'useState is the React hook used for managing local component state.',
              },
            ],
          };
          break;
        case '/api/memory':
          mockData = {
            weeklyProgress: 75,
            overallProgress: 60,
            studyStreak: 7,
            totalStudyTime: 45,
          };
          break;
        default:
          mockData = { message: 'Mock API response' };
      }
      
      setState({ data: mockData, loading: false, error: null });
      return mockData;
    } catch (error) {
      setState({ data: null, loading: false, error: (error as Error).message });
      throw error;
    }
  }, []);

  return { ...state, callApi };
};