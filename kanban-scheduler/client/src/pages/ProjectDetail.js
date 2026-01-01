import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { projectsAPI } from '../services/api';
import { useTasks } from '../hooks/useTasks';
import LoadingSpinner from '../components/LoadingSpinner';
import { ArrowLeftIcon, CalendarIcon, UsersIcon } from '@heroicons/react/24/outline';
import ProjectAccessManager from '../components/ProjectAccessManager';

const ProjectDetail = () => {
  const { id } = useParams();

  const { data: project, isLoading: projectLoading, error: projectError } = useQuery(
    ['project', id],
    () => projectsAPI.getProject(id).then(res => res.data.project),
    {
      enabled: !!id,
      staleTime: 30000,
    }
  );

  const { tasks, loading: tasksLoading } = useTasks({ projectId: id });

  const isLoading = projectLoading || tasksLoading;

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (projectError) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading project: {projectError.message}</p>
        <Link to="/projects" className="btn-primary mt-4">
          Back to Projects
        </Link>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Project not found</p>
        <Link to="/projects" className="btn-primary mt-4">
          Back to Projects
        </Link>
      </div>
    );
  }

  const taskStats = project.stats || {};
  const completedTasks = taskStats.completedTasks || 0;
  const totalTasks = taskStats.totalTasks || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link 
            to="/projects" 
            className="text-gray-400 hover:text-gray-600"
          >
            <ArrowLeftIcon className="h-6 w-6" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <div 
                className="w-4 h-4 rounded"
                style={{ backgroundColor: project.color }}
              />
              <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
            </div>
            {project.description && (
              <p className="text-gray-600 mt-1">{project.description}</p>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className={`badge ${
            project.status === 'ACTIVE' ? 'badge-success' :
            project.status === 'ON_HOLD' ? 'badge-warning' :
            project.status === 'COMPLETED' ? 'badge-primary' :
            'badge-gray'
          }`}>
            {project.status}
          </span>
        </div>
      </div>

      {/* Project Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 rounded-lg bg-blue-100">
                <span className="text-blue-600 font-semibold text-sm">Total</span>
              </div>
              <div className="ml-3">
                <p className="text-2xl font-semibold text-gray-900">{totalTasks}</p>
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
                <p className="text-2xl font-semibold text-gray-900">{completedTasks}</p>
                <p className="text-sm text-gray-600">Completed</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 rounded-lg bg-red-100">
                <span className="text-red-600 font-semibold text-sm">Overdue</span>
              </div>
              <div className="ml-3">
                <p className="text-2xl font-semibold text-gray-900">{taskStats.overdueTasks || 0}</p>
                <p className="text-sm text-gray-600">Overdue</p>
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
                <p className="text-2xl font-semibold text-gray-900">{taskStats.completionPercentage || 0}%</p>
                <p className="text-sm text-gray-600">Complete</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Project Details */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Tasks List */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-body">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Tasks</h3>
              {tasks.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">No tasks in this project yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {tasks.map((task) => (
                    <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${
                          task.status === 'DONE' ? 'bg-green-500' :
                          task.status === 'IN_PROGRESS' ? 'bg-blue-500' :
                          task.status === 'BLOCKED' ? 'bg-red-500' :
                          'bg-gray-400'
                        }`} />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{task.title}</p>
                          {task.description && (
                            <p className="text-xs text-gray-600">{task.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`badge ${
                          task.priority === 'URGENT' ? 'badge-danger' :
                          task.priority === 'HIGH' ? 'badge-warning' :
                          task.priority === 'MEDIUM' ? 'badge-primary' :
                          'badge-gray'
                        }`}>
                          {task.priority}
                        </span>
                        {task.dueDate && (
                          <span className="text-xs text-gray-500">
                            {new Date(task.dueDate).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Project Info */}
        <div className="space-y-6">
          <div className="card">
            <div className="card-body">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Project Info</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Type</span>
                  <span className="text-sm font-medium text-gray-900">{project.type}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Status</span>
                  <span className={`badge ${
                    project.status === 'ACTIVE' ? 'badge-success' :
                    project.status === 'ON_HOLD' ? 'badge-warning' :
                    project.status === 'COMPLETED' ? 'badge-primary' :
                    'badge-gray'
                  }`}>
                    {project.status}
                  </span>
                </div>
                {project.startDate && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Start Date</span>
                    <span className="text-sm font-medium text-gray-900">
                      {new Date(project.startDate).toLocaleDateString()}
                    </span>
                  </div>
                )}
                {project.endDate && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">End Date</span>
                    <span className="text-sm font-medium text-gray-900">
                      {new Date(project.endDate).toLocaleDateString()}
                    </span>
                  </div>
                )}
                {project.githubUrl && (
                  <div className="pt-3 border-t border-gray-200">
                    <a
                      href={project.githubUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      View on GitHub →
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Progress Chart */}
          <div className="card">
            <div className="card-body">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Progress</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Completion</span>
                  <span className="font-medium text-gray-900">{taskStats.completionPercentage || 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-primary-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${taskStats.completionPercentage || 0}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500">
                  {completedTasks} of {totalTasks} tasks completed
                </div>
              </div>
            </div>
          </div>

          {/* Project Access & Members */}
          <div className="card">
            <div className="card-body">
              <ProjectAccessManager
                projectId={project.id}
                projectName={project.name}
                ownerUsername={project.user?.username}
                isOwner={project.isOwner}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetail;
