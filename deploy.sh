#!/bin/bash

# Seti Backend Deployment Script
echo "🚀 Deploying Seti Backend to Render..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please initialize git first:"
    echo "   git init"
    echo "   git remote add origin <your-github-repo-url>"
    exit 1
fi

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Uncommitted changes detected. Committing them..."
    git add .
    git commit -m "Deploy: Update backend configuration for Base blockchain and Render deployment"
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main

echo "✅ Code pushed to GitHub!"
echo ""
echo "🔗 Next steps:"
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Select the 'backend' folder as root directory"
echo "5. Set environment variables (see DEPLOYMENT.md)"
echo "6. Deploy!"
echo ""
echo "📋 Required Environment Variables:"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_KEY" 
echo "   - SUPABASE_SERVICE_KEY"
echo "   - SECRET_KEY"
echo ""
echo "🎉 Your backend will be available at: https://your-app-name.onrender.com"
