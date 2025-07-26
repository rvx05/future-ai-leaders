import React, { useState } from 'react';
import { ExamGenerator } from '../components/ExamGenerator';

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

export const ExamPage: React.FC = () => {
  const [generatedExam, setGeneratedExam] = useState<ExamData | null>(null);

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Test Your Knowledge
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Put your learning to the test and see how far you've come!
        </p>
      </div>

      <ExamGenerator onExamGenerated={(exam) => setGeneratedExam(exam)} />

      {generatedExam && (
        <div className="mt-8">
          {/* Exam results would be displayed here */}
        </div>
      )}
    </div>
  );
};