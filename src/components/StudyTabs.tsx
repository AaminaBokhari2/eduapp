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
import { motion } from 'framer-motion';
import { useApp } from '../contexts/AppContext';
import type { TabType } from '../types';

const tabs = [
  { id: 'summary' as TabType, label: 'Summary', icon: FileText, color: 'from-blue-500 to-blue-600' },
  { id: 'flashcards' as TabType, label: 'Flashcards', icon: Brain, color: 'from-purple-500 to-purple-600' },
  { id: 'quiz' as TabType, label: 'Quiz', icon: HelpCircle, color: 'from-green-500 to-green-600' },
  { id: 'qa' as TabType, label: 'Q&A', icon: MessageCircle, color: 'from-orange-500 to-orange-600' },
  { id: 'research' as TabType, label: 'Research', icon: BookOpen, color: 'from-red-500 to-red-600' },
  { id: 'videos' as TabType, label: 'Videos', icon: Video, color: 'from-pink-500 to-pink-600' },
  { id: 'resources' as TabType, label: 'Resources', icon: Globe, color: 'from-indigo-500 to-indigo-600' },
];

export function StudyTabs() {
  const { state, dispatch } = useApp();

  const handleTabChange = (tabId: TabType) => {
    dispatch({ type: 'SET_TAB', payload: tabId });
  };

  return (
    <div className="border-b border-gray-200 dark:border-gray-700 mb-8">
      <nav className="flex space-x-1 overflow-x-auto scrollbar-hide">
        {tabs.map((tab, index) => {
          const Icon = tab.icon;
          const isActive = state.currentTab === tab.id;
          
          return (
            <motion.button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`
                flex items-center space-x-2 px-6 py-4 text-sm font-medium rounded-t-lg transition-all duration-200 whitespace-nowrap relative
                ${isActive 
                  ? 'text-white shadow-lg' 
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                }
              `}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              {isActive && (
                <motion.div
                  className={`absolute inset-0 bg-gradient-to-r ${tab.color} rounded-t-lg`}
                  layoutId="activeTab"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
              <div className="relative z-10 flex items-center space-x-2">
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </div>
              {isActive && (
                <motion.div
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-white"
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ duration: 0.3 }}
                />
              )}
            </motion.button>
          );
        })}
      </nav>
    </div>
  );
}