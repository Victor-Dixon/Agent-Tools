import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ClipboardDocumentListIcon, 
  FolderIcon, 
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { useQuery } from 'react-query';
import { tasksAPI, projectsAPI, boardsAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const { data: tasksData, isLoading: tasksLoading } = useQuery(
    'dashboard-tasks',
    () => tasksAPI.getTasks({ limit: 10 }).then(res => res.data),
    { staleTime: 30000 }
  );

  const { data: projectsData, isLoading: projectsLoading } = useQuery(
    'dashboard-projects',
    () => projectsAPI.getProjects({ limit: 6 }).then(res => res.data),
    { staleTime: 60000 }
  );

  const { data: boardsData, isLoading: boardsLoading } = useQuery(
    'dashboard-boards',
    () => boardsAPI.getBoards({ limit: 6 }).then(res => res.data),
    { staleTime: 60000 }
  );

  const isLoading = tasksLoading || projectsLoading || boardsLoading;

  if (isLoading) {
    return <LoadingSpinner />;
  }

  const tasks = tasksData?.tasks || [];
  const projects = projectsData?.projects || [];
  const boards = boardsData?.boards || [];

  const completedTasks = tasks.filter(task => task.status === 'DONE').length;
  const inProgressTasks = tasks.filter(task => task.status === 'IN_PROGRESS').length;
  const overdueTasks = tasks.filter(task => 
    task.dueDate && new Date(task.dueDate) < new Date() && task.status !== 'DONE'
  ).length;
  const highPriorityTasks = tasks.filter(task => 
    task.priority === 'HIGH' || task.priority === 'URGENT'
  ).length;

  const stats = [
    {
      name: 'Total Tasks',
      value: tasks.length,
      icon: ClipboardDocumentListIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Completed',
      value: completedTasks,
      icon: CheckCircleIcon,
      color: 'bg-green-500',
    },
    {
      name: 'In Progress',
      value: inProgressTasks,
      icon: ClockIcon,
      color: 'bg-yellow-500',
    },
    {
      name: 'Overdue',
      value: overdueTasks,
      icon: ExclamationTriangleIcon,
      color: 'bg-red-500',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back! Here's what's happening with your tasks.</p>
        </div>
        <div className="flex gap-3">
          <Link to="/boards" className="btn-primary">
            View Boards
          </Link>
          <Link to="/projects" className="btn-outline">
            <PlusIcon className="h-4 w-4 mr-2" />
            New Project
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="card-body">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Tasks */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Recent Tasks</h3>
              <Link to="/boards" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                View all
              </Link>
            </div>
            <div className="space-y-3">
              {tasks.slice(0, 5).map((task) => (
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
                      {task.project && (
                        <p className="text-xs text-gray-500">{task.project.name}</p>
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
                  </div>
                </div>
              ))}
              {tasks.length === 0 && (
                <p className="text-gray-500 text-center py-4">No tasks yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Active Projects */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Active Projects</h3>
              <Link to="/projects" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                View all
              </Link>
            </div>
            <div className="space-y-3">
              {projects.slice(0, 5).map((project) => (
                <div key={project.id} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: project.color }}
                      />
                      <h4 className="text-sm font-medium text-gray-900">{project.name}</h4>
                    </div>
                    <span className={`badge ${
                      project.status === 'ACTIVE' ? 'badge-success' :
                      project.status === 'ON_HOLD' ? 'badge-warning' :
                      project.status === 'COMPLETED' ? 'badge-primary' :
                      'badge-gray'
                    }`}>
                      {project.status}
                    </span>
                  </div>
                  {project.description && (
                    <p className="text-xs text-gray-600 mb-2">{project.description}</p>
                  )}
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {project._count.tasks} tasks
                    </span>
                    <span className="text-xs text-gray-500">
                      {project.completionPercentage || 0}% complete
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                    <div 
                      className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${project.completionPercentage || 0}%` }}
                    />
                  </div>
                </div>
              ))}
              {projects.length === 0 && (
                <p className="text-gray-500 text-center py-4">No projects yet</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-body">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Link 
              to="/boards" 
              className="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <ClipboardDocumentListIcon className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <p className="font-medium text-blue-900">View Boards</p>
                <p className="text-sm text-blue-700">Manage your Kanban boards</p>
              </div>
            </Link>
            <Link 
              to="/projects" 
              className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
            >
              <FolderIcon className="h-8 w-8 text-green-600 mr-3" />
              <div>
                <p className="font-medium text-green-900">Projects</p>
                <p className="text-sm text-green-700">Organize your projects</p>
              </div>
            </Link>
            <Link 
              to="/boards" 
              className="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
            >
              <PlusIcon className="h-8 w-8 text-purple-600 mr-3" />
              <div>
                <p className="font-medium text-purple-900">New Task</p>
                <p className="text-sm text-purple-700">Create a new task</p>
              </div>
            </Link>
            <Link 
              to="/profile" 
              className="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <CheckCircleIcon className="h-8 w-8 text-gray-600 mr-3" />
              <div>
                <p className="font-medium text-gray-900">Profile</p>
                <p className="text-sm text-gray-700">Manage your account</p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
