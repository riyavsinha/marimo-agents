# Marimo Agents Docker Setup

This directory contains Docker configurations and scripts for building and running marimo with agents functionality.

## Overview

The marimo-agents fork includes AI agent functionality with a complete frontend. This setup provides Docker containers that include both the Python backend and the bundled frontend assets.

## Architecture

The build process follows these key steps:

1. **Frontend Build**: Build the React/TypeScript frontend locally using pnpm
2. **Asset Bundling**: Copy frontend assets to `marimo/_static/` for packaging
3. **Docker Build**: Create container with Python package including bundled assets
4. **Distribution**: Publish to PyPI with complete frontend included

## Files

- `Dockerfile.simple` - Simplified Docker build that uses pre-built frontend assets
- `Dockerfile.local` - Full Docker build with frontend compilation (may have dependency issues)
- `build_agents.sh` - Complete build script for marimo-agents
- `run_agents.sh` - Script to run the marimo-agents Docker container
- `README_AGENTS.md` - This documentation

## Quick Start

### Option 1: Use Pre-built Package from PyPI

```bash
# Build Docker image using published package
docker build -t marimo-agents-simple -f docker/Dockerfile.simple .

# Run the container
docker run -p 8081:8080 marimo-agents-simple

# Access marimo at http://localhost:8081
```

### Option 2: Build Complete Package Locally

```bash
# Run the complete build process
./docker/build_agents.sh

# Run the container
./docker/run_agents.sh

# Access marimo at http://localhost:8081
```

## Build Process Details

### 1. Frontend Build

The frontend is built using pnpm and Turbo:

```bash
cd frontend
pnpm install
pnpm build
```

This generates ~36MB of assets including:

- Main JavaScript bundle (~629KB)
- React Plotly bundle (~4.7MB)
- Node SQL Parser bundle (~2.6MB)
- Hundreds of additional language and theme assets

### 2. Asset Integration

Frontend assets are copied to the Python package:

```bash
bash scripts/buildfrontend.sh
```

This script:

- Removes old static files from `marimo/_static/`
- Copies new built assets from `frontend/dist/`
- Results in ~36MB of bundled frontend assets

### 3. Package Building

The Python package is built with bundled assets:

```bash
python -m build
```

This creates a ~33MB wheel file containing both Python code and frontend assets.

### 4. Docker Image

The Docker image includes:

- Python 3.11+ runtime
- Complete marimo-agents package
- All frontend assets
- Agent functionality

## Docker Images

### Dockerfile.simple (Recommended)

Uses the pre-built package from PyPI or local wheel:

```dockerfile
FROM python:3.11-slim
RUN pip install marimo-agents
EXPOSE 8080
CMD ["marimo", "edit", "--host", "0.0.0.0", "--port", "8080", "--no-token"]
```

**Pros:**

- Fast build time
- Reliable (uses tested package)
- Small final image

**Cons:**

- Requires package to be published or locally built

### Dockerfile.local

Builds everything from source including frontend:

```dockerfile
# Multi-stage build with Node.js and Python
```

**Pros:**

- Self-contained build
- No external dependencies

**Cons:**

- Complex dependency resolution
- Longer build time
- May fail on frontend dependencies

## Agent Functionality

The Docker image includes full agent support:

```python
import marimo as mo

# Register an agent
def my_agent(query: str) -> str:
    return f"Agent response to: {query}"

mo.ai.agents.register_agent(my_agent, name="my-agent")

# Use in cells
result = mo.ai.agents.run_agent("my-agent", "Hello!")
```

## Troubleshooting

### Frontend Build Issues

If local frontend build fails:

```bash
# Clean and rebuild
cd frontend
rm -rf node_modules dist
pnpm install
pnpm build
```

### Docker Build Issues

If Docker build fails:

1. Ensure frontend assets are built locally first
2. Use `Dockerfile.simple` instead of `Dockerfile.local`
3. Check that `marimo/_static/assets` contains ~36MB of files

### Container Runtime Issues

If container won't start:

1. Check Python version compatibility (requires 3.10+)
2. Verify frontend assets are included
3. Check port conflicts (default 8081)

## Development Workflow

For active development:

1. Make code changes
2. Rebuild frontend: `cd frontend && pnpm build`
3. Copy assets: `bash scripts/buildfrontend.sh`
4. Rebuild Docker: `docker build -t marimo-agents-simple -f docker/Dockerfile.simple .`
5. Test: `docker run -p 8081:8080 marimo-agents-simple`

## Production Deployment

For production use:

1. Build and publish package: `python -m build && hatch publish`
2. Use published package in Dockerfile.simple
3. Deploy with proper networking and persistence configurations

## Package Sizes

- Frontend assets: ~36MB
- Python wheel: ~33MB
- Docker image: ~150MB (with Python runtime)
- Published PyPI package: ~35MB

## Compatibility

- **Python**: 3.10+ (uses modern union syntax `str | None`)
- **Node.js**: 20+ (for frontend build)
- **Docker**: Any recent version
- **Browsers**: Modern browsers with ES2020+ support
