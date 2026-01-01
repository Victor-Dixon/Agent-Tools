const express = require('express');
const { body, validationResult, query } = require('express-validator');
const prisma = require('../utils/database');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Get all tasks for the authenticated user
router.get('/', authenticateToken, [
  query('status').optional().isIn(['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'BLOCKED', 'CANCELLED']),
  query('priority').optional().isIn(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
  query('projectId').optional().isUUID(),
  query('boardId').optional().isUUID(),
  query('listId').optional().isUUID(),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const {
      status,
      priority,
      projectId,
      boardId,
      listId,
      page = 1,
      limit = 50,
      search
    } = req.query;

    const skip = (parseInt(page) - 1) * parseInt(limit);

    const where = {
      userId: req.user.id
    };

    if (status) where.status = status;
    if (priority) where.priority = priority;
    if (projectId) where.projectId = projectId;
    if (boardId) where.boardId = boardId;
    if (listId) where.listId = listId;
    if (search) {
      where.OR = [
        { title: { contains: search, mode: 'insensitive' } },
        { description: { contains: search, mode: 'insensitive' } }
      ];
    }

    const [tasks, total] = await Promise.all([
      prisma.task.findMany({
        where,
        include: {
          project: {
            select: { id: true, name: true, color: true, type: true }
          },
          board: {
            select: { id: true, name: true, color: true }
          },
          list: {
            select: { id: true, name: true, color: true }
          },
          comments: {
            select: {
              id: true,
              content: true,
              createdAt: true,
              user: {
                select: { id: true, username: true, name: true }
              }
            },
            orderBy: { createdAt: 'desc' }
          },
          subtasks: {
            orderBy: { position: 'asc' }
          },
          _count: {
            select: {
              comments: true,
              subtasks: true
            }
          }
        },
        orderBy: [
          { position: 'asc' },
          { createdAt: 'desc' }
        ],
        skip,
        take: parseInt(limit)
      }),
      prisma.task.count({ where })
    ]);

    res.json({
      tasks,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / parseInt(limit))
      }
    });
  } catch (error) {
    console.error('Get tasks error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get a single task
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const task = await prisma.task.findFirst({
      where: {
        id: req.params.id,
        userId: req.user.id
      },
      include: {
        project: true,
        board: true,
        list: true,
        comments: {
          include: {
            user: {
              select: { id: true, username: true, name: true, avatar: true }
            }
          },
          orderBy: { createdAt: 'asc' }
        },
        subtasks: {
          orderBy: { position: 'asc' }
        }
      }
    });

    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    res.json({ task });
  } catch (error) {
    console.error('Get task error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create a new task
router.post('/', authenticateToken, [
  body('title').trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim(),
  body('status').optional().isIn(['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'BLOCKED', 'CANCELLED']),
  body('priority').optional().isIn(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
  body('dueDate').optional().isISO8601(),
  body('projectId').optional().isUUID(),
  body('boardId').optional().isUUID(),
  body('listId').optional().isUUID(),
  body('tags').optional().isArray()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const {
      title,
      description,
      status = 'TODO',
      priority = 'MEDIUM',
      dueDate,
      projectId,
      boardId,
      listId,
      tags = []
    } = req.body;

    // Validate project ownership if projectId is provided
    if (projectId) {
      const project = await prisma.project.findFirst({
        where: { id: projectId, userId: req.user.id }
      });
      if (!project) {
        return res.status(404).json({ error: 'Project not found' });
      }
    }

    // Validate board ownership if boardId is provided
    if (boardId) {
      const board = await prisma.board.findFirst({
        where: { id: boardId, userId: req.user.id }
      });
      if (!board) {
        return res.status(404).json({ error: 'Board not found' });
      }
    }

    // Get the next position
    const lastTask = await prisma.task.findFirst({
      where: { userId: req.user.id, listId: listId || null },
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
        boardId,
        listId,
        tags,
        position,
        userId: req.user.id
      },
      include: {
        project: {
          select: { id: true, name: true, color: true, type: true }
        },
        board: {
          select: { id: true, name: true, color: true }
        },
        list: {
          select: { id: true, name: true, color: true }
        }
      }
    });

    res.status(201).json({
      message: 'Task created successfully',
      task
    });
  } catch (error) {
    console.error('Create task error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update a task
router.put('/:id', authenticateToken, [
  body('title').optional().trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim(),
  body('status').optional().isIn(['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'BLOCKED', 'CANCELLED']),
  body('priority').optional().isIn(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
  body('dueDate').optional().isISO8601(),
  body('projectId').optional().isUUID(),
  body('boardId').optional().isUUID(),
  body('listId').optional().isUUID(),
  body('tags').optional().isArray(),
  body('position').optional().isInt()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const taskId = req.params.id;
    const updateData = {};

    // Check if task exists and belongs to user
    const existingTask = await prisma.task.findFirst({
      where: { id: taskId, userId: req.user.id }
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
      projectId,
      boardId,
      listId,
      tags,
      position
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
    if (projectId !== undefined) updateData.projectId = projectId;
    if (boardId !== undefined) updateData.boardId = boardId;
    if (listId !== undefined) updateData.listId = listId;
    if (tags !== undefined) updateData.tags = tags;
    if (position !== undefined) updateData.position = position;

    const task = await prisma.task.update({
      where: { id: taskId },
      data: updateData,
      include: {
        project: {
          select: { id: true, name: true, color: true, type: true }
        },
        board: {
          select: { id: true, name: true, color: true }
        },
        list: {
          select: { id: true, name: true, color: true }
        },
        subtasks: {
          orderBy: { position: 'asc' }
        }
      }
    });

    res.json({
      message: 'Task updated successfully',
      task
    });
  } catch (error) {
    console.error('Update task error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete a task
router.delete('/:id', authenticateToken, async (req, res) => {
  try {
    const taskId = req.params.id;

    const task = await prisma.task.findFirst({
      where: { id: taskId, userId: req.user.id }
    });

    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    await prisma.task.delete({
      where: { id: taskId }
    });

    res.json({ message: 'Task deleted successfully' });
  } catch (error) {
    console.error('Delete task error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Reorder tasks
router.put('/reorder', authenticateToken, [
  body('tasks').isArray(),
  body('tasks.*.id').isUUID(),
  body('tasks.*.position').isInt()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { tasks } = req.body;

    // Verify all tasks belong to the user
    const taskIds = tasks.map(t => t.id);
    const userTasks = await prisma.task.findMany({
      where: {
        id: { in: taskIds },
        userId: req.user.id
      },
      select: { id: true }
    });

    if (userTasks.length !== taskIds.length) {
      return res.status(400).json({ error: 'Some tasks not found or not owned by user' });
    }

    // Update positions
    await Promise.all(
      tasks.map(task =>
        prisma.task.update({
          where: { id: task.id },
          data: { position: task.position }
        })
      )
    );

    res.json({ message: 'Tasks reordered successfully' });
  } catch (error) {
    console.error('Reorder tasks error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
