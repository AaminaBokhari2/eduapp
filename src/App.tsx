import React, { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { AppProvider, useApp } from './contexts/AppContext';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Header } from './components/Header';
import { FileUpload } from './components/FileUpload';
import { StudyTabs } from './components/StudyTabs';
import { SummaryTab } from './components/SummaryTab';
import { FlashcardTab } from './components/FlashcardTab';
import { QuizTab } from './components/QuizTab';
import { QATab } from './components/QATab';
import { ResearchTab } from './components/ResearchTab';
import { VideosTab } from './components/VideosTab';
import { ResourcesTab } from './components/ResourcesTab';
import { FullPageLoader } from './components/LoadingSpinner';

function AppContent() {
  const { state } = useApp();

  // Apply theme to document
  useEffect(() => {
    if (state.theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [state.theme]);

  const renderTabContent = () => {
    switch (state.currentTab) {
      case 'summary':
        return <SummaryTab />;
      case 'flashcards':
        return <FlashcardTab />;
      case 'quiz':
        return <QuizTab />;
      case 'qa':
        return <QATab />;
      case 'research':
        return <ResearchTab />;
      case 'videos':
        return <VideosTab />;
      case 'resources':
        return <ResourcesTab />;
      default:
        return <SummaryTab />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!state.session.active ? (
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h1 className="text-5xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-4">
                AI Study Assistant
              </h1>
              <p className="text-2xl text-gray-600 dark:text-gray-300 mb-2">
                Professional Edition
              </p>
              <p className="text-lg text-gray-500 dark:text-gray-400">
                Transform your PDFs into comprehensive study materials with advanced AI technology
              </p>
            </div>
            <FileUpload />
          </div>
        ) : (
          <div className="space-y-6">
            <StudyTabs />
            <div className="animate-fade-in">
              {renderTabContent()}
            </div>
          </div>
        )}
      </main>

      {state.isLoading && <FullPageLoader text="Processing your document with AI" />}
      
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: state.theme === 'dark' ? '#374151' : '#ffffff',
            color: state.theme === 'dark' ? '#f9fafb' : '#111827',
            border: `1px solid ${state.theme === 'dark' ? '#4b5563' : '#e5e7eb'}`,
            borderRadius: '12px',
            padding: '16px',
            fontSize: '14px',
            fontWeight: '500',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#ffffff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#ffffff',
            },
          },
        }}
      />
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AppProvider>
        <AppContent />
      </AppProvider>
    </ErrorBoundary>
  );
}

export default App;