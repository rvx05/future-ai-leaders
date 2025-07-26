import React, { useState, useEffect } from 'react';
import { Lightbulb } from 'lucide-react';

const motivationalQuotes = [
  "The secret to getting ahead is getting started.",
  "Don't watch the clock; do what it does. Keep going.",
  "The expert in anything was once a beginner.",
  "Believe you can and you're halfway there.",
  "Success is not final, failure is not fatal: it is the courage to continue that counts.",
  "The future belongs to those who believe in the beauty of their dreams."
];

export const DailyMotivation: React.FC = () => {
  const [quote, setQuote] = useState('');

  useEffect(() => {
    // Select a random quote when the component mounts
    const randomIndex = Math.floor(Math.random() * motivationalQuotes.length);
    setQuote(motivationalQuotes[randomIndex]);
  }, []);

  return (
    <div className="bg-blue-50 dark:bg-gray-800 border-l-4 border-blue-500 text-blue-700 dark:text-blue-300 p-4 rounded-r-lg shadow-sm mb-8">
      <div className="flex">
        <div className="py-1">
          <Lightbulb className="h-6 w-6 mr-4" />
        </div>
        <div>
          <p className="font-bold">Daily Dose of Motivation</p>
          <p className="text-sm">{quote}</p>
        </div>
      </div>
    </div>
  );
};
