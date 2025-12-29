const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { body, validationResult, query } = require('express-validator');
const prisma = require('../utils/database');
const { authenticateToken, authenticateAIAgent } = require('../middleware/auth');

const router = express.Router();

// Configure multer for image uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = path.join(__dirname, '../uploads/whiteboards');
    // Create directory if it doesn't exist
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    // Generate unique filename
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const ext = path.extname(file.originalname);
    cb(null, `whiteboard-${uniqueSuffix}${ext}`);
  }
});

const fileFilter = (req, file, cb) => {
  // Accept image files
  if (file.mimetype.startsWith('image/')) {
    cb(null, true);
  } else {
    cb(new Error('Only image files are allowed'), false);
  }
};

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: fileFilter
});

// OCR function - using Tesseract.js
async function performOCR(imagePath) {
  try {
    // Try to use Tesseract if available, otherwise return null
    const Tesseract = require('tesseract.js');
    const { data: { text } } = await Tesseract.recognize(imagePath, 'eng', {
      logger: m => {
        if (m.status === 'recognizing text') {
          // Progress logging if needed
        }
      }
    });
    return text.trim();
  } catch (error) {
    console.error('OCR error:', error);
    // If Tesseract is not installed or fails, return null
    // The user can manually transcribe
    return null;
  }
}

// Get all whiteboards for the authenticated user
router.get('/', authenticateToken, [
  query('page').optional().isInt({ min: 1 }).toInt(),
  query('limit').optional().isInt({ min: 1, max: 100 }).toInt(),
  query('search').optional().isString(),
  query('tag').optional().isString()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 50;
    const skip = (page - 1) * limit;
    const search = req.query.search;
    const tag = req.query.tag;

    // Build where clause
    const where = {
      userId: req.user.id
    };

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

    const [whiteboards, total] = await Promise.all([
      prisma.whiteboard.findMany({
        where,
        orderBy: [
          { isPinned: 'desc' },
          { updatedAt: 'desc' }
        ],
        skip,
        take: limit
      }),
      prisma.whiteboard.count({ where })
    ]);

    res.json({
      whiteboards,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Get whiteboards error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get a single whiteboard
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const whiteboard = await prisma.whiteboard.findFirst({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!whiteboard) {
      return res.status(404).json({ error: 'Whiteboard not found' });
    }

    res.json(whiteboard);
  } catch (error) {
    console.error('Get whiteboard error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create a new whiteboard
router.post('/', authenticateToken, [
  body('title').trim().notEmpty().withMessage('Title is required'),
  body('content').optional().isString(),
  body('tags').optional().isString(),
  body('color').optional().isString(),
  body('isPinned').optional().isBoolean()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { title, content, tags, color, isPinned } = req.body;

    const whiteboard = await prisma.whiteboard.create({
      data: {
        title,
        content: content || null,
        tags: tags || null,
        color: color || '#8B5CF6',
        isPinned: isPinned || false,
        userId: req.user.id
      }
    });

    res.status(201).json(whiteboard);
  } catch (error) {
    console.error('Create whiteboard error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Upload image and perform OCR
router.post('/upload', authenticateToken, upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    const { title, tags, performOCR: shouldPerformOCR } = req.body;

    // Generate URL for the uploaded image
    const imageUrl = `/uploads/whiteboards/${req.file.filename}`;

    // Perform OCR if requested
    let transcription = null;
    if (shouldPerformOCR === 'true' || shouldPerformOCR === true) {
      transcription = await performOCR(req.file.path);
    }

    // Create whiteboard with image
    const whiteboard = await prisma.whiteboard.create({
      data: {
        title: title || `Whiteboard ${new Date().toLocaleDateString()}`,
        imageUrl,
        transcription,
        tags: tags || null,
        userId: req.user.id
      }
    });

    res.status(201).json({
      ...whiteboard,
      ocrAvailable: transcription !== null
    });
  } catch (error) {
    console.error('Upload whiteboard error:', error);
    
    // Clean up uploaded file if whiteboard creation failed
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }

    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
});

// Trigger OCR on existing whiteboard image
router.post('/:id/transcribe', authenticateToken, async (req, res) => {
  try {
    const whiteboard = await prisma.whiteboard.findFirst({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!whiteboard) {
      return res.status(404).json({ error: 'Whiteboard not found' });
    }

    if (!whiteboard.imageUrl) {
      return res.status(400).json({ error: 'No image to transcribe' });
    }

    // Construct full path to image
    const imagePath = path.join(__dirname, '..', whiteboard.imageUrl);

    if (!fs.existsSync(imagePath)) {
      return res.status(404).json({ error: 'Image file not found' });
    }

    // Perform OCR
    const transcription = await performOCR(imagePath);

    // Update whiteboard with transcription
    const updated = await prisma.whiteboard.update({
      where: { id: whiteboard.id },
      data: { transcription }
    });

    res.json({
      ...updated,
      ocrAvailable: transcription !== null
    });
  } catch (error) {
    console.error('Transcribe whiteboard error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message 
    });
  }
});

// Update a whiteboard
router.put('/:id', authenticateToken, [
  body('title').optional().trim().notEmpty(),
  body('content').optional().isString(),
  body('tags').optional().isString(),
  body('color').optional().isString(),
  body('isPinned').optional().isBoolean()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Check if whiteboard exists and belongs to user
    const existing = await prisma.whiteboard.findFirst({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!existing) {
      return res.status(404).json({ error: 'Whiteboard not found' });
    }

    const { title, content, tags, color, isPinned, transcription } = req.body;

    const whiteboard = await prisma.whiteboard.update({
      where: { id: req.params.id },
      data: {
        ...(title && { title }),
        ...(content !== undefined && { content }),
        ...(tags !== undefined && { tags }),
        ...(color && { color }),
        ...(isPinned !== undefined && { isPinned }),
        ...(transcription !== undefined && { transcription })
      }
    });

    res.json(whiteboard);
  } catch (error) {
    console.error('Update whiteboard error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete a whiteboard
router.delete('/:id', authenticateToken, async (req, res) => {
  try {
    const whiteboard = await prisma.whiteboard.findFirst({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!whiteboard) {
      return res.status(404).json({ error: 'Whiteboard not found' });
    }

    // Delete image file if exists
    if (whiteboard.imageUrl) {
      const imagePath = path.join(__dirname, '..', whiteboard.imageUrl);
      if (fs.existsSync(imagePath)) {
        fs.unlinkSync(imagePath);
      }
    }

    await prisma.whiteboard.delete({
      where: { id: req.params.id }
    });

    res.json({ message: 'Whiteboard deleted successfully' });
  } catch (error) {
    console.error('Delete whiteboard error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Note: Static file serving for uploads is handled in server/index.js
// This route is kept for backward compatibility but may not be needed

module.exports = router;

