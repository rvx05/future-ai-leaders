import React, { useState } from 'react';
import { ExamGenerator } from '../components/ExamGenerator';

export const ExamPage: React.FC = () => {
  const [generatedExam, setGeneratedExam] = useState(null);

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Practice Exams
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Test your knowledge with AI-generated practice exams
        </p>
      </div>

      <ExamGenerator onExamGenerated={setGeneratedExam} />

      {generatedExam && (
        <div className="mt-8">
          {/* Exam results would be displayed here */}
        </div>
      )}
    </div>
  );
};