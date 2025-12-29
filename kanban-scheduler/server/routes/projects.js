const express = require('express');
const { body, validationResult, query } = require('express-validator');
const prisma = require('../utils/database');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Get all projects for the authenticated user
router.get('/', authenticateToken, [
  query('type').optional().isIn(['PERSONAL', 'WORK', 'GITHUB', 'LEARNING', 'HEALTH', 'FINANCE', 'OTHER']),
  query('status').optional().isIn(['ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED']),
  query('phase').optional().isIn(['0A', '0B', '1', '2', '3', '4', '5']),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const {
      type,
      status,
      phase,
      page = 1,
      limit = 50,
      search
    } = req.query;

    const skip = (parseInt(page) - 1) * parseInt(limit);

    const where = {
      userId: req.user.id
    };

    if (type) where.type = type;
    if (status) where.status = status;
    if (phase) where.phase = phase;
    if (search) {
      where.OR = [
        { name: { contains: search, mode: 'insensitive' } },
        { description: { contains: search, mode: 'insensitive' } }
      ];
    }

    const [projects, total] = await Promise.all([
      prisma.project.findMany({
        where,
        include: {
          _count: {
            select: {
              tasks: true
            }
          },
          tasks: {
            where: { status: 'DONE' },
            select: { id: true }
          }
        },
        orderBy: [
          { phase: 'asc' },
          { status: 'asc' },
          { createdAt: 'desc' }
        ],
        skip,
        take: parseInt(limit)
      }),
      prisma.project.count({ where })
    ]);

    // Add completion percentage to each project
    const projectsWithStats = projects.map(project => ({
      ...project,
      completionPercentage: project._count.tasks > 0 
        ? Math.round((project.tasks.length / project._count.tasks) * 100)
        : 0
    }));

    res.json({
      projects: projectsWithStats,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / parseInt(limit))
      }
    });
  } catch (error) {
    console.error('Get projects error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get a single project
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const project = await prisma.project.findFirst({
      where: {
        id: req.params.id,
        userId: req.user.id
      },
      include: {
        tasks: {
          include: {
            comments: {
              select: {
                id: true,
                content: true,
                createdAt: true,
                user: {
                  select: { id: true, username: true, name: true }
                }
              },
              orderBy: { createdAt: 'desc' },
              take: 5
            }
          },
          orderBy: [
            { status: 'asc' },
            { position: 'asc' }
          ]
        },
        _count: {
          select: {
            tasks: true
          }
        }
      }
    });

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Calculate project statistics
    const taskStats = project.tasks.reduce((acc, task) => {
      acc[task.status] = (acc[task.status] || 0) + 1;
      return acc;
    }, {});

    const completionPercentage = project._count.tasks > 0 
      ? Math.round((taskStats.DONE || 0) / project._count.tasks * 100)
      : 0;

    res.json({
      project: {
        ...project,
        stats: {
          totalTasks: project._count.tasks,
          completedTasks: taskStats.DONE || 0,
          completionPercentage,
          taskStatusBreakdown: taskStats
        }
      }
    });
  } catch (error) {
    console.error('Get project error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create a new project
router.post('/', authenticateToken, [
  body('name').trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim(),
  body('type').isIn(['PERSONAL', 'WORK', 'GITHUB', 'LEARNING', 'HEALTH', 'FINANCE', 'OTHER']),
  body('status').optional().isIn(['ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED']),
  body('phase').optional().isIn(['0A', '0B', '1', '2', '3', '4', '5']),
  body('githubUrl').optional().isURL(),
  body('color').optional().isHexColor(),
  body('startDate').optional().isISO8601(),
  body('endDate').optional().isISO8601()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const {
      name,
      description,
      type,
      status = 'ACTIVE',
      phase = '0A',
      githubUrl,
      color = '#10B981',
      startDate,
      endDate
    } = req.body;

    const project = await prisma.project.create({
      data: {
        name,
        description,
        type,
        status,
        phase,
        githubUrl,
        color,
        startDate: startDate ? new Date(startDate) : null,
        endDate: endDate ? new Date(endDate) : null,
        userId: req.user.id
      }
    });

    res.status(201).json({
      message: 'Project created successfully',
      project
    });
  } catch (error) {
    console.error('Create project error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update a project
router.put('/:id', authenticateToken, [
  body('name').optional().trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim(),
  body('type').optional().isIn(['PERSONAL', 'WORK', 'GITHUB', 'LEARNING', 'HEALTH', 'FINANCE', 'OTHER']),
  body('status').optional().isIn(['ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED']),
  body('phase').optional().isIn(['0A', '0B', '1', '2', '3', '4', '5']),
  body('githubUrl').optional().isURL(),
  body('color').optional().isHexColor(),
  body('startDate').optional().isISO8601(),
  body('endDate').optional().isISO8601()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const projectId = req.params.id;
    const updateData = {};

    // Check if project exists and belongs to user
    const existingProject = await prisma.project.findFirst({
      where: { id: projectId, userId: req.user.id }
    });

    if (!existingProject) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Build update data
    const {
      name,
      description,
      type,
      status,
      phase,
      githubUrl,
      color,
      startDate,
      endDate
    } = req.body;

    if (name !== undefined) updateData.name = name;
    if (description !== undefined) updateData.description = description;
    if (type !== undefined) updateData.type = type;
    if (status !== undefined) updateData.status = status;
    if (phase !== undefined) updateData.phase = phase;
    if (githubUrl !== undefined) updateData.githubUrl = githubUrl;
    if (color !== undefined) updateData.color = color;
    if (startDate !== undefined) updateData.startDate = startDate ? new Date(startDate) : null;
    if (endDate !== undefined) updateData.endDate = endDate ? new Date(endDate) : null;

    const project = await prisma.project.update({
      where: { id: projectId },
      data: updateData
    });

    res.json({
      message: 'Project updated successfully',
      project
    });
  } catch (error) {
    console.error('Update project error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete a project
router.delete('/:id', authenticateToken, async (req, res) => {
  try {
    const projectId = req.params.id;

    const project = await prisma.project.findFirst({
      where: { id: projectId, userId: req.user.id }
    });

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Optionally move tasks to a default project or delete them
    const { moveTasksToDefault = false } = req.query;

    if (moveTasksToDefault === 'true') {
      // Move tasks to user's default project or create one
      let defaultProject = await prisma.project.findFirst({
        where: { userId: req.user.id, type: 'PERSONAL' },
        orderBy: { createdAt: 'asc' }
      });

      if (!defaultProject) {
        defaultProject = await prisma.project.create({
          data: {
            name: 'Default Project',
            type: 'PERSONAL',
            userId: req.user.id
          }
        });
      }

      await prisma.task.updateMany({
        where: { projectId },
        data: { projectId: defaultProject.id }
      });
    }

    await prisma.project.delete({
      where: { id: projectId }
    });

    res.json({ message: 'Project deleted successfully' });
  } catch (error) {
    console.error('Delete project error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get project statistics
router.get('/:id/stats', authenticateToken, async (req, res) => {
  try {
    const projectId = req.params.id;

    const project = await prisma.project.findFirst({
      where: { id: projectId, userId: req.user.id },
      include: {
        tasks: {
          select: {
            id: true,
            status: true,
            priority: true,
            dueDate: true,
            completedAt: true,
            createdAt: true
          }
        }
      }
    });

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Calculate statistics
    const totalTasks = project.tasks.length;
    const completedTasks = project.tasks.filter(task => task.status === 'DONE').length;
    const overdueTasks = project.tasks.filter(task => 
      task.dueDate && task.dueDate < new Date() && task.status !== 'DONE'
    ).length;

    const priorityBreakdown = project.tasks.reduce((acc, task) => {
      acc[task.priority] = (acc[task.priority] || 0) + 1;
      return acc;
    }, {});

    const statusBreakdown = project.tasks.reduce((acc, task) => {
      acc[task.status] = (acc[task.status] || 0) + 1;
      return acc;
    }, {});

    // Calculate average completion time for completed tasks
    const completedTasksWithTime = project.tasks.filter(task => task.completedAt);
    const avgCompletionTime = completedTasksWithTime.length > 0 
      ? completedTasksWithTime.reduce((acc, task) => {
          const completionTime = task.completedAt - task.createdAt;
          return acc + completionTime;
        }, 0) / completedTasksWithTime.length
      : 0;

    res.json({
      stats: {
        totalTasks,
        completedTasks,
        completionPercentage: totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0,
        overdueTasks,
        priorityBreakdown,
        statusBreakdown,
        avgCompletionTimeMs: Math.round(avgCompletionTime),
        avgCompletionTimeDays: Math.round(avgCompletionTime / (1000 * 60 * 60 * 24))
      }
    });
  } catch (error) {
    console.error('Get project stats error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
