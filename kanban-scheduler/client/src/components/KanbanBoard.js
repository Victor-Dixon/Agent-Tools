import React, { useState } from 'react';
import { DragDropContext, Droppable } from 'react-beautiful-dnd';
import KanbanColumn from './KanbanColumn';
import TaskModal from './TaskModal';
import { useTasks } from '../hooks/useTasks';
import { tasksAPI } from '../services/api';
import toast from 'react-hot-toast';
import { PlusIcon } from '@heroicons/react/24/outline';

const KanbanBoard = ({ boardId, projectId, onTaskClick }) => {
  const [selectedTask, setSelectedTask] = useState(null);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);

  const {
    tasks,
    lists,
    loading,
    error,
    refetch
  } = useTasks({ boardId, projectId });

  const handleTaskClick = (task) => {
    setSelectedTask(task);
    setIsTaskModalOpen(true);
    if (onTaskClick) {
      onTaskClick(task);
    }
  };

  const handleTaskEdit = (task) => {
    setEditingTask(task);
    setIsTaskModalOpen(true);
  };

  const handleTaskCreate = () => {
    setEditingTask({
      title: '',
      description: '',
      status: 'TODO',
      priority: 'MEDIUM',
      projectId,
      boardId
    });
    setIsTaskModalOpen(true);
  };

  const handleTaskSave = async (taskData) => {
    try {
      if (editingTask?.id) {
        await tasksAPI.updateTask(editingTask.id, taskData);
        toast.success('Task updated successfully');
      } else {
        await tasksAPI.createTask(taskData);
        toast.success('Task created successfully');
      }
      setIsTaskModalOpen(false);
      setEditingTask(null);
      refetch();
    } catch (error) {
      toast.error('Failed to save task');
    }
  };

  const handleTaskDelete = async (taskId) => {
    try {
      await tasksAPI.deleteTask(taskId);
      toast.success('Task deleted successfully');
      setIsTaskModalOpen(false);
      setEditingTask(null);
      refetch();
    } catch (error) {
      toast.error('Failed to delete task');
    }
  };

  const handleDragEnd = async (result) => {
    const { destination, source, draggableId } = result;

    if (!destination) return;

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const sourceListId = source.droppableId === 'no-list' ? null : source.droppableId;
    const destListId = destination.droppableId === 'no-list' ? null : destination.droppableId;

    // Update task position and list
    try {
      await tasksAPI.updateTask(draggableId, {
        listId: destListId,
        position: destination.index
      });

      // Reorder tasks within the source and destination lists
      const sourceTasks = tasks.filter(task => 
        (sourceListId ? task.listId === sourceListId : task.listId === null)
      );
      const destTasks = tasks.filter(task => 
        (destListId ? task.listId === destListId : task.listId === null)
      );

      const movedTask = sourceTasks.find(task => task.id === draggableId);
      sourceTasks.splice(source.index, 1);
      
      if (sourceListId === destListId) {
        sourceTasks.splice(destination.index, 0, movedTask);
      } else {
        destTasks.splice(destination.index, 0, movedTask);
      }

      // Update positions for all affected tasks
      const tasksToUpdate = [];
      
      sourceTasks.forEach((task, index) => {
        if (task.position !== index) {
          tasksToUpdate.push({ id: task.id, position: index });
        }
      });

      if (sourceListId !== destListId) {
        destTasks.forEach((task, index) => {
          if (task.position !== index) {
            tasksToUpdate.push({ id: task.id, position: index });
          }
        });
      }

      if (tasksToUpdate.length > 0) {
        await tasksAPI.reorderTasks(tasksToUpdate);
      }

      refetch();
    } catch (error) {
      toast.error('Failed to move task');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading board: {error.message}</p>
      </div>
    );
  }

  // Group tasks by list
  const tasksByList = lists.reduce((acc, list) => {
    acc[list.id] = tasks.filter(task => task.listId === list.id);
    return acc;
  }, {});

  const unassignedTasks = tasks.filter(task => !task.listId);

  return (
    <div className="h-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Kanban Board</h1>
          <p className="text-gray-600">Drag and drop tasks to organize your work</p>
        </div>
        <button
          onClick={handleTaskCreate}
          className="btn-primary flex items-center gap-2"
        >
          <PlusIcon className="h-5 w-5" />
          Add Task
        </button>
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="flex gap-6 overflow-x-auto pb-4">
          {/* Lists */}
          {lists.map((list) => (
            <KanbanColumn
              key={list.id}
              list={list}
              tasks={tasksByList[list.id] || []}
              onTaskClick={handleTaskClick}
              onTaskEdit={handleTaskEdit}
            />
          ))}

          {/* Unassigned tasks column */}
          {unassignedTasks.length > 0 && (
            <div className="flex-shrink-0 w-80">
              <div className="kanban-column">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Unassigned</h3>
                  <span className="badge-gray">{unassignedTasks.length}</span>
                </div>
                <Droppable droppableId="no-list">
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`min-h-64 ${snapshot.isDraggingOver ? 'bg-gray-200' : ''}`}
                    >
                      {unassignedTasks.map((task, index) => (
                        <div
                          key={task.id}
                          onClick={() => handleTaskClick(task)}
                          className="kanban-task cursor-pointer"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900 mb-1">{task.title}</h4>
                              {task.description && (
                                <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                                  {task.description}
                                </p>
                              )}
                              <div className="flex items-center gap-2">
                                <span className={`priority-indicator priority-${task.priority.toLowerCase()}`} />
                                <span className="badge-gray text-xs">{task.priority}</span>
                                {task.project && (
                                  <span 
                                    className="badge text-xs"
                                    style={{ backgroundColor: task.project.color + '20', color: task.project.color }}
                                  >
                                    {task.project.name}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
            </div>
          )}
        </div>
      </DragDropContext>

      {/* Task Modal */}
      <TaskModal
        isOpen={isTaskModalOpen}
        onClose={() => {
          setIsTaskModalOpen(false);
          setEditingTask(null);
        }}
        task={editingTask}
        onSave={handleTaskSave}
        onDelete={editingTask?.id ? handleTaskDelete : null}
        projects={[]} // You might want to pass projects here
      />
    </div>
  );
};

export default KanbanBoard;
