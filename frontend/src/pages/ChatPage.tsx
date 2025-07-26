import { AgenticChat } from '../components/AgentChat';

export const ChatPage = () => {
  return (
    <div className="h-[calc(100vh-8rem)]">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          AI Study Assistant
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Chat with your AI-powered study assistant. Ask questions, request flashcards, get study plans, and more!
        </p>
      </div>
      
      <div className="h-[calc(100%-6rem)]">
        <AgenticChat />
      </div>
    </div>
  );
};
