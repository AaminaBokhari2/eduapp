import React from 'react';
import { Video, ExternalLink, Clock, Eye, User } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { LoadingSpinner } from './LoadingSpinner';

export function VideosTab() {
  const { state } = useApp();
  const { youtubeVideos } = state;

  if (state.isLoading && youtubeVideos.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" text="Finding educational videos" />
      </div>
    );
  }

  if (youtubeVideos.length === 0) {
    return (
      <div className="text-center py-12">
        <Video className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No Videos Found
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          Upload a PDF document to discover related educational videos.
        </p>
      </div>
    );
  }

  const getEducationalScoreColor = (score?: string) => {
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
          <Video className="w-6 h-6 text-primary-500" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Educational Videos ({youtubeVideos.length} found)
          </h2>
        </div>
      </div>

      {/* Videos Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {youtubeVideos.map((video, index) => (
          <div key={index} className="card card-hover overflow-hidden">
            {/* Video Thumbnail Placeholder */}
            <div className="aspect-video bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 flex items-center justify-center">
              <Video className="w-12 h-12 text-gray-400 dark:text-gray-500" />
            </div>

            <div className="p-4">
              {/* Title */}
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2 leading-tight">
                {video.title}
              </h3>

              {/* Channel */}
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300 mb-3">
                <User className="w-4 h-4" />
                <span>{video.channel}</span>
              </div>

              {/* Metadata */}
              <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-3">
                <div className="flex items-center space-x-4">
                  {video.duration && (
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>{video.duration}</span>
                    </div>
                  )}
                  
                  {video.views && (
                    <div className="flex items-center space-x-1">
                      <Eye className="w-4 h-4" />
                      <span>{video.views}</span>
                    </div>
                  )}
                </div>

                {video.educational_score && (
                  <span className={`px-2 py-1 text-xs rounded-full ${getEducationalScoreColor(video.educational_score)}`}>
                    {video.educational_score}
                  </span>
                )}
              </div>

              {/* Description */}
              {video.description && (
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-4 line-clamp-2">
                  {video.description}
                </p>
              )}

              {/* Watch Button */}
              {video.url && video.url !== '#' && (
                <a
                  href={video.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-2 w-full justify-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  <Video className="w-4 h-4" />
                  <span>Watch on YouTube</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Educational Note */}
      <div className="card p-4 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <div className="flex items-start space-x-3">
          <Video className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-1">
              Educational Content
            </h4>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              These videos are curated from top educational channels like Khan Academy, Crash Course, MIT, TED-Ed, and other verified educational sources to provide high-quality learning content related to your document.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}