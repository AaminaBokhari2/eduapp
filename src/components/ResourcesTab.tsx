import React from 'react';
import { Globe, ExternalLink, Star, BookOpen, Code, GraduationCap } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { LoadingSpinner } from './LoadingSpinner';

export function ResourcesTab() {
  const { state } = useApp();
  const { webResources } = state;

  if (state.isLoading && webResources.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" text="Finding web resources" />
      </div>
    );
  }

  if (webResources.length === 0) {
    return (
      <div className="text-center py-12">
        <Globe className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No Web Resources Found
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          Upload a PDF document to discover related web learning resources.
        </p>
      </div>
    );
  }

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'course':
        return <GraduationCap className="w-5 h-5" />;
      case 'tutorial':
        return <Code className="w-5 h-5" />;
      case 'documentation':
        return <BookOpen className="w-5 h-5" />;
      default:
        return <Globe className="w-5 h-5" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'course':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'tutorial':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'documentation':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'reference':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  const getQualityScoreColor = (score?: string) => {
    switch (score?.toLowerCase()) {
      case 'high':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Globe className="w-6 h-6 text-primary-500" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Web Learning Resources ({webResources.length} found)
          </h2>
        </div>
      </div>

      {/* Resources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {webResources.map((resource, index) => (
          <div key={index} className="card card-hover p-6">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${getTypeColor(resource.type)}`}>
                  {getTypeIcon(resource.type)}
                </div>
                <div className="flex-1">
                  <span className={`px-2 py-1 text-xs rounded-full ${getTypeColor(resource.type)}`}>
                    {resource.type}
                  </span>
                </div>
              </div>
              
              {resource.quality_score && (
                <span className={`px-2 py-1 text-xs rounded-full ${getQualityScoreColor(resource.quality_score)}`}>
                  {resource.quality_score}
                </span>
              )}
            </div>

            {/* Title */}
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2 leading-tight">
              {resource.title}
            </h3>

            {/* Source */}
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300 mb-3">
              <Globe className="w-4 h-4" />
              <span>{resource.source}</span>
            </div>

            {/* Description */}
            {resource.description && (
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-4 line-clamp-3">
                {resource.description}
              </p>
            )}

            {/* Action Button */}
            {resource.url && resource.url !== '#' && (
              <a
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 w-full justify-center px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium rounded-lg transition-colors"
              >
                <span>Visit Resource</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>
        ))}
      </div>

      {/* Platform Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-4 text-center">
          <GraduationCap className="w-8 h-8 text-blue-500 mx-auto mb-2" />
          <h4 className="font-medium text-gray-900 dark:text-white">Courses</h4>
          <p className="text-sm text-gray-600 dark:text-gray-300">Coursera, edX, Udemy</p>
        </div>
        
        <div className="card p-4 text-center">
          <Code className="w-8 h-8 text-green-500 mx-auto mb-2" />
          <h4 className="font-medium text-gray-900 dark:text-white">Tutorials</h4>
          <p className="text-sm text-gray-600 dark:text-gray-300">W3Schools, MDN, FreeCodeCamp</p>
        </div>
        
        <div className="card p-4 text-center">
          <BookOpen className="w-8 h-8 text-purple-500 mx-auto mb-2" />
          <h4 className="font-medium text-gray-900 dark:text-white">Documentation</h4>
          <p className="text-sm text-gray-600 dark:text-gray-300">Official docs & guides</p>
        </div>
        
        <div className="card p-4 text-center">
          <Star className="w-8 h-8 text-orange-500 mx-auto mb-2" />
          <h4 className="font-medium text-gray-900 dark:text-white">Quality</h4>
          <p className="text-sm text-gray-600 dark:text-gray-300">Verified platforms only</p>
        </div>
      </div>
    </div>
  );
}