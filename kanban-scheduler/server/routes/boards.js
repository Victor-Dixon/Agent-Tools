const express = require('express');
const { body, validationResult, query } = require('express-validator');
const prisma = require('../utils/database');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Get all boards for the authenticated user
router.get('/', authenticateToken, [
  query('page').optional().isInt({ min: 1 }).toInt(),
  query('limit').optional().isInt({ min: 1, max: 100 }).toInt()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 50;
    const skip = (page - 1) * limit;

    const [boards, total] = await Promise.all([
      prisma.board.findMany({
        where: { userId: req.user.id },
        include: {
          _count: {
            select: {
              tasks: true,
              lists: true
            }
          },
          tasks: {
            select: {
              id: true,
              status: true,
              priority: true
            }
          },
          lists: {
            select: {
              id: true,
              name: true,
              position: true,
              _count: {
                select: {
                  tasks: true
                }
              }
            },
            orderBy: { position: 'asc' }
          }
        },
        orderBy: [
          { isDefault: 'desc' },
          { createdAt: 'asc' }
        ],
        skip,
        take: parseInt(limit)
      }),
      prisma.board.count({ where: { userId: req.user.id } })
    ]);

    // Add task statistics to each board
    const boardsWithStats = boards.map(board => {
      const taskStats = board.tasks.reduce((acc, task) => {
        acc[task.status] = (acc[task.status] || 0) + 1;
        return acc;
      }, {});

      return {
        ...board,
        stats: {
          totalTasks: board._count.tasks,
          completedTasks: taskStats.DONE || 0,
          completionPercentage: board._count.tasks > 0 
            ? Math.round((taskStats.DONE || 0) / board._count.tasks * 100)
            : 0,
          taskStatusBreakdown: taskStats
        }
      };
    });

    res.json({
      boards: boardsWithStats,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Get boards error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get a single board with lists and tasks
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const boardId = req.params.id;
    
    // Basic validation for board ID
    if (!boardId || boardId.trim() === '') {
      return res.status(400).json({ error: 'Board ID is required' });
    }

    const board = await prisma.board.findFirst({
      where: {
        id: boardId,
        userId: req.user.id
      },
      include: {
        lists: {
          include: {
            tasks: {
              include: {
                project: {
                  select: { id: true, name: true, color: true, type: true }
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
                  orderBy: { createdAt: 'desc' },
                  take: 3
                },
                subtasks: {
                  select: { id: true, title: true, completed: true },
                  orderBy: { position: 'asc' }
                },
                _count: {
                  select: {
                    comments: true,
                    subtasks: true
                  }
                }
              },
              orderBy: { position: 'asc' }
            },
            _count: {
              select: {
                tasks: true
              }
            }
          },
          orderBy: { position: 'asc' }
        },
        tasks: {
          where: { listId: null }, // Tasks not in any list
          include: {
            project: {
              select: { id: true, name: true, color: true, type: true }
            }
          },
          orderBy: { position: 'asc' }
        }
      }
    });

    if (!board) {
      return res.status(404).json({ error: 'Board not found' });
    }

    res.json({ board });
  } catch (error) {
    console.error('Get board error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create a new board
router.post('/', authenticateToken, [
  body('name').trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim(),
  body('color').optional().isHexColor(),
  body('isDefault').optional().isBoolean()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { name, description, color = '#3B82F6', isDefault = false } = req.body;

    // If setting as default, unset other default boards
    if (isDefault) {
      await prisma.board.updateMany({
        where: { userId: req.user.id, isDefault: true },
        data: { isDefault: false }
      });
    }

    const board = await prisma.board.create({
      data: {
        name,
        description,
        color,
        isDefault,
        userId: req.user.id
      }
    });

    // Create default lists for the new board
    const defaultLists = [
      { name: 'To Do', color: '#6B7280', position: 1 },
      { name: 'In Progress', color: '#F59E0B', position: 2 },
      { name: 'Done', color: '#10B981', position: 3 }
    ];

    await Promise.all(
      defaultLists.map(list =>
        prisma.list.create({
          data: {
            ...list,
            boardId: board.id
          }
        })
      )
    );

    res.status(201).json({
      message: 'Board created successfully',
      board
    });
  } catch (error) {
    console.error('Create board error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update a board
router.put('/:id', authenticateToken, [
  body('name').optional().trim().isLength({ min: 1, max: 255 }),
  body('description').optional().trim(),
  body('color').optional().isHexColor(),
  body('isDefault').optional().isBoolean()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const boardId = req.params.id;
    const updateData = {};

    // Check if board exists and belongs to user
    const existingBoard = await prisma.board.findFirst({
      where: { id: boardId, userId: req.user.id }
    });

    if (!existingBoard) {
      return res.status(404).json({ error: 'Board not found' });
    }

    // Build update data
    const { name, description, color, isDefault } = req.body;

    if (name !== undefined) updateData.name = name;
    if (description !== undefined) updateData.description = description;
    if (color !== undefined) updateData.color = color;
    if (isDefault !== undefined) {
      updateData.isDefault = isDefault;
      
      // If setting as default, unset other default boards
      if (isDefault) {
        await prisma.board.updateMany({
          where: { userId: req.user.id, isDefault: true, id: { not: boardId } },
          data: { isDefault: false }
        });
      }
    }

    const board = await prisma.board.update({
      where: { id: boardId },
      data: updateData
    });

    res.json({
      message: 'Board updated successfully',
      board
    });
  } catch (error) {
    console.error('Update board error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete a board
router.delete('/:id', authenticateToken, async (req, res) => {
  try {
    const boardId = req.params.id;

    const board = await prisma.board.findFirst({
      where: { id: boardId, userId: req.user.id }
    });

    if (!board) {
      return res.status(404).json({ error: 'Board not found' });
    }

    // Don't allow deletion of the last board
    const boardCount = await prisma.board.count({
      where: { userId: req.user.id }
    });

    if (boardCount <= 1) {
      return res.status(400).json({ error: 'Cannot delete the last board' });
    }

    await prisma.board.delete({
      where: { id: boardId }
    });

    res.json({ message: 'Board deleted successfully' });
  } catch (error) {
    console.error('Delete board error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Board list management
// Create a new list in a board
router.post('/:boardId/lists', authenticateToken, [
  body('name').trim().isLength({ min: 1, max: 255 }),
  body('color').optional().isHexColor(),
  body('position').optional().isInt()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { boardId } = req.params;
    const { name, color = '#6B7280', position } = req.body;

    // Verify board belongs to user
    const board = await prisma.board.findFirst({
      where: { id: boardId, userId: req.user.id }
    });

    if (!board) {
      return res.status(404).json({ error: 'Board not found' });
    }

    // Get the next position if not provided
    let listPosition = position;
    if (listPosition === undefined) {
      const lastList = await prisma.list.findFirst({
        where: { boardId },
        orderBy: { position: 'desc' }
      });
      listPosition = (lastList?.position || 0) + 1;
    }

    const list = await prisma.list.create({
      data: {
        name,
        color,
        position: listPosition,
        boardId
      }
    });

    res.status(201).json({
      message: 'List created successfully',
      list
    });
  } catch (error) {
    console.error('Create list error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update a list
router.put('/lists/:listId', authenticateToken, [
  body('name').optional().trim().isLength({ min: 1, max: 255 }),
  body('color').optional().isHexColor(),
  body('position').optional().isInt()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { listId } = req.params;
    const updateData = {};

    // Check if list exists and belongs to user's board
    const list = await prisma.list.findFirst({
      where: {
        id: listId,
        board: { userId: req.user.id }
      }
    });

    if (!list) {
      return res.status(404).json({ error: 'List not found' });
    }

    // Build update data
    const { name, color, position } = req.body;

    if (name !== undefined) updateData.name = name;
    if (color !== undefined) updateData.color = color;
    if (position !== undefined) updateData.position = position;

    const updatedList = await prisma.list.update({
      where: { id: listId },
      data: updateData
    });

    res.json({
      message: 'List updated successfully',
      list: updatedList
    });
  } catch (error) {
    console.error('Update list error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete a list
router.delete('/lists/:listId', authenticateToken, async (req, res) => {
  try {
    const { listId } = req.params;

    // Check if list exists and belongs to user's board
    const list = await prisma.list.findFirst({
      where: {
        id: listId,
        board: { userId: req.user.id }
      }
    });

    if (!list) {
      return res.status(404).json({ error: 'List not found' });
    }

    // Move tasks to board root or delete them
    const { moveTasksToBoard = true } = req.query;

    if (moveTasksToBoard === 'true') {
      await prisma.task.updateMany({
        where: { listId },
        data: { listId: null }
      });
    }

    await prisma.list.delete({
      where: { id: listId }
    });

    res.json({ message: 'List deleted successfully' });
  } catch (error) {
    console.error('Delete list error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Reorder lists in a board
router.put('/:boardId/lists/reorder', authenticateToken, [
  body('lists').isArray(),
  body('lists.*.id').isUUID(),
  body('lists.*.position').isInt()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { boardId } = req.params;
    const { lists } = req.body;

    // Verify board belongs to user
    const board = await prisma.board.findFirst({
      where: { id: boardId, userId: req.user.id }
    });

    if (!board) {
      return res.status(404).json({ error: 'Board not found' });
    }

    // Verify all lists belong to this board
    const listIds = lists.map(l => l.id);
    const boardLists = await prisma.list.findMany({
      where: {
        id: { in: listIds },
        boardId
      },
      select: { id: true }
    });

    if (boardLists.length !== listIds.length) {
      return res.status(400).json({ error: 'Some lists not found in this board' });
    }

    // Update positions
    await Promise.all(
      lists.map(list =>
        prisma.list.update({
          where: { id: list.id },
          data: { position: list.position }
        })
      )
    );

    res.json({ message: 'Lists reordered successfully' });
  } catch (error) {
    console.error('Reorder lists error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
