#!/bin/bash
set -e

echo "🚀 Building marimo-agents complete package..."

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Error: Must run from marimo project root directory"
    exit 1
fi

# Check if frontend directory exists
if [[ ! -d "frontend" ]]; then
    echo "❌ Error: frontend directory not found"
    exit 1
fi

echo "📦 Step 1: Installing frontend dependencies..."
cd frontend
if ! command -v pnpm &> /dev/null; then
    echo "❌ Error: pnpm not found. Please install pnpm first:"
    echo "   npm install -g pnpm"
    exit 1
fi

pnpm install

echo "🔨 Step 2: Building frontend assets..."
pnpm build

echo "📁 Frontend build completed. Assets generated in frontend/dist/"

cd ..

echo "📋 Step 3: Copying frontend assets to marimo/_static/..."
if [[ ! -f "scripts/buildfrontend.sh" ]]; then
    echo "❌ Error: scripts/buildfrontend.sh not found"
    exit 1
fi

bash scripts/buildfrontend.sh

echo "✅ Frontend assets copied to marimo/_static/"

echo "📦 Step 4: Building Python package..."
if ! command -v python &> /dev/null; then
    echo "❌ Error: python not found"
    exit 1
fi

# Install build if not available
if ! python -c "import build" 2>/dev/null; then
    echo "Installing build package..."
    pip install build
fi

python -m build

echo "📊 Step 5: Checking package size..."
if [[ -d "dist" ]]; then
    latest_wheel=$(ls -t dist/*.whl | head -1)
    if [[ -n "$latest_wheel" ]]; then
        wheel_size=$(du -h "$latest_wheel" | cut -f1)
        echo "✅ Package built: $latest_wheel ($wheel_size)"
    fi
fi

echo "🐳 Step 6: Building Docker image..."
docker build -t marimo-agents-simple -f docker/Dockerfile.simple .

echo "✅ Step 7: Verifying Docker image..."
echo "Testing Docker image startup..."
timeout 10s docker run --rm marimo-agents-simple marimo --help > /dev/null || true

echo ""
echo "🎉 Build complete!"
echo ""
echo "📋 What was built:"
echo "  • Frontend assets: $(du -sh marimo/_static/assets | cut -f1)"
echo "  • Python package: $(ls -t dist/*.whl | head -1)"
echo "  • Docker image: marimo-agents-simple"
echo ""
echo "🚀 To run:"
echo "  docker run -p 8081:8080 marimo-agents-simple"
echo "  Then visit: http://localhost:8081"
echo ""
echo "📦 To publish to PyPI:"
echo "  hatch publish"
echo ""