import React from 'react';
import { BookOpen, ExternalLink, Star, Calendar, Users } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { LoadingSpinner } from './LoadingSpinner';

export function ResearchTab() {
  const { state } = useApp();
  const { researchPapers } = state;

  if (state.isLoading && researchPapers.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" text="Discovering research papers" />
      </div>
    );
  }

  if (researchPapers.length === 0) {
    return (
      <div className="text-center py-12">
        <BookOpen className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No Research Papers Found
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          Upload a PDF document to discover related research papers.
        </p>
      </div>
    );
  }

  const getRelevanceColor = (score?: number, label?: string) => {
    if (label) {
      switch (label.toLowerCase()) {
        case 'high':
          return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
        case 'medium':
          return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
        case 'low':
          return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
        default:
          return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
      }
    }
    
    if (score) {
      if (score >= 0.8) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      if (score >= 0.6) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
    }
    
    return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
  };

  const getRelevanceText = (score?: number, label?: string) => {
    if (label) return label;
    if (score) return `${Math.round(score * 100)}% match`;
    return 'N/A';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BookOpen className="w-6 h-6 text-primary-500" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Research Papers ({researchPapers.length} found)
          </h2>
        </div>
      </div>

      {/* Papers Grid */}
      <div className="grid gap-6">
        {researchPapers.map((paper, index) => (
          <div key={index} className="card card-hover p-6">
            <div className="flex items-start justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white leading-tight flex-1 mr-4">
                {paper.title}
              </h3>
              
              {(paper.relevance_score || paper.relevance_label) && (
                <span className={`px-2 py-1 text-xs rounded-full flex-shrink-0 ${getRelevanceColor(paper.relevance_score, paper.relevance_label)}`}>
                  {getRelevanceText(paper.relevance_score, paper.relevance_label)}
                </span>
              )}
            </div>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-300 mb-4">
              {paper.authors && (
                <div className="flex items-center space-x-1">
                  <Users className="w-4 h-4" />
                  <span>{paper.authors}</span>
                </div>
              )}
              
              {paper.year && (
                <div className="flex items-center space-x-1">
                  <Calendar className="w-4 h-4" />
                  <span>{paper.year}</span>
                </div>
              )}
              
              {paper.citation_count && (
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4" />
                  <span>{paper.citation_count} citations</span>
                </div>
              )}
              
              {paper.source && (
                <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full">
                  {paper.source}
                </span>
              )}
            </div>

            {/* Fields of Study */}
            {paper.fields_of_study && paper.fields_of_study.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {paper.fields_of_study.slice(0, 3).map((field, fieldIndex) => (
                  <span
                    key={fieldIndex}
                    className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-xs rounded-full"
                  >
                    {field}
                  </span>
                ))}
                {paper.fields_of_study.length > 3 && (
                  <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded-full">
                    +{paper.fields_of_study.length - 3} more
                  </span>
                )}
              </div>
            )}

            {/* Abstract */}
            {paper.abstract && (
              <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed mb-4 line-clamp-3">
                {paper.abstract}
              </p>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex flex-wrap gap-2">
                {paper.categories && paper.categories.slice(0, 2).map((category, catIndex) => (
                  <span
                    key={catIndex}
                    className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded"
                  >
                    {category}
                  </span>
                ))}
              </div>
              
              {paper.url && paper.url !== '#' && (
                <a
                  href={paper.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-2 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm font-medium transition-colors"
                >
                  <span>Read Paper</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}