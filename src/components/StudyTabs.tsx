import React from 'react';
import { 
  FileText, 
  Brain, 
  HelpCircle, 
  MessageCircle, 
  BookOpen, 
  Video, 
  Globe 
} from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { TabType } from '../types';

const tabs = [
  { id: 'summary' as TabType, label: 'Summary', icon: FileText },
  { id: 'flashcards' as TabType, label: 'Flashcards', icon: Brain },
  { id: 'quiz' as TabType, label: 'Quiz', icon: HelpCircle },
  { id: 'qa' as TabType, label: 'Q&A', icon: MessageCircle },
  { id: 'research' as TabType, label: 'Research', icon: BookOpen },
  { id: 'videos' as TabType, label: 'Videos', icon: Video },
  { id: 'resources' as TabType, label: 'Resources', icon: Globe },
];

export function StudyTabs() {
  const { state, dispatch } = useApp();

  const handleTabChange = (tabId: TabType) => {
    dispatch({ type: 'SET_TAB', payload: tabId });
  };

  return (
    <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
      <nav className="flex space-x-1 overflow-x-auto scrollbar-hide">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = state.currentTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`
                flex items-center space-x-2 px-4 py-3 text-sm font-medium rounded-t-lg transition-all duration-200 whitespace-nowrap
                ${isActive 
                  ? 'tab-active border-b-2 border-primary-500' 
                  : 'tab-inactive hover:text-gray-900 dark:hover:text-white'
                }
              `}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}