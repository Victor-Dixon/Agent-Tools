import React from 'react';
import { format, isAfter, isBefore, addDays } from 'date-fns';
import { 
  CalendarIcon, 
  ChatBubbleLeftIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  PencilIcon
} from '@heroicons/react/24/outline';

const TaskCard = ({ task, onClick, onEdit, isDragging = false }) => {
  const isOverdue = task.dueDate && isBefore(new Date(task.dueDate), new Date()) && task.status !== 'DONE';
  const isDueSoon = task.dueDate && isAfter(addDays(new Date(), 3), new Date(task.dueDate)) && !isOverdue;

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'URGENT': return 'border-l-red-500';
      case 'HIGH': return 'border-l-orange-500';
      case 'MEDIUM': return 'border-l-yellow-500';
      case 'LOW': return 'border-l-green-500';
      default: return 'border-l-gray-300';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'DONE': return 'bg-green-50 border-green-200';
      case 'IN_PROGRESS': return 'bg-blue-50 border-blue-200';
      case 'IN_REVIEW': return 'bg-purple-50 border-purple-200';
      case 'BLOCKED': return 'bg-red-50 border-red-200';
      case 'CANCELLED': return 'bg-gray-50 border-gray-200';
      default: return 'bg-white border-gray-200';
    }
  };

  const completionProgress = task.subtasks?.length > 0 
    ? Math.round((task.subtasks.filter(st => st.completed).length / task.subtasks.length) * 100)
    : null;

  return (
    <div
      className={`kanban-task border-l-4 ${getPriorityColor(task.priority)} ${getStatusColor(task.status)} ${
        isDragging ? 'opacity-50 transform rotate-3' : ''
      } hover:shadow-md transition-all duration-200`}
      onClick={onClick}
    >
      {/* Task Header */}
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-medium text-gray-900 text-sm leading-tight flex-1">
          {task.title}
        </h4>
        <div className="flex items-center gap-1 ml-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit();
            }}
            className="text-gray-400 hover:text-gray-600 p-1 rounded"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Description */}
      {task.description && (
        <p className="text-xs text-gray-600 mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* Project Badge */}
      {task.project && (
        <div className="mb-3">
          <span 
            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
            style={{ 
              backgroundColor: `${task.project.color}20`, 
              color: task.project.color 
            }}
          >
            {task.project.name}
          </span>
        </div>
      )}

      {/* Tags */}
      {task.tags && task.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {task.tags.slice(0, 3).map((tag, index) => (
            <span key={index} className="badge-gray text-xs">
              {tag}
            </span>
          ))}
          {task.tags.length > 3 && (
            <span className="badge-gray text-xs">
              +{task.tags.length - 3}
            </span>
          )}
        </div>
      )}

      {/* Subtasks Progress */}
      {completionProgress !== null && (
        <div className="mb-3">
          <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
            <span>Progress</span>
            <span>{completionProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div 
              className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${completionProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-3">
          {/* Due Date */}
          {task.dueDate && (
            <div className={`flex items-center gap-1 ${
              isOverdue ? 'text-red-600' : isDueSoon ? 'text-orange-600' : 'text-gray-500'
            }`}>
              {isOverdue ? (
                <ExclamationTriangleIcon className="h-3 w-3" />
              ) : isDueSoon ? (
                <ClockIcon className="h-3 w-3" />
              ) : (
                <CalendarIcon className="h-3 w-3" />
              )}
              <span>{format(new Date(task.dueDate), 'MMM dd')}</span>
            </div>
          )}

          {/* Comments */}
          {task._count?.comments > 0 && (
            <div className="flex items-center gap-1 text-gray-500">
              <ChatBubbleLeftIcon className="h-3 w-3" />
              <span>{task._count.comments}</span>
            </div>
          )}

          {/* Subtasks */}
          {task._count?.subtasks > 0 && (
            <div className="flex items-center gap-1 text-gray-500">
              <CheckCircleIcon className="h-3 w-3" />
              <span>
                {task.subtasks?.filter(st => st.completed).length || 0}/{task._count.subtasks}
              </span>
            </div>
          )}
        </div>

        {/* Priority Indicator */}
        <div className={`priority-indicator priority-${task.priority.toLowerCase()}`} />
      </div>
    </div>
  );
};

export default TaskCard;
