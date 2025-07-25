import React, { useCallback, useState } from 'react';
import { Upload, File, X, Link, Type } from 'lucide-react';

interface FileUploadInputProps {
  onFilesChange: (files: File[]) => void;
}

export const FileUploadInput: React.FC<FileUploadInputProps> = ({ onFilesChange }) => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [textInput, setTextInput] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [activeTab, setActiveTab] = useState<'files' | 'text' | 'url'>('files');

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const newFiles = Array.from(e.dataTransfer.files);
      const updatedFiles = [...files, ...newFiles];
      setFiles(updatedFiles);
      onFilesChange(updatedFiles);
    }
  }, [files, onFilesChange]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      const updatedFiles = [...files, ...newFiles];
      setFiles(updatedFiles);
      onFilesChange(updatedFiles);
    }
  };

  const removeFile = (index: number) => {
    const updatedFiles = files.filter((_, i) => i !== index);
    setFiles(updatedFiles);
    onFilesChange(updatedFiles);
  };

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      const textFile = new File([textInput], 'pasted-text.txt', { type: 'text/plain' });
      const updatedFiles = [...files, textFile];
      setFiles(updatedFiles);
      onFilesChange(updatedFiles);
      setTextInput('');
    }
  };

  const handleUrlSubmit = () => {
    if (urlInput.trim()) {
      const urlFile = new File([urlInput], 'url-link.txt', { type: 'text/plain' });
      const updatedFiles = [...files, urlFile];
      setFiles(updatedFiles);
      onFilesChange(updatedFiles);
      setUrlInput('');
    }
  };

  const tabs = [
    { id: 'files' as const, label: 'Files', icon: File },
    { id: 'text' as const, label: 'Text', icon: Type },
    { id: 'url' as const, label: 'URL', icon: Link },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 px-3 py-2 rounded-md font-medium transition-colors flex-1 justify-center ${
              activeTab === tab.id
                ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* File Upload Tab */}
      {activeTab === 'files' && (
        <div>
          <div
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Drop files here or click to browse
            </p>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Supports PDF, PPT, DOCX, images, audio files
            </p>
            <input
              type="file"
              multiple
              accept=".pdf,.ppt,.pptx,.doc,.docx,.txt,.jpg,.jpeg,.png,.mp3,.wav,.m4a"
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors">
              Choose Files
            </button>
          </div>
        </div>
      )}

      {/* Text Input Tab */}
      {activeTab === 'text' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Paste your text content
            </label>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste your notes, lecture content, or any text material here..."
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <button
            onClick={handleTextSubmit}
            disabled={!textInput.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            Add Text Content
          </button>
        </div>
      )}

      {/* URL Input Tab */}
      {activeTab === 'url' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Website or document URL
            </label>
            <input
              type="url"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="https://example.com/document.pdf"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <button
            onClick={handleUrlSubmit}
            disabled={!urlInput.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            Add URL
          </button>
        </div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Selected Files ({files.length})
          </h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                <div className="flex items-center space-x-3">
                  <File className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{file.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors"
                >
                  <X className="h-4 w-4 text-gray-500" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};