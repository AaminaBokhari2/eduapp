import React from 'react';
import { FileText, Clock, BookOpen } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { LoadingSpinner } from './LoadingSpinner';

export function SummaryTab() {
  const { state } = useApp();

  if (state.isLoading && !state.summary) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" text="Generating intelligent summary" />
      </div>
    );
  }

  if (!state.summary) {
    return (
      <div className="text-center py-12">
        <FileText className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No Summary Available
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          Upload a PDF document to generate an AI-powered summary.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-300">Words</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {state.session.word_count?.toLocaleString() || 'N/A'}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-300">Pages</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {state.session.page_count || 'N/A'}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-300">Read Time</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {state.session.word_count ? `${Math.ceil(state.session.word_count / 200)} min` : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Content */}
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <FileText className="w-5 h-5 text-primary-500" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Intelligent Summary
          </h2>
        </div>
        
        <div className="prose prose-gray dark:prose-invert max-w-none">
          <div className="whitespace-pre-wrap text-gray-700 dark:text-gray-300 leading-relaxed">
            {state.summary}
          </div>
        </div>
      </div>

      {/* Processing Methods */}
      {state.session.methods_used && state.session.methods_used.length > 0 && (
        <div className="card p-4">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
            Processing Methods Used
          </h3>
          <div className="flex flex-wrap gap-2">
            {state.session.methods_used.map((method, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full"
              >
                {method}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}