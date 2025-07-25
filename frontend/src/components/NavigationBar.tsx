import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  CreditCard, 
  Calendar, 
  FileText, 
  Upload, 
  Settings, 
  Moon, 
  Sun,
  Brain
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

export const NavigationBar: React.FC = () => {
  const location = useLocation();
  const { isDark, toggleTheme } = useTheme();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/flashcards', icon: CreditCard, label: 'Flashcards' },
    { path: '/study-plan', icon: Calendar, label: 'Study Plan' },
    { path: '/exam', icon: FileText, label: 'Practice Exams' },
    { path: '/upload', icon: Upload, label: 'Upload' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <Brain className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              AI Study Buddy
            </span>
          </div>

          <div className="flex items-center space-x-1">
            {navItems.map(({ path, icon: Icon, label }) => (
              <Link
                key={path}
                to={path}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === path
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-blue-400 dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="h-4 w-4 inline mr-2" />
                {label}
              </Link>
            ))}
            
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-blue-400 dark:hover:bg-gray-700 transition-colors"
              aria-label="Toggle theme"
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};