import { useQuery, useMutation, useQueryClient } from 'react-query';
import { projectsAPI } from '../services/api';
import toast from 'react-hot-toast';

export const useProjects = ({ type, status } = {}) => {
  const queryClient = useQueryClient();

  const queryKey = ['projects', { type, status }];

  const {
    data: projects = [],
    isLoading,
    error,
    refetch
  } = useQuery(
    queryKey,
    () => projectsAPI.getProjects({ type, status }).then(res => res.data.projects),
    {
      staleTime: 60000, // 1 minute
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  );

  const createProjectMutation = useMutation(
    (projectData) => projectsAPI.createProject(projectData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['projects']);
        toast.success('Project created successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to create project');
      },
    }
  );

  const updateProjectMutation = useMutation(
    ({ id, projectData }) => projectsAPI.updateProject(id, projectData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['projects']);
        toast.success('Project updated successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to update project');
      },
    }
  );

  const deleteProjectMutation = useMutation(
    (id) => projectsAPI.deleteProject(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['projects']);
        toast.success('Project deleted successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to delete project');
      },
    }
  );

  return {
    data: projects,
    loading: isLoading,
    error,
    refetch,
    createProject: createProjectMutation.mutateAsync,
    updateProject: updateProjectMutation.mutateAsync,
    deleteProject: deleteProjectMutation.mutateAsync,
    isCreating: createProjectMutation.isLoading,
    isUpdating: updateProjectMutation.isLoading,
    isDeleting: deleteProjectMutation.isLoading,
  };
};

export const useProject = (id) => {
  const {
    data: project,
    isLoading,
    error
  } = useQuery(
    ['project', id],
    () => projectsAPI.getProject(id).then(res => res.data.project),
    {
      enabled: !!id,
      staleTime: 30000,
    }
  );

  return {
    project,
    loading: isLoading,
    error
  };
};

export const useProjectStats = (id) => {
  const {
    data: stats,
    isLoading,
    error
  } = useQuery(
    ['project-stats', id],
    () => projectsAPI.getProjectStats(id).then(res => res.data.stats),
    {
      enabled: !!id,
      staleTime: 60000,
    }
  );

  return {
    stats,
    loading: isLoading,
    error
  };
};
