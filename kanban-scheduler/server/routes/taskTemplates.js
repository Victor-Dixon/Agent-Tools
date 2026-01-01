const express = require('express');
const { body, validationResult } = require('express-validator');
const prisma = require('../utils/database');
const { authenticateToken, authenticateAIAgent } = require('../middleware/auth');

const router = express.Router();

// Definition of Done categories
const DOD_CATEGORIES = [
  'Code Quality',
  'Documentation',
  'Testing',
  'Security',
  'Performance',
  'User Experience',
  'Deployment',
  'Version Control'
];

// Phase definitions
const PHASES = {
  '0A': 'Organization and Planning',
  '0B': 'Research',
  '1': 'Design',
  '2': 'Development',
  '3': 'Testing',
  '4': 'Deployment',
  '5': 'Maintenance'
};

// Create tasks from a master task list template (for agents)
router.post('/create-from-template', authenticateAIAgent, [
  body('userId').isUUID(),
  body('projectId').optional().isUUID(),
  body('boardId').optional().isUUID(),
  body('template').isObject(),
  body('template.name').trim().isLength({ min: 1 }),
  body('template.categories').isArray(),
  body('template.categories.*.name').trim().isLength({ min: 1 }),
  body('template.categories.*.tasks').isArray(),
  body('template.categories.*.tasks.*.title').trim().isLength({ min: 1 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { userId, projectId, boardId, template } = req.body;

    // Verify user exists
    const user = await prisma.user.findUnique({
      where: { id: userId }
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Verify project if provided
    if (projectId) {
      const project = await prisma.project.findFirst({
        where: { id: projectId, userId }
      });
      if (!project) {
        return res.status(404).json({ error: 'Project not found' });
      }
    }

    // Verify board if provided
    if (boardId) {
      const board = await prisma.board.findFirst({
        where: { id: boardId, userId }
      });
      if (!board) {
        return res.status(404).json({ error: 'Board not found' });
      }
    }

    // Get current max position
    const lastTask = await prisma.task.findFirst({
      where: { userId, projectId: projectId || null, boardId: boardId || null },
      orderBy: { position: 'desc' }
    });
    let currentPosition = (lastTask?.position || 0) + 1;

    // Create tasks from template
    const createdTasks = [];
    const taskErrors = [];

    for (const category of template.categories || []) {
      const categoryName = category.name;
      const phase = category.phase || template.defaultPhase || '0A';

      for (const taskTemplate of category.tasks || []) {
        try {
          const task = await prisma.task.create({
            data: {
              title: taskTemplate.title,
              description: taskTemplate.description || `${categoryName}: ${taskTemplate.title}`,
              status: 'TODO',
              priority: taskTemplate.priority || 'MEDIUM',
              category: categoryName,
              phase: phase,
              tags: taskTemplate.tags ? JSON.stringify(taskTemplate.tags) : null,
              position: currentPosition++,
              userId,
              projectId: projectId || null,
              boardId: boardId || null,
              metadata: JSON.stringify({
                aiGenerated: true,
                templateName: template.name,
                category: categoryName,
                phase: phase,
                createdAt: new Date().toISOString()
              })
            }
          });
          createdTasks.push(task);
        } catch (error) {
          taskErrors.push({
            category: categoryName,
            task: taskTemplate.title,
            error: error.message
          });
        }
      }
    }

    res.status(201).json({
      message: `Created ${createdTasks.length} tasks from template "${template.name}"`,
      created: createdTasks.length,
      errors: taskErrors.length > 0 ? taskErrors : undefined,
      tasks: createdTasks
    });
  } catch (error) {
    console.error('Create tasks from template error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create Definition of Done checklist for a project
router.post('/definition-of-done', authenticateAIAgent, [
  body('userId').isUUID(),
  body('projectId').isUUID(),
  body('categories').optional().isArray()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { userId, projectId, categories = DOD_CATEGORIES } = req.body;

    // Verify project exists
    const project = await prisma.project.findFirst({
      where: { id: projectId, userId }
    });

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Get current max position
    const lastTask = await prisma.task.findFirst({
      where: { userId, projectId },
      orderBy: { position: 'desc' }
    });
    let currentPosition = (lastTask?.position || 0) + 1;

    // Default tasks for each category
    const defaultTasks = {
      'Code Quality': [
        'Code review completed',
        'Remove console.log statements',
        'Add code comments for complex logic',
        'Consistent code formatting',
        'Refactor duplicated code',
        'Error handling for edge cases'
      ],
      'Documentation': [
        'README.md complete with installation instructions',
        'README.md includes usage guide',
        'README.md includes feature list',
        'Code comments for complex logic',
        'API documentation (if applicable)'
      ],
      'Testing': [
        'Unit tests written',
        'Integration tests completed',
        'Manual testing completed',
        'Test edge cases',
        'Cross-platform testing (if applicable)'
      ],
      'Security': [
        'Input validation on all user inputs',
        'Security vulnerabilities fixed',
        'No sensitive data exposed',
        'Proper error handling (no sensitive info)',
        'Security headers configured'
      ],
      'Performance': [
        'Performance optimization completed',
        'Load testing (if applicable)',
        'Memory leaks fixed',
        'Bundle size optimized'
      ],
      'User Experience': [
        'Polished UI/animations',
        'Helpful error messages',
        'Loading states implemented',
        'Accessibility improvements',
        'Mobile-responsive design'
      ],
      'Deployment': [
        'Build process works',
        'Deployment documentation',
        'Environment variables documented',
        'Hosting setup complete'
      ],
      'Version Control': [
        'Proper git history',
        '.gitignore configured',
        'No sensitive files committed',
        'Release tags created'
      ]
    };

    const createdTasks = [];

    for (const category of categories) {
      const tasks = defaultTasks[category] || [];
      
      for (const taskTitle of tasks) {
        const task = await prisma.task.create({
          data: {
            title: taskTitle,
            description: `Definition of Done: ${category}`,
            status: 'TODO',
            priority: 'HIGH',
            category: category,
            phase: project.phase || '0A',
            position: currentPosition++,
            userId,
            projectId,
            metadata: JSON.stringify({
              aiGenerated: true,
              definitionOfDone: true,
              category: category,
              createdAt: new Date().toISOString()
            })
          }
        });
        createdTasks.push(task);
      }
    }

    res.status(201).json({
      message: `Created Definition of Done checklist with ${createdTasks.length} tasks`,
      created: createdTasks.length,
      tasks: createdTasks
    });
  } catch (error) {
    console.error('Create Definition of Done error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get task templates (predefined structures)
router.get('/templates', authenticateAIAgent, (req, res) => {
  const templates = {
    definitionOfDone: {
      name: 'Definition of Done',
      description: 'Standard Definition of Done checklist for any project',
      categories: DOD_CATEGORIES
    },
    phases: PHASES,
    categories: DOD_CATEGORIES
  };

  res.json(templates);
});

module.exports = router;


