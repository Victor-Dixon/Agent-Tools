const express = require('express');
const axios = require('axios');
const { body, validationResult, query } = require('express-validator');
const prisma = require('../utils/database');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// GitHub API configuration
const GITHUB_API_BASE = 'https://api.github.com';
const GITHUB_GRAPHQL_API = 'https://api.github.com/graphql';

// Get GitHub repositories for the authenticated user
router.get('/repositories', authenticateToken, async (req, res) => {
  try {
    const { page = 1, per_page = 30, sort = 'updated' } = req.query;

    if (!process.env.GITHUB_TOKEN) {
      return res.status(400).json({ error: 'GitHub token not configured' });
    }

    const response = await axios.get(`${GITHUB_API_BASE}/user/repos`, {
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      },
      params: {
        page,
        per_page,
        sort,
        type: 'owner'
      }
    });

    const repositories = response.data.map(repo => ({
      id: repo.id,
      name: repo.name,
      fullName: repo.full_name,
      description: repo.description,
      url: repo.html_url,
      cloneUrl: repo.clone_url,
      language: repo.language,
      stars: repo.stargazers_count,
      forks: repo.forks_count,
      isPrivate: repo.private,
      createdAt: repo.created_at,
      updatedAt: repo.updated_at,
      pushedAt: repo.pushed_at,
      defaultBranch: repo.default_branch,
      openIssues: repo.open_issues_count,
      size: repo.size
    }));

    res.json({
      repositories,
      pagination: {
        page: parseInt(page),
        per_page: parseInt(per_page),
        hasNext: response.data.length === parseInt(per_page)
      }
    });
  } catch (error) {
    console.error('GitHub repositories error:', error);
    if (error.response?.status === 401) {
      res.status(401).json({ error: 'Invalid GitHub token' });
    } else {
      res.status(500).json({ error: 'Failed to fetch GitHub repositories' });
    }
  }
});

// Get issues from a GitHub repository
router.get('/repositories/:owner/:repo/issues', authenticateToken, [
  query('state').optional().isIn(['open', 'closed', 'all']),
  query('labels').optional().isString(),
  query('page').optional().isInt({ min: 1 }),
  query('per_page').optional().isInt({ min: 1, max: 100 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { owner, repo } = req.params;
    const { state = 'open', labels, page = 1, per_page = 30 } = req.query;

    if (!process.env.GITHUB_TOKEN) {
      return res.status(400).json({ error: 'GitHub token not configured' });
    }

    const response = await axios.get(`${GITHUB_API_BASE}/repos/${owner}/${repo}/issues`, {
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      },
      params: {
        state,
        labels,
        page,
        per_page,
        sort: 'updated',
        direction: 'desc'
      }
    });

    const issues = response.data.map(issue => ({
      id: issue.id,
      number: issue.number,
      title: issue.title,
      body: issue.body,
      state: issue.state,
      url: issue.html_url,
      labels: issue.labels.map(label => ({
        id: label.id,
        name: label.name,
        color: label.color
      })),
      assignees: issue.assignees.map(assignee => ({
        id: assignee.id,
        login: assignee.login,
        avatarUrl: assignee.avatar_url
      })),
      milestone: issue.milestone ? {
        id: issue.milestone.id,
        title: issue.milestone.title,
        state: issue.milestone.state
      } : null,
      createdAt: issue.created_at,
      updatedAt: issue.updated_at,
      closedAt: issue.closed_at,
      author: {
        id: issue.user.id,
        login: issue.user.login,
        avatarUrl: issue.user.avatar_url
      }
    }));

    res.json({
      issues,
      pagination: {
        page: parseInt(page),
        per_page: parseInt(per_page),
        hasNext: response.data.length === parseInt(per_page)
      }
    });
  } catch (error) {
    console.error('GitHub issues error:', error);
    if (error.response?.status === 404) {
      res.status(404).json({ error: 'Repository not found' });
    } else if (error.response?.status === 401) {
      res.status(401).json({ error: 'Invalid GitHub token' });
    } else {
      res.status(500).json({ error: 'Failed to fetch GitHub issues' });
    }
  }
});

