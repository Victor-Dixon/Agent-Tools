#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Kanban Scheduler - Starting Up...   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found! Please install Node.js first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Node.js found"

# Check if node_modules exist, install if needed
if [ ! -d "node_modules" ] || [ ! -d "server/node_modules" ] || [ ! -d "client/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies (this might take a minute)...${NC}"
    npm install --silent 2>/dev/null
    cd server && npm install --silent 2>/dev/null && cd ..
    cd client && npm install --silent 2>/dev/null && cd ..
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${GREEN}✓${NC} Dependencies already installed"
fi

# Setup server .env if it doesn't exist
if [ ! -f "server/.env" ]; then
    echo -e "${YELLOW}🔧 Setting up server configuration...${NC}"
    
    # Generate a random API key
    API_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    
    # Get local IP
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    
    cat > server/.env << EOF
# Server Configuration
PORT=5000
NODE_ENV=development
HOST=0.0.0.0

# Database (SQLite - no setup needed!)
DATABASE_URL="file:./prisma/dev.db"

# JWT Secret (auto-generated)
JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
JWT_EXPIRES_IN=7d

# AI Agent API Key (for agents to access from other computers)
AI_API_KEY=$API_KEY

# Client URL
CLIENT_URL=http://localhost:3000
EOF
    echo -e "${GREEN}✓${NC} Server config created"
else
    echo -e "${GREEN}✓${NC} Server config exists"
    
    # Check if AI_API_KEY exists, add if not
    if ! grep -q "AI_API_KEY" server/.env; then
        API_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
        echo "" >> server/.env
        echo "# AI Agent API Key (for agents to access from other computers)" >> server/.env
        echo "AI_API_KEY=$API_KEY" >> server/.env
        echo -e "${GREEN}✓${NC} AI API Key added to config"
    fi
fi

# Generate Prisma client and setup database if needed
if [ ! -d "server/node_modules/@prisma/client" ] || [ ! -f "server/prisma/dev.db" ]; then
    echo -e "${YELLOW}🔧 Setting up database...${NC}"
    cd server
    npm run db:generate --silent 2>/dev/null
    # Push schema to create database if it doesn't exist
    if [ ! -f "prisma/dev.db" ]; then
        npx prisma db push --accept-data-loss --skip-generate 2>/dev/null || true
    fi
    cd ..
    echo -e "${GREEN}✓${NC} Database ready"
else
    echo -e "${GREEN}✓${NC} Database ready"
fi

# Get the API key and IP for display
API_KEY=$(grep "AI_API_KEY" server/.env | cut -d '=' -f2 | tr -d '"' | tr -d "'" | head -1)
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        Everything is Ready! 🚀        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Starting servers...${NC}"
echo ""
echo -e "${YELLOW}📋 Quick Info:${NC}"
echo -e "   Web App:    ${GREEN}http://localhost:3000${NC}"
echo -e "   API Server: ${GREEN}http://localhost:5000${NC}"
if [ ! -z "$API_KEY" ]; then
    echo ""
    echo -e "${YELLOW}🤖 For Agents on Other Computers:${NC}"
    echo -e "   API URL:  ${GREEN}http://${LOCAL_IP}:5000/api/ai${NC}"
    echo -e "   API Key:  ${GREEN}${API_KEY}${NC}"
fi
echo ""
echo -e "${BLUE}───────────────────────────────────────────${NC}"
echo ""

# Start the servers
npm run dev

