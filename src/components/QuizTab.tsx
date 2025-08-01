import React from 'react';
import { HelpCircle, ChevronLeft, ChevronRight, CheckCircle, XCircle, Trophy, RotateCcw } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { LoadingSpinner } from './LoadingSpinner';

export function QuizTab() {
  const { state, dispatch } = useApp();
  const { quiz, quizState } = state;

  const currentQuestion = quiz[quizState.currentQuestion];

  const handleAnswerSelect = (selectedAnswer: string) => {
    const newAnswers = { ...quizState.answers };
    newAnswers[quizState.currentQuestion] = selectedAnswer;
    
    dispatch({
      type: 'UPDATE_QUIZ_STATE',
      payload: { 
        answers: newAnswers,
        showExplanation: false
      }
    });
  };

  const handleSubmitAnswer = () => {
    const selectedAnswer = quizState.answers[quizState.currentQuestion];
    if (!selectedAnswer) return;

    const isCorrect = selectedAnswer === currentQuestion.options[currentQuestion.correct_answer];
    const newScore = isCorrect ? quizState.score + 1 : quizState.score;

    dispatch({
      type: 'UPDATE_QUIZ_STATE',
      payload: {
        score: newScore,
        showExplanation: true
      }
    });
  };

  const handleNext = () => {
    if (quizState.currentQuestion < quiz.length - 1) {
      dispatch({
        type: 'UPDATE_QUIZ_STATE',
        payload: {
          currentQuestion: quizState.currentQuestion + 1,
          showExplanation: false
        }
      });
    } else {
      // Complete quiz
      dispatch({
        type: 'UPDATE_QUIZ_STATE',
        payload: { completed: true }
      });
    }
  };

  const handlePrevious = () => {
    if (quizState.currentQuestion > 0) {
      dispatch({
        type: 'UPDATE_QUIZ_STATE',
        payload: {
          currentQuestion: quizState.currentQuestion - 1,
          showExplanation: false
        }
      });
    }
  };

  const handleReset = () => {
    dispatch({
      type: 'UPDATE_QUIZ_STATE',
      payload: {
        currentQuestion: 0,
        answers: {},
        score: 0,
        completed: false,
        showExplanation: false
      }
    });
  };

  if (state.isLoading && quiz.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" text="Creating adaptive quiz" />
      </div>
    );
  }

  if (quiz.length === 0) {
    return (
      <div className="text-center py-12">
        <HelpCircle className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No Quiz Available
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          Upload a PDF document to generate an adaptive quiz.
        </p>
      </div>
    );
  }

  if (quizState.completed) {
    const scorePercentage = Math.round((quizState.score / quiz.length) * 100);
    const getScoreMessage = () => {
      if (scorePercentage >= 90) return { message: "Excellent work!", icon: "🌟", color: "text-green-600" };
      if (scorePercentage >= 70) return { message: "Good job!", icon: "👍", color: "text-blue-600" };
      if (scorePercentage >= 50) return { message: "Keep studying!", icon: "📚", color: "text-yellow-600" };
      return { message: "Don't give up!", icon: "💪", color: "text-red-600" };
    };

    const scoreInfo = getScoreMessage();

    return (
      <div className="text-center py-12">
        <div className="max-w-md mx-auto">
          <div className="w-20 h-20 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <Trophy className="w-10 h-10 text-white" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Quiz Completed!
          </h2>
          
          <div className="card p-6 mb-6">
            <div className="text-4xl font-bold text-primary-600 mb-2">
              {quizState.score}/{quiz.length}
            </div>
            <div className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-4">
              {scorePercentage}%
            </div>
            <div className={`text-lg ${scoreInfo.color} font-medium`}>
              {scoreInfo.icon} {scoreInfo.message}
            </div>
          </div>

          <button
            onClick={handleReset}
            className="btn-primary inline-flex items-center space-x-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Retake Quiz</span>
          </button>
        </div>
      </div>
    );
  }

  const selectedAnswer = quizState.answers[quizState.currentQuestion];
  const isAnswered = selectedAnswer !== undefined;
  const isCorrect = isAnswered && selectedAnswer === currentQuestion.options[currentQuestion.correct_answer];

  return (
    <div className="space-y-6">
      {/* Progress and Score */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <HelpCircle className="w-5 h-5 text-primary-500" />
            <span className="text-lg font-semibold text-gray-900 dark:text-white">
              Question {quizState.currentQuestion + 1} of {quiz.length}
            </span>
          </div>
          
          <div className="flex items-center space-x-2 px-3 py-1 bg-primary-50 dark:bg-primary-900 rounded-full">
            <Trophy className="w-4 h-4 text-primary-600 dark:text-primary-400" />
            <span className="text-sm font-medium text-primary-700 dark:text-primary-300">
              Score: {quizState.score}/{Object.keys(quizState.answers).length}
            </span>
          </div>
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
          style={{ width: `${((quizState.currentQuestion + 1) / quiz.length) * 100}%` }}
        />
      </div>

      {/* Question */}
      <div className="card p-6">
        <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-6 leading-relaxed">
          {currentQuestion?.question}
        </h3>

        {/* Options */}
        <div className="space-y-3">
          {currentQuestion?.options.map((option, index) => {
            const isSelected = selectedAnswer === option;
            const isCorrectOption = index === currentQuestion.correct_answer;
            
            let optionClass = "w-full text-left p-4 rounded-lg border-2 transition-all duration-200 ";
            
            if (quizState.showExplanation) {
              if (isCorrectOption) {
                optionClass += "border-green-500 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300";
              } else if (isSelected && !isCorrectOption) {
                optionClass += "border-red-500 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300";
              } else {
                optionClass += "border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300";
              }
            } else {
              if (isSelected) {
                optionClass += "border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300";
              } else {
                optionClass += "border-gray-200 dark:border-gray-600 hover:border-primary-300 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300";
              }
            }

            return (
              <button
                key={index}
                onClick={() => !quizState.showExplanation && handleAnswerSelect(option)}
                disabled={quizState.showExplanation}
                className={optionClass}
              >
                <div className="flex items-center justify-between">
                  <span>{option}</span>
                  {quizState.showExplanation && (
                    <div className="flex items-center space-x-2">
                      {isCorrectOption && <CheckCircle className="w-5 h-5 text-green-500" />}
                      {isSelected && !isCorrectOption && <XCircle className="w-5 h-5 text-red-500" />}
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Submit Button */}
        {!quizState.showExplanation && (
          <div className="mt-6">
            <button
              onClick={handleSubmitAnswer}
              disabled={!isAnswered}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Submit Answer
            </button>
          </div>
        )}

        {/* Explanation */}
        {quizState.showExplanation && currentQuestion.explanation && (
          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Explanation:</h4>
            <p className="text-blue-800 dark:text-blue-200">{currentQuestion.explanation}</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={handlePrevious}
          disabled={quizState.currentQuestion === 0}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Previous</span>
        </button>

        {quizState.showExplanation && (
          <button
            onClick={handleNext}
            className="flex items-center space-x-2 btn-primary"
          >
            <span>{quizState.currentQuestion === quiz.length - 1 ? 'Finish Quiz' : 'Next Question'}</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}