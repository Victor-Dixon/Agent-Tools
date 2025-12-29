import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { boardsAPI } from '../services/api';
import { PlusIcon, EllipsisHorizontalIcon, ClipboardDocumentListIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const Boards = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const queryClient = useQueryClient();

  const { data: boardsData, isLoading, error } = useQuery(
    'boards',
    () => boardsAPI.getBoards().then(res => res.data),
    { staleTime: 60000 }
  );

  const createBoardMutation = useMutation(
    (boardData) => boardsAPI.createBoard(boardData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['boards']);
        setShowCreateModal(false);
        toast.success('Board created successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to create board');
      },
    }
  );

  const deleteBoardMutation = useMutation(
    (id) => boardsAPI.deleteBoard(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['boards']);
        toast.success('Board deleted successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to delete board');
      },
    }
  );

  const handleCreateBoard = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const boardData = {
      name: formData.get('name'),
      description: formData.get('description'),
      color: formData.get('color') || '#3B82F6'
    };
    createBoardMutation.mutate(boardData);
  };

  const handleDeleteBoard = (id, name) => {
    if (window.confirm(`Are you sure you want to delete the board "${name}"?`)) {
      deleteBoardMutation.mutate(id);
    }
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    const errorMessage = error.response?.data?.error || error.message || 'Failed to load boards';
    const statusCode = error.response?.status;
    
    return (
      <div className="text-center py-8">
        <p className="text-red-600 font-semibold text-lg mb-2">Error loading boards</p>
        <p className="text-gray-600 mb-1">{errorMessage}</p>
        {statusCode === 401 && (
          <p className="text-yellow-600 text-sm mb-4">Please log in to view your boards.</p>
        )}
        {statusCode === 400 && error.response?.data?.errors && (
          <div className="text-gray-500 text-sm mb-4">
            <p>Validation errors:</p>
            <ul className="list-disc list-inside mt-2">
              {error.response.data.errors.map((err, idx) => (
                <li key={idx}>{err.msg}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  const boards = boardsData?.boards || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Boards</h1>
          <p className="text-gray-600">Manage your Kanban boards and organize your tasks</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <PlusIcon className="h-5 w-5" />
          New Board
        </button>
      </div>

      {/* Boards Grid */}
      {boards.length === 0 ? (
        <div className="text-center py-12">
          <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No boards</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating a new board.</p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              New Board
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {boards.map((board) => (
            <div key={board.id} className="card hover:shadow-lg transition-shadow">
              <div className="card-body">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: board.color }}
                    />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{board.name}</h3>
                      {board.description && (
                        <p className="text-sm text-gray-600 mt-1">{board.description}</p>
                      )}
                    </div>
                  </div>
                  <div className="relative">
                    <button className="text-gray-400 hover:text-gray-600">
                      <EllipsisHorizontalIcon className="h-5 w-5" />
                    </button>
                    {/* Dropdown menu would go here */}
                  </div>
                </div>

                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>{board._count.tasks} tasks</span>
                    <span>{board._count.lists} lists</span>
                  </div>
                  
                  {board._count.tasks > 0 && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span>{board.stats.completionPercentage}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${board.stats.completionPercentage}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-4 flex items-center justify-between">
                  <Link
                    to={`/boards/${board.id}`}
                    className="btn-primary btn-sm"
                  >
                    Open Board
                  </Link>
                  <div className="flex items-center space-x-2">
                    {board.isDefault && (
                      <span className="badge-primary text-xs">Default</span>
                    )}
                    <button
                      onClick={() => handleDeleteBoard(board.id, board.name)}
                      className="text-red-600 hover:text-red-800 text-sm"
                      disabled={deleteBoardMutation.isLoading}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Board Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" onClick={() => setShowCreateModal(false)}>
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <form onSubmit={handleCreateBoard}>
                <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Create New Board
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Board Name *
                      </label>
                      <input
                        name="name"
                        required
                        className="input"
                        placeholder="Enter board name"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <textarea
                        name="description"
                        rows={3}
                        className="textarea"
                        placeholder="Enter board description"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Color
                      </label>
                      <input
                        name="color"
                        type="color"
                        defaultValue="#3B82F6"
                        className="h-10 w-20 rounded border border-gray-300"
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                  <button
                    type="submit"
                    disabled={createBoardMutation.isLoading}
                    className="btn-primary"
                  >
                    {createBoardMutation.isLoading ? 'Creating...' : 'Create Board'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="btn-outline mr-3"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Boards;
