import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { boardsAPI } from '../services/api';
import KanbanBoard from '../components/KanbanBoard';
import LoadingSpinner from '../components/LoadingSpinner';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

const BoardDetail = () => {
  const { id } = useParams();

  const { data: board, isLoading, error } = useQuery(
    ['board', id],
    () => boardsAPI.getBoard(id).then(res => res.data.board),
    {
      enabled: !!id,
      staleTime: 30000,
    }
  );

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    const errorMessage = error.response?.data?.error || error.message || 'Failed to load board';
    const statusCode = error.response?.status;
    
    return (
      <div className="text-center py-8">
        <p className="text-red-600 font-semibold text-lg mb-2">Error loading board</p>
        <p className="text-gray-600 mb-1">{errorMessage}</p>
        {statusCode === 401 && (
          <p className="text-yellow-600 text-sm mb-4">Please log in to view this board.</p>
        )}
        {statusCode === 404 && (
          <p className="text-gray-500 text-sm mb-4">This board doesn't exist or you don't have access to it.</p>
        )}
        <Link to="/boards" className="btn-primary mt-4 inline-block">
          Back to Boards
        </Link>
      </div>
    );
  }

  if (!board) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Board not found</p>
        <Link to="/boards" className="btn-primary mt-4">
          Back to Boards
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link 
            to="/boards" 
            className="text-gray-400 hover:text-gray-600"
          >
            <ArrowLeftIcon className="h-6 w-6" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <div 
                className="w-4 h-4 rounded"
                style={{ backgroundColor: board.color }}
              />
              <h1 className="text-3xl font-bold text-gray-900">{board.name}</h1>
            </div>
            {board.description && (
              <p className="text-gray-600 mt-1">{board.description}</p>
            )}
          </div>
        </div>
      </div>

      {/* Board Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 rounded-lg bg-blue-100">
                <span className="text-blue-600 font-semibold text-sm">Total</span>
              </div>
              <div className="ml-3">
                <p className="text-2xl font-semibold text-gray-900">{board.stats?.totalTasks || 0}</p>
                <p className="text-sm text-gray-600">Tasks</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 rounded-lg bg-green-100">
                <span className="text-green-600 font-semibold text-sm">Done</span>
              </div>
              <div className="ml-3">
                <p className="text-2xl font-semibold text-gray-900">{board.stats?.completedTasks || 0}</p>
                <p className="text-sm text-gray-600">Completed</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 rounded-lg bg-yellow-100">
                <span className="text-yellow-600 font-semibold text-sm">Lists</span>
              </div>
              <div className="ml-3">
                <p className="text-2xl font-semibold text-gray-900">{board._count?.lists || 0}</p>
                <p className="text-sm text-gray-600">Columns</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 rounded-lg bg-purple-100">
                <span className="text-purple-600 font-semibold text-sm">Progress</span>
              </div>
              <div className="ml-3">
                <p className="text-2xl font-semibold text-gray-900">{board.stats?.completionPercentage || 0}%</p>
                <p className="text-sm text-gray-600">Complete</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="card">
        <div className="card-body p-6">
          <KanbanBoard 
            boardId={id}
            lists={board.lists}
          />
        </div>
      </div>
    </div>
  );
};

export default BoardDetail;
