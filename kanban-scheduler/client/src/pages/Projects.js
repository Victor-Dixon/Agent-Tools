import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { projectsAPI } from '../services/api';
import { PlusIcon, FolderIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import { getPhaseInfo } from '../utils/phases';

const Projects = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedType, setSelectedType] = useState('ALL');
  const queryClient = useQueryClient();

  const { data: projectsData, isLoading, error } = useQuery(
    ['projects', { type: selectedType === 'ALL' ? undefined : selectedType }],
    () => projectsAPI.getProjects({ type: selectedType === 'ALL' ? undefined : selectedType }).then(res => res.data),
    { staleTime: 60000 }
  );

  const createProjectMutation = useMutation(
    (projectData) => projectsAPI.createProject(projectData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['projects']);
        setShowCreateModal(false);
        toast.success('Project created successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to create project');
      },
    }
  );

  const handleCreateProject = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const projectData = {
      name: formData.get('name'),
      description: formData.get('description'),
      type: formData.get('type'),
      phase: formData.get('phase') || '0A',
      color: formData.get('color') || '#10B981'
    };
    createProjectMutation.mutate(projectData);
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading projects: {error.message}</p>
      </div>
    );
  }

  const projects = projectsData?.projects || [];

  const projectTypes = [
    { value: 'ALL', label: 'All Projects' },
    { value: 'PERSONAL', label: 'Personal' },
    { value: 'WORK', label: 'Work' },
    { value: 'GITHUB', label: 'GitHub' },
    { value: 'LEARNING', label: 'Learning' },
    { value: 'HEALTH', label: 'Health' },
    { value: 'FINANCE', label: 'Finance' },
    { value: 'OTHER', label: 'Other' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-600">Organize your work and life with projects</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <PlusIcon className="h-5 w-5" />
          New Project
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {projectTypes.map((type) => (
            <button
              key={type.value}
              onClick={() => setSelectedType(type.value)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                selectedType === type.value
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {type.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Projects Grid */}
      {projects.length === 0 ? (
        <div className="text-center py-12">
          <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No projects</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating a new project.</p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              New Project
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Link key={project.id} to={`/projects/${project.id}`}>
              <div className="card hover:shadow-lg transition-shadow cursor-pointer">
                <div className="card-body">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: project.color }}
                      />
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <p className="text-sm text-gray-600">{project.type}</p>
                          {project.phase && (
                            <span 
                              className="text-xs px-2 py-0.5 rounded-full font-medium"
                              style={{ 
                                backgroundColor: getPhaseInfo(project.phase).color + '20',
                                color: getPhaseInfo(project.phase).color
                              }}
                            >
                              {getPhaseInfo(project.phase).icon} {project.phase}
                            </span>
                          )}
                        </div>
                      </div>
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
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">{project.description}</p>
                  )}

                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>{project._count.tasks} tasks</span>
                      <span>{project.completionPercentage || 0}% complete</span>
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${project.completionPercentage || 0}%` }}
                      />
                    </div>
                  </div>

                  {project.githubUrl && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <a
                        href={project.githubUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="text-sm text-blue-600 hover:text-blue-800"
                      >
                        View on GitHub →
                      </a>
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" onClick={() => setShowCreateModal(false)}>
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <form onSubmit={handleCreateProject}>
                <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Create New Project
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Project Name *
                      </label>
                      <input
                        name="name"
                        required
                        className="input"
                        placeholder="Enter project name"
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
                        placeholder="Enter project description"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Type
                      </label>
                      <select name="type" className="select">
                        <option value="PERSONAL">Personal</option>
                        <option value="WORK">Work</option>
                        <option value="GITHUB">GitHub</option>
                        <option value="LEARNING">Learning</option>
                        <option value="HEALTH">Health</option>
                        <option value="FINANCE">Finance</option>
                        <option value="OTHER">Other</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Phase
                      </label>
                      <select name="phase" className="select" defaultValue="0A">
                        <option value="0A">📋 0A - Organization and Planning</option>
                        <option value="0B">🔍 0B - Research</option>
                        <option value="1">🎨 1 - Design</option>
                        <option value="2">💻 2 - Development</option>
                        <option value="3">🧪 3 - Testing</option>
                        <option value="4">🚀 4 - Deployment</option>
                        <option value="5">🔧 5 - Maintenance</option>
                      </select>
                      <p className="mt-1 text-xs text-gray-500">
                        All projects start in Phase 0A (Organization and Planning)
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Color
                      </label>
                      <input
                        name="color"
                        type="color"
                        defaultValue="#10B981"
                        className="h-10 w-20 rounded border border-gray-300"
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                  <button
                    type="submit"
                    disabled={createProjectMutation.isLoading}
                    className="btn-primary"
                  >
                    {createProjectMutation.isLoading ? 'Creating...' : 'Create Project'}
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

export default Projects;
