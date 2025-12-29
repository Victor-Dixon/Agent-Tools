const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const authRoutes = require('./routes/auth');
const taskRoutes = require('./routes/tasks');
const projectRoutes = require('./routes/projects');
const boardRoutes = require('./routes/boards');
const githubRoutes = require('./routes/github');
const aiAgentRoutes = require('./routes/aiAgent');
const taskTemplateRoutes = require('./routes/taskTemplates');
const taskImporterRoutes = require('./routes/taskImporter');
const whiteboardRoutes = require('./routes/whiteboards');

const app = express();
const PORT = process.env.PORT || 5000;

// Security middleware
app.use(helmet());
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // limit each IP to 1000 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});
app.use('/api/', limiter);

// CORS configuration
// Allow requests from any origin for development (AI agents can access from other computers)
// In production, you should restrict this to specific origins
const corsOptions = {
  origin: function (origin, callback) {
    // Allow requests with no origin (like mobile apps, curl, or AI agents)
    if (!origin) return callback(null, true);
    
    // In development, allow all origins for AI agent access
    if (process.env.NODE_ENV !== 'production') {
      return callback(null, true);
    }
    
    // In production, check against allowed origins
    const allowedOrigins = process.env.ALLOWED_ORIGINS 
      ? process.env.ALLOWED_ORIGINS.split(',')
      : [process.env.CLIENT_URL || 'http://localhost:3000'];
    
    if (allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true
};

app.use(cors(corsOptions));

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Serve static files for uploaded images
const path = require('path');
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/tasks', taskRoutes);
app.use('/api/projects', projectRoutes);
app.use('/api/boards', boardRoutes);
app.use('/api/github', githubRoutes);
app.use('/api/ai', aiAgentRoutes);
app.use('/api/templates', taskTemplateRoutes);
app.use('/api/import', taskImporterRoutes);
app.use('/api/whiteboards', whiteboardRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

const os = require('os');

// Get local IP address for network access
const getLocalIP = () => {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return 'localhost';
};

const HOST = process.env.HOST || '0.0.0.0'; // Listen on all interfaces
const localIP = getLocalIP();

app.listen(PORT, HOST, () => {
  console.log('');
  console.log('═══════════════════════════════════════════════════════════');
  console.log('🚀  SERVER IS RUNNING!');
  console.log('═══════════════════════════════════════════════════════════');
  console.log('');
  console.log('📱  Web App:     http://localhost:3000');
  console.log('🔧  API Server:  http://localhost:' + PORT);
  console.log('');
  console.log('🌐  FOR AGENTS ON OTHER COMPUTERS:');
  console.log('───────────────────────────────────────────────────────────');
  console.log('   API URL:  http://' + localIP + ':' + PORT + '/api/ai');
  if (process.env.AI_API_KEY) {
    console.log('   API Key:  ' + process.env.AI_API_KEY);
    console.log('');
    console.log('   Copy these two lines above for your agents!');
  } else {
    console.log('   ⚠️  API Key not set - check server/.env file');
  }
  console.log('───────────────────────────────────────────────────────────');
  console.log('');
});

module.exports = app;
