# Kanban Life Scheduler

A customized Kanban board task and project organizer that integrates with GitHub and supports AI agent interactions for managing both life tasks and development projects.

## Features

- 🎯 **Dual-purpose Kanban**: Manage both personal life tasks and GitHub projects
- 🤖 **AI Agent Integration**: API endpoints for AI agents to view and update tasks
- 🔄 **GitHub Sync**: Automatic synchronization with GitHub repositories and issues
- 📅 **Smart Scheduling**: Deadline management and task prioritization
- 👤 **Multi-user Support**: Authentication and user management
- 📱 **Responsive Design**: Modern, mobile-friendly interface

## Tech Stack

- **Backend**: Node.js, Express, PostgreSQL
- **Frontend**: React, TypeScript, Tailwind CSS
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: JWT tokens
- **GitHub Integration**: GitHub API v4 (GraphQL)

## Quick Start (Super Simple!)

**Just run this:**
```bash
npm start
```

That's it! The script automatically:
- ✅ Installs all dependencies
- ✅ Sets up the database
- ✅ Generates API keys
- ✅ Starts everything

Then open http://localhost:3000 in your browser!

---

### Manual Setup (if you prefer)

1. Install dependencies:
   ```bash
   npm run install-all
   ```

2. Set up environment variables:
   ```bash
   cp server/.env.example server/.env
   # Edit server/.env with your database and GitHub credentials
   ```

3. Set up the database:
   ```bash
   npm run db:setup
   ```

4. Start development servers:
   ```bash
   npm run dev
   ```

## Project Structure

```
kanban-scheduler/
├── server/           # Backend API
│   ├── controllers/  # Route controllers
│   ├── models/       # Database models
│   ├── routes/       # API routes
│   ├── middleware/   # Auth and validation
│   └── services/     # Business logic
├── client/           # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom hooks
│   │   └── services/    # API services
└── shared/           # Shared types and utilities
```

## AI Agent API

The system provides RESTful API endpoints for AI agents to interact with tasks and projects:

- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/github/sync` - Sync GitHub repositories

## License

MIT
