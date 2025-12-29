import React from 'react';
import { Droppable, Draggable } from 'react-beautiful-dnd';
import TaskCard from './TaskCard';
import { EllipsisHorizontalIcon } from '@heroicons/react/24/outline';

const KanbanColumn = ({ list, tasks, onTaskClick, onTaskEdit }) => {
  const getStatusColor = (listName) => {
    const name = listName.toLowerCase();
    if (name.includes('todo') || name.includes('to do')) return 'bg-gray-100';
    if (name.includes('progress') || name.includes('doing')) return 'bg-yellow-100';
    if (name.includes('review') || name.includes('testing')) return 'bg-blue-100';
    if (name.includes('done') || name.includes('complete')) return 'bg-green-100';
    return 'bg-gray-100';
  };

  const getStatusTextColor = (listName) => {
    const name = listName.toLowerCase();
    if (name.includes('todo') || name.includes('to do')) return 'text-gray-800';
    if (name.includes('progress') || name.includes('doing')) return 'text-yellow-800';
    if (name.includes('review') || name.includes('testing')) return 'text-blue-800';
    if (name.includes('done') || name.includes('complete')) return 'text-green-800';
    return 'text-gray-800';
  };

  return (
    <div className="flex-shrink-0 w-80">
      <div className="kanban-column">
        {/* Column Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(list.name)}`} />
            <h3 className={`text-lg font-semibold ${getStatusTextColor(list.name)}`}>
              {list.name}
            </h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="badge-gray text-xs">{tasks.length}</span>
            <button className="text-gray-400 hover:text-gray-600">
              <EllipsisHorizontalIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Droppable Area */}
        <Droppable droppableId={list.id}>
          {(provided, snapshot) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className={`min-h-64 transition-colors ${
                snapshot.isDraggingOver ? 'bg-gray-200' : ''
              }`}
            >
              {tasks.map((task, index) => (
                <Draggable key={task.id} draggableId={task.id} index={index}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      className={`mb-3 ${
                        snapshot.isDragging ? 'shadow-lg' : ''
                      }`}
                    >
                      <TaskCard
                        task={task}
                        onClick={() => onTaskClick(task)}
                        onEdit={() => onTaskEdit(task)}
                        isDragging={snapshot.isDragging}
                      />
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
              
              {/* Empty state */}
              {tasks.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  <p className="text-sm">No tasks yet</p>
                  <p className="text-xs">Drag tasks here or create new ones</p>
                </div>
              )}
            </div>
          )}
        </Droppable>
      </div>
    </div>
  );
};

export default KanbanColumn;
