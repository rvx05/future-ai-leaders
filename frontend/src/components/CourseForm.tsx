import React, { useState } from 'react';

interface CourseInfo {
  instructor: string;
  courseCode: string;
  institution: string;
  frequency: string;
  description?: string;
}

interface CourseFormProps {
  onSubmit: (courseInfo: CourseInfo) => void;
}

export const CourseForm: React.FC<CourseFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<CourseInfo>({
    instructor: '',
    courseCode: '',
    institution: '',
    frequency: 'weekly',
    description: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 space-y-4">
      <div>
        <label htmlFor="courseCode" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Course Code *
        </label>
        <input
          type="text"
          id="courseCode"
          name="courseCode"
          value={formData.courseCode}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          placeholder="e.g., CS101, MATH201"
          required
        />
      </div>

      <div>
        <label htmlFor="instructor" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Instructor Name
        </label>
        <input
          type="text"
          id="instructor"
          name="instructor"
          value={formData.instructor}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          placeholder="Professor Name"
        />
      </div>

      <div>
        <label htmlFor="institution" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Institution
        </label>
        <input
          type="text"
          id="institution"
          name="institution"
          value={formData.institution}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          placeholder="University/School Name"
        />
      </div>

      <div>
        <label htmlFor="frequency" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Content Update Frequency
        </label>
        <select
          id="frequency"
          name="frequency"
          value={formData.frequency}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="biweekly">Bi-weekly</option>
          <option value="monthly">Monthly</option>
          <option value="asneeded">As needed</option>
        </select>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Course Description (Optional)
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          placeholder="Brief description of the course content and objectives..."
        />
      </div>

      <button
        type="submit"
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
      >
        Save Course Information
      </button>
    </form>
  );
};