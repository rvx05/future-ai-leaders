import React, { useState } from 'react';
import { FileUploadInput } from '../components/FileUploadInput';
import { CourseForm } from '../components/CourseForm';

interface CourseInfo {
  instructor: string;
  courseCode: string;
  institution: string;
  frequency: string;
  description?: string;
}

export const UploadPage: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [courseInfo, setCourseInfo] = useState<CourseInfo | null>(null);

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Add Your Course Materials
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Let's get your notes and documents ready for your AI Study Buddy.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Course Information Form */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Course Information
          </h2>
          <CourseForm onSubmit={(info) => setCourseInfo(info)} />
        </div>

        {/* File Upload */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Upload Materials
          </h2>
          <FileUploadInput onFilesChange={setUploadedFiles} />
        </div>
      </div>

      {/* Uploaded Files Preview */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Uploaded Files ({uploadedFiles.length})
          </h2>
          <div className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{file.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <span className="px-2 py-1 text-xs bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded">
                  Uploaded
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Status */}
      {uploadedFiles.length > 0 || courseInfo ? (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 dark:text-blue-300 mb-2">
            Ready to Process
          </h3>
          <p className="text-blue-700 dark:text-blue-400 mb-4">
            Your course materials are ready to be processed by our AI. This will enable personalized flashcards, study plans, and practice exams.
          </p>
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-md transition-colors">
            Process Materials with AI
          </button>
        </div>
      ) : null}
    </div>
  );
};