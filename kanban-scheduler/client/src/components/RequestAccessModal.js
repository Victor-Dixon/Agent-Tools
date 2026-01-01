import React, { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { projectSharingAPI } from '../services/api';
import toast from 'react-hot-toast';

const RequestAccessModal = ({ isOpen, onClose, projectId, projectName, ownerUsername }) => {
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (projectId) {
        await projectSharingAPI.requestAccess(projectId, message);
        toast.success('Access request sent successfully!');
      } else if (ownerUsername && projectName) {
        await projectSharingAPI.requestAccessByUsername(ownerUsername, projectName, message);
        toast.success('Access request sent successfully!');
      }
      setMessage('');
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to send request');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold">Request Project Access</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {projectName && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project
              </label>
              <p className="text-gray-900 font-medium">{projectName}</p>
              {ownerUsername && (
                <p className="text-sm text-gray-500">Owner: @{ownerUsername}</p>
              )}
            </div>
          )}

          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
              Message (optional)
            </label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Tell the project owner why you'd like access..."
              maxLength={500}
            />
            <p className="text-xs text-gray-500 mt-1">{message.length}/500</p>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              {isSubmitting ? 'Sending...' : 'Send Request'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RequestAccessModal;

