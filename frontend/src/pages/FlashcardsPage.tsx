import React, { useState, useEffect } from 'react';
import { FlashcardViewer } from '../components/FlashcardViewer';
import { Plus, RefreshCw, Download, Upload } from 'lucide-react';
import { useApi } from '../hooks/useApi';

export const FlashcardsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'generate' | 'review' | 'import'>('review');
  const { data: flashcards, loading, callApi } = useApi<Array<{
    id: number;
    front: string;
    back: string;
  }>>();

  useEffect(() => {
    callApi('/api/flashcards');
  }, [callApi]);

  const tabs = [
    { id: 'review' as const, label: 'Review Existing', icon: RefreshCw },
    { id: 'generate' as const, label: 'Generate New', icon: Plus },
    { id: 'import' as const, label: 'Import/Export', icon: Upload },
  ];

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Boost Your Memory with Flashcards
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Create, review, and master your subjects with a little help from your AI buddy.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors flex-1 justify-center ${
              activeTab === tab.id
                ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'review' && (
        <div className="space-y-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Loading flashcards...</p>
            </div>
          ) : flashcards && flashcards.length > 0 ? (
            <FlashcardViewer flashcards={flashcards} />
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400">No flashcards available. Generate some first!</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'generate' && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Generate New Flashcards</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Course/Topic
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="e.g., React Fundamentals, Calculus Chapter 3"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Number of Cards
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
                <option value="10">10 cards</option>
                <option value="20">20 cards</option>
                <option value="30">30 cards</option>
                <option value="50">50 cards</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Difficulty Level
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors">
              Generate Flashcards
            </button>
          </div>
        </div>
      )}

      {activeTab === 'import' && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Import/Export Flashcards</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Import</h3>
              
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400 mb-2">
                  Drop your Anki deck file here or click to browse
                </p>
                <input type="file" className="hidden" accept=".apkg,.txt,.csv" />
                <button className="text-blue-600 hover:text-blue-700 font-medium">
                  Choose File
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Export</h3>
              
              <div className="space-y-3">
                <button className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-gray-300 text-gray-600 dark:text-gray-400 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700">
                  <Download className="h-4 w-4" />
                  <span>Export as Anki Deck</span>
                </button>
                
                <button className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-gray-300 text-gray-600 dark:text-gray-400 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700">
                  <Download className="h-4 w-4" />
                  <span>Export as CSV</span>
                </button>
                
                <button className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-gray-300 text-gray-600 dark:text-gray-400 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700">
                  <Download className="h-4 w-4" />
                  <span>Export as PDF</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};