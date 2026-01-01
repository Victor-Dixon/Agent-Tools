import { useQuery, useMutation, useQueryClient } from 'react-query';
import { tasksAPI } from '../services/api';
import toast from 'react-hot-toast';

export const useTasks = ({ boardId, projectId, status, priority } = {}) => {
  const queryClient = useQueryClient();

  const queryKey = ['tasks', { boardId, projectId, status, priority }];

  const {
    data: tasks = [],
    isLoading,
    error,
    refetch
  } = useQuery(
    queryKey,
    () => tasksAPI.getTasks({ boardId, projectId, status, priority }).then(res => res.data.tasks),
    {
      staleTime: 30000, // 30 seconds
      cacheTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  const createTaskMutation = useMutation(
    (taskData) => tasksAPI.createTask(taskData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks']);
        toast.success('Task created successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to create task');
      },
    }
  );

  const updateTaskMutation = useMutation(
    ({ id, taskData }) => tasksAPI.updateTask(id, taskData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks']);
        toast.success('Task updated successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to update task');
      },
    }
  );

  const deleteTaskMutation = useMutation(
    (id) => tasksAPI.deleteTask(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks']);
        toast.success('Task deleted successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to delete task');
      },
    }
  );

  const reorderTasksMutation = useMutation(
    (tasks) => tasksAPI.reorderTasks(tasks),
    {
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to reorder tasks');
      },
    }
  );

  return {
    tasks,
    loading: isLoading,
    error,
    refetch,
    createTask: createTaskMutation.mutateAsync,
    updateTask: updateTaskMutation.mutateAsync,
    deleteTask: deleteTaskMutation.mutateAsync,
    reorderTasks: reorderTasksMutation.mutateAsync,
    isCreating: createTaskMutation.isLoading,
    isUpdating: updateTaskMutation.isLoading,
    isDeleting: deleteTaskMutation.isLoading,
  };
};

export const useTask = (id) => {
  const {
    data: task,
    isLoading,
    error
  } = useQuery(
    ['task', id],
    () => tasksAPI.getTask(id).then(res => res.data.task),
    {
      enabled: !!id,
      staleTime: 30000,
    }
  );

  return {
    task,
    loading: isLoading,
    error
  };
};
