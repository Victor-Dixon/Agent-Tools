import axios from 'axios';
import toast from 'react-hot-toast';

// Automatically detect if we're accessing from network or localhost
const getApiUrl = () => {
  // If REACT_APP_API_URL is set, use it
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // If accessed from network (not localhost), use the network IP
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    // Use the same hostname the client is accessed from
    return `${window.location.protocol}//${window.location.hostname}:5000/api`;
  }
  
  // Default to localhost for local development
  return 'http://localhost:5000/api';
};

const API_BASE_URL = getApiUrl();

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    }
    return Promise.reject(error);
  }
);

// API service functions
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (profileData) => api.put('/auth/profile', profileData),
};

export const tasksAPI = {
  getTasks: (params) => api.get('/tasks', { params }),
  getTask: (id) => api.get(`/tasks/${id}`),
  createTask: (taskData) => api.post('/tasks', taskData),
  updateTask: (id, taskData) => api.put(`/tasks/${id}`, taskData),
  deleteTask: (id) => api.delete(`/tasks/${id}`),
  reorderTasks: (tasks) => api.put('/tasks/reorder', { tasks }),
};

export const projectsAPI = {
  getProjects: (params) => api.get('/projects', { params }),
  getProject: (id) => api.get(`/projects/${id}`),
  createProject: (projectData) => api.post('/projects', projectData),
  updateProject: (id, projectData) => api.put(`/projects/${id}`, projectData),
  deleteProject: (id) => api.delete(`/projects/${id}`),
  getProjectStats: (id) => api.get(`/projects/${id}/stats`),
};

export const boardsAPI = {
  getBoards: (params) => api.get('/boards', { params }),
  getBoard: (id) => api.get(`/boards/${id}`),
  createBoard: (boardData) => api.post('/boards', boardData),
  updateBoard: (id, boardData) => api.put(`/boards/${id}`, boardData),
  deleteBoard: (id) => api.delete(`/boards/${id}`),
  createList: (boardId, listData) => api.post(`/boards/${boardId}/lists`, listData),
  updateList: (listId, listData) => api.put(`/boards/lists/${listId}`, listData),
  deleteList: (listId) => api.delete(`/boards/lists/${listId}`),
  reorderLists: (boardId, lists) => api.put(`/boards/${boardId}/lists/reorder`, { lists }),
};

export const githubAPI = {
  getRepositories: (params) => api.get('/github/repositories', { params }),
  getRepositoryIssues: (owner, repo, params) => api.get(`/github/repositories/${owner}/${repo}/issues`, { params }),
  importRepository: (owner, repo, options) => api.post(`/github/import/${owner}/${repo}`, options),
  syncRepository: (projectId, owner, repo) => api.post(`/github/sync/${projectId}`, { owner, repo }),
};

export const aiAgentAPI = {
  getTasks: (params) => api.get('/ai/tasks', { 
    params,
    headers: { 'X-API-Key': process.env.REACT_APP_AI_API_KEY }
  }),
  createTask: (taskData) => api.post('/ai/tasks', taskData, {
    headers: { 'X-API-Key': process.env.REACT_APP_AI_API_KEY }
  }),
  updateTask: (id, taskData) => api.put(`/ai/tasks/${id}`, taskData, {
    headers: { 'X-API-Key': process.env.REACT_APP_AI_API_KEY }
  }),
  getProjects: (params) => api.get('/ai/projects', {
    params,
    headers: { 'X-API-Key': process.env.REACT_APP_AI_API_KEY }
  }),
  getDashboard: (params) => api.get('/ai/dashboard', {
    params,
    headers: { 'X-API-Key': process.env.REACT_APP_AI_API_KEY }
  }),
};

export const whiteboardsAPI = {
  getWhiteboards: (params) => api.get('/whiteboards', { params }),
  getWhiteboard: (id) => api.get(`/whiteboards/${id}`),
  createWhiteboard: (whiteboardData) => api.post('/whiteboards', whiteboardData),
  updateWhiteboard: (id, whiteboardData) => api.put(`/whiteboards/${id}`, whiteboardData),
  deleteWhiteboard: (id) => api.delete(`/whiteboards/${id}`),
  uploadImage: (formData) => api.post('/whiteboards/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  transcribeImage: (id) => api.post(`/whiteboards/${id}/transcribe`),
};

export const projectSharingAPI = {
  requestAccess: (projectId, message) => api.post(`/project-sharing/request/${projectId}`, { message }),
  requestAccessByUsername: (ownerUsername, projectName, message) => 
    api.post('/project-sharing/request-by-username', { ownerUsername, projectName, message }),
  getPendingInvitations: () => api.get('/project-sharing/pending-invitations'),
  getMyRequests: () => api.get('/project-sharing/my-requests'),
  respondToInvitation: (invitationId, action) => 
    api.put(`/project-sharing/invitation/${invitationId}/respond`, { action }),
  getProjectMembers: (projectId) => api.get(`/project-sharing/project/${projectId}/members`),
  removeMember: (projectId, userId) => api.delete(`/project-sharing/project/${projectId}/members/${userId}`),
  cancelRequest: (invitationId) => api.delete(`/project-sharing/request/${invitationId}`),
};

export default api;
