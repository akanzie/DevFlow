#!/bin/bash
# DevFlow Setup Script
# Quick initialization script for DevFlow iOS project

echo "🚀 Setting up DevFlow iOS project..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Checking Xcode...${NC}"
if ! command -v xcode-select &> /dev/null; then
    echo "❌ Xcode not found. Please install Xcode from App Store."
    exit 1
fi
echo -e "${GREEN}✓ Xcode found${NC}"

echo -e "${BLUE}Step 2: Checking Swift version...${NC}"
SWIFT_VERSION=$(swift --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo -e "${GREEN}✓ Swift ${SWIFT_VERSION} installed${NC}"

echo -e "${BLUE}Step 3: Creating project structure...${NC}"
mkdir -p ios/DevFlow/App
mkdir -p ios/DevFlow/Features/{Planner,Habits,Notes,Feed,Burnout}/Views
mkdir -p ios/DevFlow/Features/Planner/ViewModels
mkdir -p ios/DevFlow/Core/{Models,Services,Extensions}
mkdir -p ios/DevFlow/Resources
mkdir -p ios/DevFlow/Tests
echo -e "${GREEN}✓ Project structure created${NC}"

echo -e "${BLUE}Step 4: Setting up Git...${NC}"
cd ios
if [ ! -d ".git" ]; then
    git init
    echo ".build/" >> .gitignore
    echo "*.xcarchive" >> .gitignore
    echo ".DS_Store" >> .gitignore
    echo "*.swiftpm" >> .gitignore
    git add .gitignore
    echo -e "${GREEN}✓ Git initialized${NC}"
else
    echo -e "${GREEN}✓ Git already initialized${NC}"
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Open DevFlow.xcodeproj in Xcode"
echo "2. Select target → Signing & Capabilities"
echo "3. Add iCloud capability with CloudKit"
echo "4. Set container ID: iCloud.com.devflow.app"
echo "5. Build and run (Cmd+R)"
echo ""
echo "For more info, see README.md"
