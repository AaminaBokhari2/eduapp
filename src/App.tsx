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

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only handle shortcuts when not typing in inputs
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      // Flashcard shortcuts
      if (state.currentTab === 'flashcards' && state.flashcards.length > 0) {
        if (e.code === 'Space') {
          e.preventDefault();
          // Flip flashcard logic would go here
        } else if (e.code === 'ArrowLeft') {
          e.preventDefault();
          // Previous flashcard logic would go here
        } else if (e.code === 'ArrowRight') {
          e.preventDefault();
          // Next flashcard logic would go here
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [state.currentTab, state.flashcards.length]);

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
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                AI Study Assistant Pro
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-2">
                Enhanced Discovery Edition
              </p>
              <p className="text-gray-500 dark:text-gray-400">
                Upload your PDFs and get comprehensive study materials with advanced AI research discovery
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

      {state.isLoading && <FullPageLoader text="Processing your document" />}
      
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: state.theme === 'dark' ? '#374151' : '#ffffff',
            color: state.theme === 'dark' ? '#f9fafb' : '#111827',
            border: `1px solid ${state.theme === 'dark' ? '#4b5563' : '#e5e7eb'}`,
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