import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { whiteboardsAPI } from '../services/api';
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  PencilSquareIcon,
  PhotoIcon,
  SparklesIcon,
  TrashIcon,
  BookmarkIcon,
  XMarkIcon,
  DocumentTextIcon,
  ClipboardIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const Whiteboards = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedWhiteboard, setSelectedWhiteboard] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [uploading, setUploading] = useState(false);
  const queryClient = useQueryClient();

  const { data: whiteboardsData, isLoading } = useQuery(
    ['whiteboards', searchQuery],
    () => whiteboardsAPI.getWhiteboards({ search: searchQuery }).then(res => res.data),
    { staleTime: 60000 }
  );

  const createWhiteboardMutation = useMutation(
    (whiteboardData) => whiteboardsAPI.createWhiteboard(whiteboardData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['whiteboards']);
        setShowCreateModal(false);
        toast.success('Whiteboard created successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to create whiteboard');
      },
    }
  );

  const uploadImageMutation = useMutation(
    (formData) => whiteboardsAPI.uploadImage(formData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['whiteboards']);
        setShowUploadModal(false);
        toast.success('Image uploaded and transcribed successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to upload image');
        setUploading(false);
      },
    }
  );

  const transcribeMutation = useMutation(
    (id) => whiteboardsAPI.transcribeImage(id),
    {
      onSuccess: (response) => {
        queryClient.invalidateQueries(['whiteboards']);
        toast.success(response.data.transcription ? 'Transcription completed!' : 'OCR not available. Please transcribe manually.');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to transcribe image');
      },
    }
  );

  const updateWhiteboardMutation = useMutation(
    ({ id, data }) => whiteboardsAPI.updateWhiteboard(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['whiteboards']);
        setSelectedWhiteboard(null);
        toast.success('Whiteboard updated successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to update whiteboard');
      },
    }
  );

  const deleteWhiteboardMutation = useMutation(
    (id) => whiteboardsAPI.deleteWhiteboard(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['whiteboards']);
        toast.success('Whiteboard deleted successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to delete whiteboard');
      },
    }
  );

  const handleCreateWhiteboard = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const whiteboardData = {
      title: formData.get('title'),
      content: formData.get('content') || null,
      tags: formData.get('tags') || null,
      color: formData.get('color') || '#8B5CF6',
      isPinned: formData.get('isPinned') === 'on'
    };
    createWhiteboardMutation.mutate(whiteboardData);
  };

  const handleUploadImage = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const file = formData.get('image');
    const performOCR = formData.get('performOCR') === 'on';

    if (!file || file.size === 0) {
      toast.error('Please select an image file');
      return;
    }

    const uploadFormData = new FormData();
    uploadFormData.append('image', file);
    uploadFormData.append('title', formData.get('title') || `Whiteboard ${new Date().toLocaleDateString()}`);
    uploadFormData.append('tags', formData.get('tags') || '');
    uploadFormData.append('performOCR', performOCR);

    setUploading(true);
    uploadImageMutation.mutate(uploadFormData);
  };

  const handleTranscribe = (id) => {
    transcribeMutation.mutate(id);
  };

  const handleTogglePin = (whiteboard) => {
    updateWhiteboardMutation.mutate({
      id: whiteboard.id,
      data: { isPinned: !whiteboard.isPinned }
    });
  };

  const handleDelete = (id, title) => {
    if (window.confirm(`Are you sure you want to delete "${title}"?`)) {
      deleteWhiteboardMutation.mutate(id);
    }
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  const whiteboards = whiteboardsData?.whiteboards || [];

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Whiteboards</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your notes, brainstorm ideas, and transcribe handwritten notes
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center gap-2 rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-purple-600"
          >
            <PhotoIcon className="h-5 w-5" />
            Upload Image
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
          >
            <PlusIcon className="h-5 w-5" />
            New Whiteboard
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="block w-full rounded-md border-0 py-1.5 pl-10 pr-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
            placeholder="Search whiteboards..."
          />
        </div>
      </div>

      {/* Whiteboards Grid */}
      {whiteboards.length === 0 ? (
        <div className="text-center py-12">
          <PencilSquareIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No whiteboards</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new whiteboard or uploading an image.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {whiteboards.map((whiteboard) => (
            <div
              key={whiteboard.id}
              className="group relative overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-gray-900/5 hover:shadow-md transition-shadow"
            >
              {/* Pin indicator */}
              {whiteboard.isPinned && (
                <div className="absolute top-2 right-2 z-10">
                  <BookmarkIcon className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                </div>
              )}

              {/* Color bar */}
              <div
                className="h-2 w-full"
                style={{ backgroundColor: whiteboard.color || '#8B5CF6' }}
              />

              <div className="p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2 pr-6">
                  {whiteboard.title}
                </h3>

                {/* Image preview */}
                {whiteboard.imageUrl && (
                  <div className="mb-3 relative">
                    <img
                      src={`http://localhost:5000${whiteboard.imageUrl}`}
                      alt={whiteboard.title}
                      className="w-full h-32 object-cover rounded-md"
                    />
                    {!whiteboard.transcription && (
                      <button
                        onClick={() => handleTranscribe(whiteboard.id)}
                        className="absolute bottom-2 right-2 inline-flex items-center gap-1 rounded-md bg-purple-600 px-2 py-1 text-xs font-semibold text-white shadow-sm hover:bg-purple-500"
                        title="Transcribe image with OCR"
                      >
                        <SparklesIcon className="h-3 w-3" />
                        Transcribe
                      </button>
                    )}
                  </div>
                )}

                {/* Content preview */}
                {whiteboard.content && (
                  <p className="text-sm text-gray-600 mb-2 line-clamp-3">
                    {whiteboard.content}
                  </p>
                )}

                {/* Transcription preview */}
                {whiteboard.transcription && (
                  <div className="mb-2 p-2 bg-purple-50 rounded-md">
                    <div className="flex items-center gap-1 mb-1">
                      <ClipboardIcon className="h-4 w-4 text-purple-600" />
                      <span className="text-xs font-semibold text-purple-700">Transcription:</span>
                    </div>
                    <p className="text-xs text-gray-700 line-clamp-2">
                      {whiteboard.transcription}
                    </p>
                  </div>
                )}

                {/* Tags */}
                {whiteboard.tags && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {whiteboard.tags.split(',').map((tag, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700"
                      >
                        {tag.trim()}
                      </span>
                    ))}
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                  <span className="text-xs text-gray-500">
                    {new Date(whiteboard.updatedAt).toLocaleDateString()}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleTogglePin(whiteboard)}
                      className="text-gray-400 hover:text-yellow-500"
                      title={whiteboard.isPinned ? 'Unpin' : 'Pin'}
                    >
                      <BookmarkIcon className={`h-4 w-4 ${whiteboard.isPinned ? 'text-yellow-500 fill-yellow-500' : ''}`} />
                    </button>
                    <button
                      onClick={() => setSelectedWhiteboard(whiteboard)}
                      className="text-gray-400 hover:text-primary-600"
                      title="Edit"
                    >
                      <PencilSquareIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(whiteboard.id, whiteboard.title)}
                      className="text-gray-400 hover:text-red-600"
                      title="Delete"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowCreateModal(false)} />
            <div className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              <form onSubmit={handleCreateWhiteboard}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title *
                  </label>
                  <input
                    type="text"
                    name="title"
                    required
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Content
                  </label>
                  <textarea
                    name="content"
                    rows={6}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                    placeholder="Start typing your notes..."
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    name="tags"
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                    placeholder="brainstorm, ideas, notes"
                  />
                </div>
                <div className="mb-4 flex items-center gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Color
                    </label>
                    <input
                      type="color"
                      name="color"
                      defaultValue="#8B5CF6"
                      className="h-10 w-full rounded-md border border-gray-300"
                    />
                  </div>
                  <div className="flex items-center mt-6">
                    <input
                      type="checkbox"
                      name="isPinned"
                      className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                    />
                    <label className="ml-2 block text-sm text-gray-700">
                      Pin to top
                    </label>
                  </div>
                </div>
                <div className="flex gap-3 justify-end">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500"
                  >
                    Create
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Upload Image Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowUploadModal(false)} />
            <div className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              <div className="sm:flex sm:items-start">
                <div className="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-purple-100 sm:mx-0 sm:h-10 sm:w-10">
                  <PhotoIcon className="h-6 w-6 text-purple-600" />
                </div>
                <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left flex-1">
                  <h3 className="text-base font-semibold text-gray-900 mb-4">
                    Upload Image for Transcription
                  </h3>
                  <form onSubmit={handleUploadImage}>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Title
                      </label>
                      <input
                        type="text"
                        name="title"
                        className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                        placeholder="Auto-generated if empty"
                      />
                    </div>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Image File *
                      </label>
                      <input
                        type="file"
                        name="image"
                        accept="image/*"
                        required
                        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                      />
                      <p className="mt-1 text-xs text-gray-500">
                        Upload a photo of handwritten notes. OCR will transcribe the text automatically.
                      </p>
                    </div>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tags (comma-separated)
                      </label>
                      <input
                        type="text"
                        name="tags"
                        className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                      />
                    </div>
                    <div className="mb-4">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          name="performOCR"
                          defaultChecked
                          className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                        />
                        <label className="ml-2 block text-sm text-gray-700">
                          Automatically transcribe with OCR
                        </label>
                      </div>
                      <p className="mt-1 text-xs text-gray-500 ml-6">
                        Uses AI-powered OCR to extract text from your handwritten notes
                      </p>
                    </div>
                    <div className="flex gap-3 justify-end">
                      <button
                        type="button"
                        onClick={() => setShowUploadModal(false)}
                        className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={uploading}
                        className="rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500 disabled:opacity-50"
                      >
                        {uploading ? 'Uploading...' : 'Upload & Transcribe'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {selectedWhiteboard && (
        <WhiteboardEditModal
          whiteboard={selectedWhiteboard}
          onClose={() => setSelectedWhiteboard(null)}
          onSave={(data) => updateWhiteboardMutation.mutate({ id: selectedWhiteboard.id, data })}
        />
      )}
    </div>
  );
};

const WhiteboardEditModal = ({ whiteboard, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: whiteboard.title,
    content: whiteboard.content || '',
    transcription: whiteboard.transcription || '',
    tags: whiteboard.tags || '',
    color: whiteboard.color || '#8B5CF6',
    isPinned: whiteboard.isPinned
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />
        <div className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6">
          <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
            <button
              onClick={onClose}
              className="rounded-md bg-white text-gray-400 hover:text-gray-500"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          <form onSubmit={handleSubmit}>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Edit Whiteboard</h3>
            
            {/* Image preview */}
            {whiteboard.imageUrl && (
              <div className="mb-4">
                <img
                  src={`http://localhost:5000${whiteboard.imageUrl}`}
                  alt={whiteboard.title}
                  className="w-full max-h-64 object-contain rounded-md border border-gray-200"
                />
              </div>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Content
              </label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                rows={6}
                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Transcription
              </label>
              <textarea
                value={formData.transcription}
                onChange={(e) => setFormData({ ...formData, transcription: e.target.value })}
                rows={4}
                placeholder="OCR transcription will appear here, or type manually..."
                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 bg-purple-50"
              />
              <p className="mt-1 text-xs text-gray-500">
                Edit the OCR transcription or add your own notes. Both humans and AI agents can read this.
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tags (comma-separated)
              </label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
              />
            </div>

            <div className="mb-4 flex items-center gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Color
                </label>
                <input
                  type="color"
                  value={formData.color}
                  onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                  className="h-10 w-full rounded-md border border-gray-300"
                />
              </div>
              <div className="flex items-center mt-6">
                <input
                  type="checkbox"
                  checked={formData.isPinned}
                  onChange={(e) => setFormData({ ...formData, isPinned: e.target.checked })}
                  className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                />
                <label className="ml-2 block text-sm text-gray-700">
                  Pin to top
                </label>
              </div>
            </div>

            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={onClose}
                className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500"
              >
                Save
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Whiteboards;

