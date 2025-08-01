import React from 'react';
import { GraduationCap, Moon, Sun, FileText, Zap, RotateCcw } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

export function Header() {
  const { state, dispatch } = useApp();

  const toggleTheme = () => {
    dispatch({ type: 'TOGGLE_THEME' });
  };

  const handleNewSession = async () => {
    try {
      await apiService.clearSession();
      dispatch({ type: 'CLEAR_SESSION' });
      toast.success('Session cleared successfully');
    } catch (error) {
      toast.error('Failed to clear session');
    }
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow-lg border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                AI Study Assistant
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Professional Edition
              </p>
            </div>
          </div>

          {/* Session Info */}
          {state.session.active && (
            <div className="hidden md:flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-300">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4" />
                <span>{state.session.word_count?.toLocaleString()} words</span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4" />
                <span>{state.session.page_count} pages</span>
              </div>
            </div>
          )}

          {/* Controls */}
          <div className="flex items-center space-x-2">
            {state.session.active && (
              <button
                onClick={handleNewSession}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
                title="New Session"
              >
                <RotateCcw className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
            )}
            
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
              title="Toggle Theme"
            >
              {state.theme === 'light' ? (
                <Moon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              ) : (
                <Sun className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}