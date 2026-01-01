const express = require('express');
const fs = require('fs');
const path = require('path');
const { body, validationResult } = require('express-validator');
const prisma = require('../utils/database');
const { authenticateToken, authenticateAIAgent } = require('../middleware/auth');
const { parseMasterTaskList, flattenToTemplate } = require('../utils/taskListParser');
const { validateFilePath, validateFilePaths } = require('../utils/pathValidator');

const router = express.Router();

// Custom validator for file paths
const validateFilePathInput = (req, res, next) => {
  const { filePath } = req.body;
  if (!filePath) {
    return next(); // Let express-validator handle required validation
  }
  
  const validation = validateFilePath(filePath);
  if (!validation.valid) {
    return res.status(403).json({
      error: 'Invalid file path',
      details: validation.error
    });
  }
  
  // Store validated path for use in route handler
  req.validatedFilePath = validation.resolvedPath;
  next();
};

// Import master task list from file path
router.post('/import-from-file', authenticateAIAgent, [
  body('userId').isUUID(),
  body('projectId').optional().isUUID(),
  body('boardId').optional().isUUID(),
  body('filePath').isString()
], validateFilePathInput, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { userId, projectId, boardId } = req.body;
    const validatedPath = req.validatedFilePath; // From validateFilePathInput middleware

    // Verify user exists
    const user = await prisma.user.findUnique({
      where: { id: userId }
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Read and parse the file (path already validated by middleware)
    let markdown;
    try {
      markdown = fs.readFileSync(validatedPath, 'utf8');
    } catch (error) {
      return res.status(404).json({ error: `File not found: ${validatedPath}` });
    }

    // Parse the markdown
    const parsed = parseMasterTaskList(markdown);
    const template = flattenToTemplate(parsed);

    // Use the existing template creation endpoint logic
    const createdTasks = [];
    let currentPosition = 1;

    // Get current max position
    const lastTask = await prisma.task.findFirst({
      where: { userId, projectId: projectId || null, boardId: boardId || null },
      orderBy: { position: 'desc' }
    });
    if (lastTask) {
      currentPosition = lastTask.position + 1;
    }

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
                    importedFrom: validatedPath,
                createdAt: new Date().toISOString()
              })
            }
          });
          createdTasks.push(task);
        } catch (error) {
          console.error(`Error creating task "${taskTemplate.title}":`, error);
        }
      }
    }

    res.status(201).json({
      message: `Imported ${createdTasks.length} tasks from "${template.name}"`,
      created: createdTasks.length,
      template: template.name,
      sourceFile: validatedPath,
      tasks: createdTasks
    });
  } catch (error) {
    console.error('Import from file error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Scan for master task lists and return list
router.get('/scan', authenticateAIAgent, async (req, res) => {
  try {
    const searchPaths = req.query.searchPaths 
      ? JSON.parse(req.query.searchPaths)
      : [
          process.env.HOME + '/Development',
          process.env.HOME + '/Projects'
        ];

    const foundFiles = [];

    function scanDirectory(dir, depth = 0) {
      if (depth > 5) return; // Limit depth to avoid infinite loops

      try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        
        for (const entry of entries) {
          const fullPath = path.join(dir, entry.name);
          
          // Skip hidden directories and common exclusions
          if (entry.name.startsWith('.') || 
              entry.name === 'node_modules' || 
              entry.name === '__pycache__') {
            continue;
          }

          if (entry.isDirectory()) {
            scanDirectory(fullPath, depth + 1);
          } else if (entry.isFile()) {
            const name = entry.name.toLowerCase();
            if ((name.includes('master') && name.includes('task')) ||
                (name.includes('task') && name.includes('list')) ||
                name === 'master_task_list.md' ||
                name === 'master-task-list.md') {
              
              // Try to read and parse to verify it's a valid task list
              try {
                const content = fs.readFileSync(fullPath, 'utf8');
                if (content.includes('- [ ]') || content.includes('- [x]') || 
                    content.includes('Definition of Done') ||
                    content.includes('MASTER TASK LIST')) {
                  foundFiles.push({
                    path: fullPath,
                    name: entry.name,
                    size: fs.statSync(fullPath).size,
                    modified: fs.statSync(fullPath).mtime
                  });
                }
              } catch (e) {
                // Skip files that can't be read
              }
            }
          }
        }
      } catch (error) {
        // Skip directories that can't be accessed
      }
    }

    for (const searchPath of searchPaths) {
      if (fs.existsSync(searchPath)) {
        scanDirectory(searchPath);
      }
    }

    res.json({
      found: foundFiles.length,
      files: foundFiles
    });
  } catch (error) {
    console.error('Scan error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Custom validator for file paths array
const validateFilePathsInput = (req, res, next) => {
  const { filePaths } = req.body;
  if (!filePaths || !Array.isArray(filePaths)) {
    return next(); // Let express-validator handle validation
  }
  
  const validation = validateFilePaths(filePaths);
  if (!validation.valid) {
    return res.status(403).json({
      error: 'One or more file paths are invalid',
      details: validation.errors
    });
  }
  
  // Store validated paths for use in route handler
  req.validatedFilePaths = validation.results.map(r => r.resolvedPath);
  next();
};

// Import all found master task lists
router.post('/import-all', authenticateAIAgent, [
  body('userId').isUUID(),
  body('projectId').optional().isUUID(),
  body('boardId').optional().isUUID(),
  body('filePaths').isArray()
], validateFilePathsInput, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { userId, projectId, boardId } = req.body;
    const validatedPaths = req.validatedFilePaths; // From validateFilePathsInput middleware

    const results = [];

    for (const validatedPath of validatedPaths) {

      try {
        // Read and parse the file (path already validated by middleware)
        const markdown = fs.readFileSync(validatedPath, 'utf8');
        const parsed = parseMasterTaskList(markdown);
        const template = flattenToTemplate(parsed);

        // Create tasks
        let currentPosition = 1;
        const lastTask = await prisma.task.findFirst({
          where: { userId, projectId: projectId || null, boardId: boardId || null },
          orderBy: { position: 'desc' }
        });
        if (lastTask) {
          currentPosition = lastTask.position + 1;
        }

        const createdTasks = [];
        for (const category of template.categories || []) {
          const categoryName = category.name;
          const phase = category.phase || '0A';

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
                  position: currentPosition++,
                  userId,
                  projectId: projectId || null,
                  boardId: boardId || null,
                  metadata: JSON.stringify({
                    aiGenerated: true,
                    templateName: template.name,
                    category: categoryName,
                    phase: phase,
                    importedFrom: validatedPath,
                    createdAt: new Date().toISOString()
                  })
                }
              });
              createdTasks.push(task);
            } catch (error) {
              console.error(`Error creating task:`, error);
            }
          }
        }

        results.push({
          file: validatedPath,
          template: template.name,
          created: createdTasks.length,
          success: true
        });
      } catch (error) {
        results.push({
          file: validatedPath,
          success: false,
          error: error.message
        });
      }
    }

    const totalCreated = results.reduce((sum, r) => sum + (r.created || 0), 0);

    res.status(201).json({
      message: `Imported ${totalCreated} tasks from ${results.length} files`,
      totalCreated,
      results
    });
  } catch (error) {
    console.error('Import all error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

module.exports = router;

