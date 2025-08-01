import React from 'react';
import { Brain, ChevronLeft, ChevronRight, RotateCcw, Award } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { LoadingSpinner } from './LoadingSpinner';

export function FlashcardTab() {
  const { state, dispatch } = useApp();
  const { flashcards, flashcardState } = state;

  const currentCard = flashcards[flashcardState.currentCard];

  const handleFlip = () => {
    dispatch({
      type: 'UPDATE_FLASHCARD_STATE',
      payload: { isFlipped: !flashcardState.isFlipped }
    });
  };

  const handleNext = () => {
    if (flashcardState.currentCard < flashcards.length - 1) {
      dispatch({
        type: 'UPDATE_FLASHCARD_STATE',
        payload: {
          currentCard: flashcardState.currentCard + 1,
          isFlipped: false
        }
      });
    }
  };

  const handlePrevious = () => {
    if (flashcardState.currentCard > 0) {
      dispatch({
        type: 'UPDATE_FLASHCARD_STATE',
        payload: {
          currentCard: flashcardState.currentCard - 1,
          isFlipped: false
        }
      });
    }
  };

  const handleReset = () => {
    dispatch({
      type: 'UPDATE_FLASHCARD_STATE',
      payload: { currentCard: 0, isFlipped: false }
    });
  };

  if (state.isLoading && flashcards.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" text="Creating interactive flashcards" />
      </div>
    );
  }

  if (flashcards.length === 0) {
    return (
      <div className="text-center py-12">
        <Brain className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No Flashcards Available
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          Upload a PDF document to generate interactive flashcards.
        </p>
      </div>
    );
  }

  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'hard':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress and Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-primary-500" />
            <span className="text-lg font-semibold text-gray-900 dark:text-white">
              Card {flashcardState.currentCard + 1} of {flashcards.length}
            </span>
          </div>
          
          {currentCard?.category && (
            <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm rounded-full">
              {currentCard.category}
            </span>
          )}
          
          {currentCard?.difficulty && (
            <span className={`px-2 py-1 text-sm rounded-full ${getDifficultyColor(currentCard.difficulty)}`}>
              {currentCard.difficulty}
            </span>
          )}
        </div>

        <button
          onClick={handleReset}
          className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset</span>
        </button>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div
          className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${((flashcardState.currentCard + 1) / flashcards.length) * 100}%` }}
        />
      </div>

      {/* Flashcard */}
      <div className="flex justify-center">
        <div className="w-full max-w-2xl">
          <div
            className={`flashcard ${flashcardState.isFlipped ? 'flashcard-flipped' : ''}`}
            onClick={handleFlip}
          >
            <div className="flashcard-inner">
              {/* Front */}
              <div className="flashcard-face bg-white dark:bg-gray-800 shadow-xl">
                <div className="text-center">
                  <div className="mb-4">
                    <Brain className="w-8 h-8 text-primary-500 mx-auto mb-2" />
                    <p className="text-sm text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                      Question
                    </p>
                  </div>
                  <h3 className="text-xl font-medium text-gray-900 dark:text-white leading-relaxed">
                    {currentCard?.question}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-4">
                    Click to reveal answer
                  </p>
                </div>
              </div>

              {/* Back */}
              <div className="flashcard-face flashcard-back bg-gradient-to-br from-primary-500 to-primary-600 text-white shadow-xl">
                <div className="text-center">
                  <div className="mb-4">
                    <Award className="w-8 h-8 text-white mx-auto mb-2" />
                    <p className="text-sm text-primary-100 uppercase tracking-wide">
                      Answer
                    </p>
                  </div>
                  <h3 className="text-xl font-medium leading-relaxed mb-4">
                    {currentCard?.answer}
                  </h3>
                  {currentCard?.hint && (
                    <div className="mt-4 p-3 bg-white bg-opacity-20 rounded-lg">
                      <p className="text-sm text-primary-100">
                        💡 <strong>Hint:</strong> {currentCard.hint}
                      </p>
                    </div>
                  )}
                  <p className="text-sm text-primary-100 mt-4">
                    Click to flip back
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-center space-x-4">
        <button
          onClick={handlePrevious}
          disabled={flashcardState.currentCard === 0}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Previous</span>
        </button>

        <div className="flex items-center space-x-2 px-4 py-2 bg-primary-50 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded-lg">
          <span className="font-medium">
            {flashcardState.currentCard + 1} / {flashcards.length}
          </span>
        </div>

        <button
          onClick={handleNext}
          disabled={flashcardState.currentCard === flashcards.length - 1}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span>Next</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Keyboard Shortcuts */}
      <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        <p>
          <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">Space</kbd> to flip • 
          <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs ml-1">←</kbd> Previous • 
          <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs ml-1">→</kbd> Next
        </p>
      </div>
    </div>
  );
}