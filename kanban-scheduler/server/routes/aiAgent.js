const express = require('express');
const { body, validationResult, query } = require('express-validator');
const prisma = require('../utils/database');
const { authenticateToken, authenticateAIAgent } = require('../middleware/auth');

const router = express.Router();

// AI Agent routes - these can be accessed with API key for AI agents
// or with user authentication for human users

// Get all tasks for AI agent access
router.get('/tasks', authenticateAIAgent, [
  query('userId').optional().isUUID(),
  query('status').optional().isIn(['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'BLOCKED', 'CANCELLED']),
  query('priority').optional().isIn(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
  query('projectId').optional().isUUID(),
  query('limit').optional().isInt({ min: 1, max: 100 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const {
      userId,
      status,
      priority,
      projectId,
      limit = 50,
      includeCompleted = 'false'
    } = req.query;

    const where = {};
    
    if (userId) where.userId = userId;
    if (status) where.status = status;
    if (priority) where.priority = priority;
    if (projectId) where.projectId = projectId;
    if (includeCompleted === 'false') {
      where.status = { not: 'DONE' };
    }

    const tasks = await prisma.task.findMany({
      where,
      include: {
        project: {
          select: { id: true, name: true, type: true, status: true }
        },
        board: {
          select: { id: true, name: true }
        },
        list: {
          select: { id: true, name: true }
        },
        user: {
          select: { id: true, username: true, name: true }
        },
        comments: {
          select: {
            id: true,
            content: true,
            createdAt: true,
            user: {
              select: { username: true }
            }
          },
          orderBy: { createdAt: 'desc' },
          take: 3
        },
        subtasks: {
          select: { id: true, title: true, completed: true }
        }
      },
      orderBy: [
        { priority: 'desc' },
        { dueDate: 'asc' },
        { createdAt: 'desc' }
      ],
      take: parseInt(limit)
    });

    // Add AI-friendly metadata
    const aiTasks = tasks.map(task => ({
      ...task,
      aiMetadata: {
        isOverdue: task.dueDate ? task.dueDate < new Date() && task.status !== 'DONE' : false,
        daysUntilDue: task.dueDate ? Math.ceil((task.dueDate - new Date()) / (1000 * 60 * 60 * 24)) : null,
        completionProgress: task.subtasks.length > 0 
          ? Math.round((task.subtasks.filter(st => st.completed).length / task.subtasks.length) * 100)
          : null,
        hasComments: task.comments.length > 0,
        lastActivity: task.updatedAt
      }
    }));

    res.json({
      tasks: aiTasks,
      total: tasks.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('AI Agent get tasks error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create task via AI agent
router.post('/tasks', authenticateAIAgent, [
  body('userId').isUUID(),
  body('title').trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim(),
  body('status').optional().isIn(['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'BLOCKED', 'CANCELLED']),
  body('priority').optional().isIn(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
  body('dueDate').optional().isISO8601(),
  body('projectId').optional().isUUID(),
  body('tags').optional().isArray(),
  body('aiGenerated').optional().isBoolean()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const {
      userId,
      title,
      description,
      status = 'TODO',
      priority = 'MEDIUM',
      dueDate,
      projectId,
      tags = [],
      aiGenerated = true
    } = req.body;

    // Verify user exists
    const user = await prisma.user.findUnique({
      where: { id: userId }
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Get the next position
    const lastTask = await prisma.task.findFirst({
      where: { userId, listId: null },
      orderBy: { position: 'desc' }
    });
    const position = (lastTask?.position || 0) + 1;

    const task = await prisma.task.create({
      data: {
        title,
        description,
        status,
        priority,
        dueDate: dueDate ? new Date(dueDate) : null,
        projectId,
        tags,
        position,
        userId,
        metadata: {
          aiGenerated,
          createdBy: 'ai-agent',
          createdAt: new Date().toISOString()
        }
      },
      include: {
        project: {
          select: { id: true, name: true, type: true }
        },
        user: {
          select: { id: true, username: true, name: true }
        }
      }
    });

    res.status(201).json({
      message: 'Task created successfully by AI agent',
      task
    });
  } catch (error) {
    console.error('AI Agent create task error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Claim a task (assign to agent)
router.post('/tasks/:id/claim', authenticateAIAgent, [
  body('agentId').optional().isString(),
  body('agentName').optional().isString()
], async (req, res) => {
  try {
    const taskId = req.params.id;
    const { agentId, agentName } = req.body;

    const existingTask = await prisma.task.findUnique({
      where: { id: taskId }
    });

    if (!existingTask) {
      return res.status(404).json({ error: 'Task not found' });
    }

    // Check if already claimed
    const metadata = existingTask.metadata ? JSON.parse(existingTask.metadata) : {};
    if (metadata.claimedBy && metadata.claimedBy !== agentId) {
      return res.status(409).json({ 
        error: 'Task already claimed by another agent',
        claimedBy: metadata.claimedBy
      });
    }

    // Claim the task
    const updatedMetadata = {
      ...metadata,
      claimedBy: agentId || agentName || 'unknown-agent',
      claimedAt: new Date().toISOString(),
      status: 'IN_PROGRESS'
    };

    const task = await prisma.task.update({
      where: { id: taskId },
      data: {
        status: 'IN_PROGRESS',
        metadata: JSON.stringify(updatedMetadata)
      },
      include: {
        project: {
          select: { id: true, name: true, type: true }
        },
        user: {
          select: { id: true, username: true, name: true }
        }
      }
    });

    res.json({
      message: 'Task claimed successfully',
      task,
      claimedBy: updatedMetadata.claimedBy
    });
  } catch (error) {
    console.error('Claim task error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Release a task (unclaim)
router.post('/tasks/:id/release', authenticateAIAgent, async (req, res) => {
  try {
    const taskId = req.params.id;

    const existingTask = await prisma.task.findUnique({
      where: { id: taskId }
    });

    if (!existingTask) {
      return res.status(404).json({ error: 'Task not found' });
    }

    const metadata = existingTask.metadata ? JSON.parse(existingTask.metadata) : {};
    delete metadata.claimedBy;
    delete metadata.claimedAt;

    const task = await prisma.task.update({
      where: { id: taskId },
      data: {
        status: 'TODO',
        metadata: JSON.stringify(metadata)
      }
    });

    res.json({
      message: 'Task released successfully',
      task
    });
  } catch (error) {
    console.error('Release task error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get tasks claimed by an agent
router.get('/tasks/claimed', authenticateAIAgent, [
  query('agentId').optional().isString(),
  query('agentName').optional().isString()
], async (req, res) => {
  try {
    const { agentId, agentName } = req.query;
    const identifier = agentId || agentName;

    if (!identifier) {
      return res.status(400).json({ error: 'agentId or agentName required' });
    }

    // Get all tasks and filter by claimedBy in metadata
    const allTasks = await prisma.task.findMany({
      where: {
        status: { in: ['IN_PROGRESS', 'IN_REVIEW'] }
      },
      include: {
        project: {
          select: { id: true, name: true, type: true }
        }
      }
    });

    const claimedTasks = allTasks.filter(task => {
      if (!task.metadata) return false;
      try {
        const metadata = JSON.parse(task.metadata);
        return metadata.claimedBy === identifier;
      } catch {
        return false;
      }
    });

    res.json({
      agent: identifier,
      tasks: claimedTasks,
      count: claimedTasks.length
    });
  } catch (error) {
    console.error('Get claimed tasks error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update task via AI agent
router.put('/tasks/:id', authenticateAIAgent, [
  body('title').optional().trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim(),
  body('status').optional().isIn(['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'BLOCKED', 'CANCELLED']),
  body('priority').optional().isIn(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
  body('dueDate').optional().isISO8601(),
  body('tags').optional().isArray(),
  body('aiGenerated').optional().isBoolean(),
  body('agentId').optional().isString(),
  body('agentName').optional().isString()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const taskId = req.params.id;
    const updateData = {};

    // Check if task exists
    const existingTask = await prisma.task.findUnique({
      where: { id: taskId },
      include: { user: { select: { id: true, username: true } } }
    });

    if (!existingTask) {
      return res.status(404).json({ error: 'Task not found' });
    }

    // Build update data
    const {
      title,
      description,
      status,
      priority,
      dueDate,
      tags,
      aiGenerated = true
    } = req.body;

    if (title !== undefined) updateData.title = title;
    if (description !== undefined) updateData.description = description;
    if (status !== undefined) {
      updateData.status = status;
      if (status === 'DONE' && existingTask.status !== 'DONE') {
        updateData.completedAt = new Date();
      } else if (status !== 'DONE' && existingTask.status === 'DONE') {
        updateData.completedAt = null;
      }
    }
    if (priority !== undefined) updateData.priority = priority;
    if (dueDate !== undefined) updateData.dueDate = dueDate ? new Date(dueDate) : null;
    if (tags !== undefined) updateData.tags = tags;

    // Update metadata to track AI modifications
    const currentMetadata = existingTask.metadata ? JSON.parse(existingTask.metadata) : {};
    const { agentId, agentName } = req.body;
    const agentIdentifier = agentId || agentName || 'ai-agent';
    
    updateData.metadata = JSON.stringify({
      ...currentMetadata,
      lastModifiedBy: agentIdentifier,
      lastModifiedAt: new Date().toISOString(),
      aiGenerated: aiGenerated,
      // Preserve claim info if task is claimed
      claimedBy: currentMetadata.claimedBy || null,
      claimedAt: currentMetadata.claimedAt || null
    });

    const task = await prisma.task.update({
      where: { id: taskId },
      data: updateData,
      include: {
        project: {
          select: { id: true, name: true, type: true }
        },
        user: {
          select: { id: true, username: true, name: true }
        }
      }
    });

    res.json({
      message: 'Task updated successfully by AI agent',
      task
    });
  } catch (error) {
    console.error('AI Agent update task error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get project overview for AI agents
router.get('/projects', authenticateAIAgent, [
  query('userId').optional().isUUID(),
  query('type').optional().isIn(['PERSONAL', 'WORK', 'GITHUB', 'LEARNING', 'HEALTH', 'FINANCE', 'OTHER']),
  query('status').optional().isIn(['ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED']),
  query('limit').optional().isInt({ min: 1, max: 100 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const {
      userId,
      type,
      status,
      limit = 50
    } = req.query;

    const where = {};
    if (userId) where.userId = userId;
    if (type) where.type = type;
    if (status) where.status = status;

    const projects = await prisma.project.findMany({
      where,
      include: {
        user: {
          select: { id: true, username: true, name: true }
        },
        tasks: {
          select: {
            id: true,
            status: true,
            priority: true,
            dueDate: true
          }
        },
        _count: {
          select: {
            tasks: true
          }
        }
      },
      orderBy: [
        { status: 'asc' },
        { createdAt: 'desc' }
      ],
      take: parseInt(limit)
    });

    // Add AI-friendly project insights
    const aiProjects = projects.map(project => {
      const completedTasks = project.tasks.filter(task => task.status === 'DONE').length;
      const overdueTasks = project.tasks.filter(task => 
        task.dueDate && task.dueDate < new Date() && task.status !== 'DONE'
      ).length;
      const highPriorityTasks = project.tasks.filter(task => 
        task.priority === 'HIGH' || task.priority === 'URGENT'
      ).length;

      return {
        ...project,
        aiInsights: {
          completionPercentage: project._count.tasks > 0 
            ? Math.round((completedTasks / project._count.tasks) * 100)
            : 0,
          overdueTasks,
          highPriorityTasks,
          totalTasks: project._count.tasks,
          healthScore: calculateProjectHealthScore(project),
          recommendedActions: generateProjectRecommendations(project, {
            completedTasks,
            overdueTasks,
            highPriorityTasks
          })
        }
      };
    });

    res.json({
      projects: aiProjects,
      total: projects.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('AI Agent get projects error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// AI Agent dashboard/analytics
router.get('/dashboard', authenticateAIAgent, [
  query('userId').optional().isUUID()
], async (req, res) => {
  try {
    const { userId } = req.query;
    const where = userId ? { userId } : {};

    const [
      totalTasks,
      completedTasks,
      overdueTasks,
      highPriorityTasks,
      recentTasks,
      projectStats
    ] = await Promise.all([
      prisma.task.count({ where }),
      prisma.task.count({ where: { ...where, status: 'DONE' } }),
      prisma.task.count({ 
        where: { 
          ...where, 
          dueDate: { lt: new Date() },
          status: { not: 'DONE' }
        }
      }),
      prisma.task.count({ 
        where: { 
          ...where, 
          priority: { in: ['HIGH', 'URGENT'] }
        }
      }),
      prisma.task.findMany({
        where,
        include: {
          project: { select: { name: true, type: true } },
          user: { select: { username: true } }
        },
        orderBy: { updatedAt: 'desc' },
        take: 10
      }),
      prisma.project.findMany({
        where,
        include: {
          _count: {
            select: { tasks: true }
          }
        }
      })
    ]);

    const dashboard = {
      overview: {
        totalTasks,
        completedTasks,
        completionRate: totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0,
        overdueTasks,
        highPriorityTasks,
        activeProjects: projectStats.filter(p => p.status === 'ACTIVE').length
      },
      recentActivity: recentTasks,
      recommendations: generateGlobalRecommendations({
        totalTasks,
        completedTasks,
        overdueTasks,
        highPriorityTasks,
        projectStats
      }),
      timestamp: new Date().toISOString()
    };

    res.json(dashboard);
  } catch (error) {
    console.error('AI Agent dashboard error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Helper functions
function calculateProjectHealthScore(project) {
  const totalTasks = project._count.tasks;
  if (totalTasks === 0) return 100;

  const completedTasks = project.tasks.filter(task => task.status === 'DONE').length;
  const overdueTasks = project.tasks.filter(task => 
    task.dueDate && task.dueDate < new Date() && task.status !== 'DONE'
  ).length;

  let score = (completedTasks / totalTasks) * 70; // 70% for completion
  score -= (overdueTasks / totalTasks) * 30; // -30% for overdue tasks
  score = Math.max(0, Math.min(100, score));

  return Math.round(score);
}

function generateProjectRecommendations(project, stats) {
  const recommendations = [];

  if (stats.overdueTasks > 0) {
    recommendations.push(`Address ${stats.overdueTasks} overdue task(s)`);
  }

  if (stats.highPriorityTasks > 0) {
    recommendations.push(`Focus on ${stats.highPriorityTasks} high-priority task(s)`);
  }

  if (stats.completedTasks === 0 && project._count.tasks > 0) {
    recommendations.push('Start working on tasks to build momentum');
  }

  if (project.status === 'ON_HOLD' && stats.highPriorityTasks > 0) {
    recommendations.push('Consider reactivating this project due to high-priority tasks');
  }

  return recommendations;
}

function generateGlobalRecommendations(stats) {
  const recommendations = [];

  if (stats.overdueTasks > 0) {
    recommendations.push({
      type: 'urgent',
      message: `${stats.overdueTasks} tasks are overdue and need immediate attention`
    });
  }

  if (stats.highPriorityTasks > 0) {
    recommendations.push({
      type: 'high',
      message: `${stats.highPriorityTasks} high-priority tasks require focus`
    });
  }

  if (stats.completionRate < 50 && stats.totalTasks > 10) {
    recommendations.push({
      type: 'medium',
      message: 'Consider breaking down large tasks into smaller, manageable subtasks'
    });
  }

  if (stats.activeProjects > 5) {
    recommendations.push({
      type: 'low',
      message: 'You have many active projects - consider consolidating or prioritizing'
    });
  }

  return recommendations;
}

// Whiteboard endpoints for AI agents
// Get all whiteboards for a user
router.get('/whiteboards', authenticateAIAgent, [
  query('userId').isUUID(),
  query('search').optional().isString(),
  query('tag').optional().isString(),
  query('limit').optional().isInt({ min: 1, max: 100 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { userId, search, tag, limit = 50 } = req.query;

    const where = { userId };

    if (search) {
      where.OR = [
        { title: { contains: search, mode: 'insensitive' } },
        { content: { contains: search, mode: 'insensitive' } },
        { transcription: { contains: search, mode: 'insensitive' } }
      ];
    }

    if (tag) {
      where.tags = { contains: tag };
    }

    const whiteboards = await prisma.whiteboard.findMany({
      where,
      orderBy: [
        { isPinned: 'desc' },
        { updatedAt: 'desc' }
      ],
      take: parseInt(limit)
    });

    // Add AI-friendly metadata
    const aiWhiteboards = whiteboards.map(wb => ({
      id: wb.id,
      title: wb.title,
      content: wb.content,
      transcription: wb.transcription,
      imageUrl: wb.imageUrl,
      tags: wb.tags ? wb.tags.split(',').map(t => t.trim()) : [],
      isPinned: wb.isPinned,
      createdAt: wb.createdAt,
      updatedAt: wb.updatedAt,
      // AI-friendly summary
      summary: {
        hasImage: !!wb.imageUrl,
        hasTranscription: !!wb.transcription,
        hasContent: !!wb.content,
        textContent: wb.transcription || wb.content || ''
      }
    }));

    res.json({
      whiteboards: aiWhiteboards,
      count: aiWhiteboards.length,
      searchQuery: search,
      tagFilter: tag
    });
  } catch (error) {
    console.error('Get whiteboards error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create whiteboard via AI agent
router.post('/whiteboards', authenticateAIAgent, [
  body('userId').isUUID(),
  body('title').trim().isLength({ min: 1 }),
  body('content').optional().isString(),
  body('transcription').optional().isString(),
  body('tags').optional().isString(),
  body('isPinned').optional().isBoolean()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { userId, title, content, transcription, tags, isPinned } = req.body;

    // Verify user exists
    const user = await prisma.user.findUnique({
      where: { id: userId }
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    const whiteboard = await prisma.whiteboard.create({
      data: {
        title,
        content: content || null,
        transcription: transcription || null,
        tags: tags || null,
        isPinned: isPinned || false,
        userId
      }
    });

    res.status(201).json({
      ...whiteboard,
      tags: whiteboard.tags ? whiteboard.tags.split(',').map(t => t.trim()) : []
    });
  } catch (error) {
    console.error('Create whiteboard error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update whiteboard transcription via AI agent
router.put('/whiteboards/:id/transcription', authenticateAIAgent, [
  body('transcription').isString(),
  body('userId').optional().isUUID()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { transcription, userId } = req.body;
    const { id } = req.params;

    const where = { id };
    if (userId) {
      where.userId = userId;
    }

    const whiteboard = await prisma.whiteboard.findFirst({ where });

    if (!whiteboard) {
      return res.status(404).json({ error: 'Whiteboard not found' });
    }

    const updated = await prisma.whiteboard.update({
      where: { id },
      data: { transcription }
    });

    res.json({
      ...updated,
      tags: updated.tags ? updated.tags.split(',').map(t => t.trim()) : []
    });
  } catch (error) {
    console.error('Update transcription error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
