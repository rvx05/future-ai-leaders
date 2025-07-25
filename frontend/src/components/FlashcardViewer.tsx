import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, RotateCcw, Check, X } from 'lucide-react';

interface Flashcard {
  id: number;
  front: string;
  back: string;
}

interface FlashcardViewerProps {
  flashcards: Flashcard[];
}

export const FlashcardViewer: React.FC<FlashcardViewerProps> = ({ flashcards }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [reviewedCards, setReviewedCards] = useState<Set<number>>(new Set());

  const currentCard = flashcards[currentIndex];

  const nextCard = () => {
    setCurrentIndex((prev) => (prev + 1) % flashcards.length);
    setIsFlipped(false);
  };

  const prevCard = () => {
    setCurrentIndex((prev) => (prev - 1 + flashcards.length) % flashcards.length);
    setIsFlipped(false);
  };

  const markAsReviewed = (difficulty: 'easy' | 'hard') => {
    setReviewedCards(prev => new Set(prev).add(currentCard.id));
    nextCard();
  };

  const resetProgress = () => {
    setReviewedCards(new Set());
    setCurrentIndex(0);
    setIsFlipped(false);
  };

  return (
    <div className="space-y-6">
      {/* Progress */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Card {currentIndex + 1} of {flashcards.length}
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Reviewed: {reviewedCards.size}/{flashcards.length}
        </div>
      </div>

      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${((currentIndex + 1) / flashcards.length) * 100}%` }}
        />
      </div>

      {/* Flashcard */}
      <div className="relative max-w-2xl mx-auto">
        <div
          className={`relative w-full h-64 cursor-pointer transition-transform duration-500 transform-style-preserve-3d ${
            isFlipped ? 'rotate-y-180' : ''
          }`}
          onClick={() => setIsFlipped(!isFlipped)}
        >
          {/* Front */}
          <div className="absolute inset-0 w-full h-full backface-hidden">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-8 shadow-lg border border-gray-200 dark:border-gray-700 h-full flex items-center justify-center">
              <div className="text-center">
                <p className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  {currentCard.front}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Click to reveal answer
                </p>
              </div>
            </div>
          </div>

          {/* Back */}
          <div className="absolute inset-0 w-full h-full backface-hidden rotate-y-180">
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-8 shadow-lg border border-blue-200 dark:border-blue-700 h-full flex items-center justify-center">
              <div className="text-center">
                <p className="text-lg font-medium text-gray-900 dark:text-white">
                  {currentCard.back}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center space-x-4">
        <button
          onClick={prevCard}
          className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          disabled={flashcards.length <= 1}
        >
          <ChevronLeft className="h-5 w-5 text-gray-700 dark:text-gray-300" />
        </button>

        <button
          onClick={resetProgress}
          className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          title="Reset progress"
        >
          <RotateCcw className="h-5 w-5 text-gray-700 dark:text-gray-300" />
        </button>

        <button
          onClick={nextCard}
          className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          disabled={flashcards.length <= 1}
        >
          <ChevronRight className="h-5 w-5 text-gray-700 dark:text-gray-300" />
        </button>
      </div>

      {/* Review Buttons (shown when flipped) */}
      {isFlipped && (
        <div className="flex items-center justify-center space-x-4">
          <button
            onClick={() => markAsReviewed('hard')}
            className="flex items-center space-x-2 px-4 py-2 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-md hover:bg-red-200 dark:hover:bg-red-900/40 transition-colors"
          >
            <X className="h-4 w-4" />
            <span>Hard</span>
          </button>

          <button
            onClick={() => markAsReviewed('easy')}
            className="flex items-center space-x-2 px-4 py-2 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-md hover:bg-green-200 dark:hover:bg-green-900/40 transition-colors"
          >
            <Check className="h-4 w-4" />
            <span>Easy</span>
          </button>
        </div>
      )}
    </div>
  );
};