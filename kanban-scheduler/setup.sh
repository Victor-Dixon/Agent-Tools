#!/bin/bash

echo "🚀 Setting up Kanban Life Scheduler..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm and try again."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL and try again."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Install server dependencies
echo "📦 Installing server dependencies..."
cd server
npm install

# Install client dependencies
echo "📦 Installing client dependencies..."
cd ../client
npm install

# Go back to root
cd ..

# Create environment files if they don't exist
if [ ! -f "server/.env" ]; then
    echo "📝 Creating server environment file..."
    cp server/.env.example server/.env
    echo "⚠️  Please edit server/.env with your database and GitHub credentials"
fi

if [ ! -f "client/.env" ]; then
    echo "📝 Creating client environment file..."
    cp client/.env.example client/.env
fi

# Generate Prisma client
echo "🔧 Generating Prisma client..."
cd server
npx prisma generate

# Push database schema
echo "🗄️  Setting up database..."
echo "⚠️  Make sure PostgreSQL is running and create a database named 'kanban_scheduler'"
echo "⚠️  Update DATABASE_URL in server/.env with your PostgreSQL connection string"
echo "⚠️  Then run: cd server && npx prisma db push"

cd ..

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit server/.env with your database credentials"
echo "2. Edit client/.env if needed"
echo "3. Run: cd server && npx prisma db push"
echo "4. Start the development servers: npm run dev"
echo ""
echo "The application will be available at:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:5000"
echo "- API Documentation: http://localhost:5000/health"