// Import GitHub repository as a project
router.post('/import/:owner/:repo', authenticateToken, async (req, res) => {
  try {
    const { owner, repo } = req.params;
    const { importIssues = false, projectType = 'GITHUB' } = req.body;

    if (!process.env.GITHUB_TOKEN) {
      return res.status(400).json({ error: 'GitHub token not configured' });
    }

    // Get repository information
    const repoResponse = await axios.get(`${GITHUB_API_BASE}/repos/${owner}/${repo}`, {
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });

    const repoData = repoResponse.data;

    // Check if project already exists
    const existingProject = await prisma.project.findFirst({
      where: {
        githubId: repoData.id,
        userId: req.user.id
      }
    });

    if (existingProject) {
      return res.status(400).json({ error: 'Project already imported' });
    }

    // Create project
    const project = await prisma.project.create({
      data: {
        name: repoData.name,
        description: repoData.description || `GitHub repository: ${repoData.full_name}`,
        type: projectType,
        status: 'ACTIVE',
        githubUrl: repoData.html_url,
        githubId: repoData.id,
        color: getLanguageColor(repoData.language),
        userId: req.user.id
      }
    });

    let importedIssues = [];

    // Import issues if requested
    if (importIssues) {
      const issuesResponse = await axios.get(`${GITHUB_API_BASE}/repos/${owner}/${repo}/issues`, {
        headers: {
          'Authorization': `token ${process.env.GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json'
        },
        params: {
          state: 'open',
          per_page: 100
        }
      });

      const issues = issuesResponse.data;

      // Create tasks from issues
      const tasks = await Promise.all(
        issues.map(async (issue, index) => {
          const priority = getPriorityFromLabels(issue.labels);
          const status = getStatusFromGitHub(issue.state, issue.assignees);

          return prisma.task.create({
            data: {
              title: issue.title,
              description: issue.body || `GitHub Issue #${issue.number}`,
              status,
              priority,
              tags: issue.labels.map(label => label.name),
              position: index + 1,
              projectId: project.id,
              userId: req.user.id,
              metadata: {
                githubIssueId: issue.id,
                githubIssueNumber: issue.number,
                githubUrl: issue.html_url,
                importedAt: new Date().toISOString()
              }
            }
          });
        })
      );

      importedIssues = tasks;
    }

    res.status(201).json({
      message: 'GitHub repository imported successfully',
      project,
      importedIssues: importedIssues.length,
      issues: importedIssues
    });
  } catch (error) {
    console.error('GitHub import error:', error);
    if (error.response?.status === 404) {
      res.status(404).json({ error: 'Repository not found' });
    } else if (error.response?.status === 401) {
      res.status(401).json({ error: 'Invalid GitHub token' });
    } else {
      res.status(500).json({ error: 'Failed to import GitHub repository' });
    }
  }
});

// Sync GitHub issues with existing project
router.post('/sync/:projectId', authenticateToken, [
  body('owner').isString(),
  body('repo').isString()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { projectId } = req.params;
    const { owner, repo } = req.body;

    // Verify project belongs to user
    const project = await prisma.project.findFirst({
      where: {
        id: projectId,
        userId: req.user.id
      }
    });

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    if (!process.env.GITHUB_TOKEN) {
      return res.status(400).json({ error: 'GitHub token not configured' });
    }

    // Get current issues from GitHub
    const issuesResponse = await axios.get(`${GITHUB_API_BASE}/repos/${owner}/${repo}/issues`, {
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      },
      params: {
        state: 'all',
        per_page: 100
      }
    });

    const githubIssues = issuesResponse.data;
    const syncedTasks = [];

    // Get existing tasks with GitHub metadata
    const existingTasks = await prisma.task.findMany({
      where: {
        projectId,
        metadata: {
          path: ['githubIssueId'],
          not: null
        }
      }
    });

    const existingGitHubIds = new Set(
      existingTasks.map(task => task.metadata?.githubIssueId)
    );

    // Create new tasks for new GitHub issues
    for (const issue of githubIssues) {
      if (!existingGitHubIds.has(issue.id)) {
        const priority = getPriorityFromLabels(issue.labels);
        const status = getStatusFromGitHub(issue.state, issue.assignees);

        const task = await prisma.task.create({
          data: {
            title: issue.title,
            description: issue.body || `GitHub Issue #${issue.number}`,
            status,
            priority,
            tags: issue.labels.map(label => label.name),
            position: 0,
            projectId,
            userId: req.user.id,
            metadata: {
              githubIssueId: issue.id,
              githubIssueNumber: issue.number,
              githubUrl: issue.html_url,
              syncedAt: new Date().toISOString()
            }
          }
        });

        syncedTasks.push(task);
      }
    }

    res.json({
      message: 'GitHub issues synced successfully',
      syncedTasks: syncedTasks.length,
      tasks: syncedTasks
    });
  } catch (error) {
    console.error('GitHub sync error:', error);
    if (error.response?.status === 404) {
      res.status(404).json({ error: 'Repository not found' });
    } else if (error.response?.status === 401) {
      res.status(401).json({ error: 'Invalid GitHub token' });
    } else {
      res.status(500).json({ error: 'Failed to sync GitHub issues' });
    }
  }
});

// Helper functions
function getLanguageColor(language) {
  const colors = {
    'JavaScript': '#F7DF1E',
    'TypeScript': '#3178C6',
    'Python': '#3776AB',
    'Java': '#ED8B00',
    'C++': '#00599C',
    'C#': '#239120',
    'Go': '#00ADD8',
    'Rust': '#DEA584',
    'PHP': '#777BB4',
    'Ruby': '#CC342D',
    'Swift': '#FA7343',
    'Kotlin': '#7F52FF',
    'HTML': '#E34F26',
    'CSS': '#1572B6',
    'Vue': '#4FC08D',
    'React': '#61DAFB',
    'Angular': '#DD0031',
    'Node.js': '#339933'
  };
  return colors[language] || '#10B981';
}

function getPriorityFromLabels(labels) {
  const labelNames = labels.map(label => label.name.toLowerCase());
  
  if (labelNames.some(name => name.includes('urgent') || name.includes('critical'))) {
    return 'URGENT';
  } else if (labelNames.some(name => name.includes('high') || name.includes('priority'))) {
    return 'HIGH';
  } else if (labelNames.some(name => name.includes('low'))) {
    return 'LOW';
  }
  
  return 'MEDIUM';
}

function getStatusFromGitHub(state, assignees) {
  if (state === 'closed') {
    return 'DONE';
  } else if (assignees && assignees.length > 0) {
    return 'IN_PROGRESS';
  } else {
    return 'TODO';
  }
}

module.exports = router;
