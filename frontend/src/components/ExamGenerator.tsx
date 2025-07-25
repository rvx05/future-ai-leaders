import React, { useState } from 'react';
import { Clock, CheckCircle, XCircle, RotateCcw, Save } from 'lucide-react';
import { useApi } from '../hooks/useApi';

interface Question {
  id: number;
  question: string;
  options: string[];
  correct: number;
  explanation: string;
}

interface ExamData {
  questions: Question[];
}

interface ExamGeneratorProps {
  onExamGenerated: (exam: ExamData) => void;
}

export const ExamGenerator: React.FC<ExamGeneratorProps> = ({ onExamGenerated }) => {
  const [examConfig, setExamConfig] = useState({
    topics: [] as string[],
    questionCount: 10,
    difficulty: 'intermediate',
    timeLimit: 30,
  });
  const [currentExam, setCurrentExam] = useState<ExamData | null>(null);
  const [userAnswers, setUserAnswers] = useState<Record<number, number>>({});
  const [showResults, setShowResults] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const { data, loading, callApi } = useApi<ExamData>();

  const availableTopics = [
    'React Fundamentals',
    'JavaScript ES6+',
    'TypeScript',
    'CSS & Styling',
    'State Management',
    'API Integration',
    'Testing',
    'Performance Optimization',
  ];

  const generateExam = async () => {
    const exam = await callApi('/api/exam');
    if (exam) {
      setCurrentExam(exam);
      setUserAnswers({});
      setShowResults(false);
      setTimeRemaining(examConfig.timeLimit * 60); // Convert to seconds
      onExamGenerated(exam);
    }
  };

  const submitExam = () => {
    setShowResults(true);
    setTimeRemaining(null);
  };

  const resetExam = () => {
    setCurrentExam(null);
    setUserAnswers({});
    setShowResults(false);
    setTimeRemaining(null);
  };

  const handleTopicToggle = (topic: string) => {
    setExamConfig(prev => ({
      ...prev,
      topics: prev.topics.includes(topic)
        ? prev.topics.filter(t => t !== topic)
        : [...prev.topics, topic]
    }));
  };

  const calculateScore = () => {
    if (!currentExam) return 0;
    const correct = currentExam.questions.reduce((count, question) => {
      return userAnswers[question.id] === question.correct ? count + 1 : count;
    }, 0);
    return Math.round((correct / currentExam.questions.length) * 100);
  };

  // Timer effect would go here in a real implementation

  if (!currentExam) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Generate Practice Exam</h2>
        
        <div className="space-y-6">
          {/* Topic Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Select Topics (choose at least one)
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {availableTopics.map((topic) => (
                <button
                  key={topic}
                  onClick={() => handleTopicToggle(topic)}
                  className={`p-3 text-sm rounded-md border transition-colors ${
                    examConfig.topics.includes(topic)
                      ? 'bg-blue-100 border-blue-300 text-blue-700 dark:bg-blue-900/20 dark:border-blue-600 dark:text-blue-400'
                      : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {topic}
                </button>
              ))}
            </div>
          </div>

          {/* Exam Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Number of Questions
              </label>
              <select
                value={examConfig.questionCount}
                onChange={(e) => setExamConfig(prev => ({ ...prev, questionCount: Number(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value={5}>5 questions</option>
                <option value={10}>10 questions</option>
                <option value={15}>15 questions</option>
                <option value={20}>20 questions</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Difficulty Level
              </label>
              <select
                value={examConfig.difficulty}
                onChange={(e) => setExamConfig(prev => ({ ...prev, difficulty: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Time Limit (minutes)
              </label>
              <select
                value={examConfig.timeLimit}
                onChange={(e) => setExamConfig(prev => ({ ...prev, timeLimit: Number(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value={15}>15 minutes</option>
                <option value={30}>30 minutes</option>
                <option value={45}>45 minutes</option>
                <option value={60}>60 minutes</option>
              </select>
            </div>
          </div>

          <button
            onClick={generateExam}
            disabled={loading || examConfig.topics.length === 0}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-md transition-colors"
          >
            {loading ? 'Generating Exam...' : 'Generate Exam'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Exam Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Practice Exam ({currentExam.questions.length} questions)
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Selected topics: {examConfig.topics.join(', ')}
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {timeRemaining && (
              <div className="flex items-center space-x-2 text-orange-600 dark:text-orange-400">
                <Clock className="h-5 w-5" />
                <span className="font-medium">
                  {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, '0')}
                </span>
              </div>
            )}
            
            <button
              onClick={resetExam}
              className="flex items-center space-x-2 px-3 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Reset</span>
            </button>
          </div>
        </div>
      </div>

      {/* Questions */}
      <div className="space-y-6">
        {currentExam.questions.map((question, index) => (
          <div key={question.id} className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Question {index + 1}
              </h3>
              <p className="text-gray-700 dark:text-gray-300">{question.question}</p>
            </div>

            <div className="space-y-2">
              {question.options.map((option, optionIndex) => (
                <button
                  key={optionIndex}
                  onClick={() => !showResults && setUserAnswers(prev => ({ ...prev, [question.id]: optionIndex }))}
                  disabled={showResults}
                  className={`w-full text-left p-3 rounded-md border transition-colors ${
                    showResults
                      ? optionIndex === question.correct
                        ? 'bg-green-100 border-green-300 text-green-700 dark:bg-green-900/20 dark:border-green-600 dark:text-green-400'
                        : userAnswers[question.id] === optionIndex
                        ? 'bg-red-100 border-red-300 text-red-700 dark:bg-red-900/20 dark:border-red-600 dark:text-red-400'
                        : 'bg-gray-50 border-gray-200 text-gray-700 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300'
                      : userAnswers[question.id] === optionIndex
                      ? 'bg-blue-100 border-blue-300 text-blue-700 dark:bg-blue-900/20 dark:border-blue-600 dark:text-blue-400'
                      : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="font-medium">{String.fromCharCode(65 + optionIndex)}.</span>
                    <span>{option}</span>
                    {showResults && optionIndex === question.correct && (
                      <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 ml-auto" />
                    )}
                    {showResults && userAnswers[question.id] === optionIndex && optionIndex !== question.correct && (
                      <XCircle className="h-5 w-5 text-red-600 dark:text-red-400 ml-auto" />
                    )}
                  </div>
                </button>
              ))}
            </div>

            {showResults && (
              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md">
                <p className="text-sm text-blue-800 dark:text-blue-300">
                  <strong>Explanation:</strong> {question.explanation}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Submit/Results */}
      {!showResults ? (
        <div className="flex justify-center">
          <button
            onClick={submitExam}
            className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-6 rounded-md transition-colors"
          >
            <Save className="h-5 w-5" />
            <span>Submit Exam</span>
          </button>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Exam Results
          </h2>
          <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-4">
            {calculateScore()}%
          </div>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            You answered {currentExam.questions.reduce((count, question) => 
              userAnswers[question.id] === question.correct ? count + 1 : count, 0
            )} out of {currentExam.questions.length} questions correctly.
          </p>
          
          <div className="flex justify-center space-x-4">
            <button
              onClick={resetExam}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Take Another Exam</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};