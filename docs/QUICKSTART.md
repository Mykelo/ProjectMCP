# MCP BigQuery Server - Quick Start Guide

## 🎯 Project Goal

Build a secure MCP server that allows AI assistants (like Claude) to query Google BigQuery databases through the Model Context Protocol, using bearer token authentication and containerized deployment.

## 📋 Prerequisites

Before starting, ensure you have:

1. **Python 3.11+** installed
2. **Docker Desktop** installed and running
3. **Google Cloud Project** with BigQuery API enabled
4. **Service Account** with BigQuery permissions
5. **uv package manager** installed (`pip install uv`)

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                      MCP Client                          │
│                   (Claude Desktop)                       │
└────────────────────────┬─────────────────────────────────┘
                         │
                         │ HTTP/STDIO + Bearer Token
                         │
┌────────────────────────▼─────────────────────────────────┐
│                   MCP Server (FastMCP)                   │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Auth     │  │   BigQuery   │  │   MCP Tools     │  │
│  │ Middleware │→ │    Client    │→ │  - execute_query│  │
│  │            │  │              │  │  - list_datasets│  │
│  └────────────┘  └──────────────┘  └─────────────────┘  │
└────────────────────────┬─────────────────────────────────┘
                         │
                         │ Google Cloud API
                         │
┌────────────────────────▼─────────────────────────────────┐
│              Google BigQuery Service                     │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Dataset 1│  │ Dataset 2│  │ Dataset 3│  ...         │
│  └──────────┘  └──────────┘  └──────────┘              │
└──────────────────────────────────────────────────────────┘
```

## 🚀 Implementation Plan (7 Phases)

### Phase 1: Project Setup (1.25 hours) ⭐ START HERE
**Goal**: Set up the project structure and dependency management

1. Create directory structure
2. Initialize git repository
3. Configure uv and pyproject.toml
4. Set up development environment

**Files to create**:
- `pyproject.toml` - Python project configuration
- `.gitignore` - Git ignore patterns
- `README.md` - Project documentation
- `.env.example` - Environment variables template

---

### Phase 2: Core Implementation (10 hours)
**Goal**: Implement the MCP server with BigQuery integration

**Components**:

1. **Configuration Management** (`config.py`)
   - Environment variable handling
   - Settings validation
   - Secure credential loading

2. **Authentication** (`auth.py`)
   - Bearer token validation
   - Request authentication middleware
   - Security logging

3. **BigQuery Client** (`bigquery_client.py`)
   - Query execution
   - Dataset/table listing
   - Schema introspection
   - Error handling

4. **MCP Server** (`server.py`)
   - FastMCP application setup
   - Tool definitions (execute_query, list_datasets, etc.)
   - Request routing
   - Response formatting

---

### Phase 3: Containerization (4.5 hours)
**Goal**: Package the server in a Docker container

**Deliverables**:
1. Multi-stage Dockerfile
2. docker-compose.yml for easy deployment
3. .dockerignore for optimization
4. Health check configuration

**Key considerations**:
- Use Python 3.11 slim base image
- Install uv in build stage
- Copy only necessary files to runtime stage
- Run as non-root user
- Securely mount credentials

---

### Phase 4: Testing (6.5 hours)
**Goal**: Ensure reliability and correctness

**Test types**:
1. **Unit tests**: Individual functions and classes
2. **Integration tests**: Component interactions
3. **Docker tests**: Container functionality
4. **E2E tests**: Full workflow validation

**Tools**: pytest, pytest-mock, coverage

---

### Phase 5: Documentation (4.5 hours)
**Goal**: Make the project easy to use and maintain

**Documents**:
1. README.md - User-facing documentation
2. CONTRIBUTING.md - Developer guidelines
3. API.md - MCP tools reference
4. DEPLOYMENT.md - Production deployment guide

---

### Phase 6: Security & Quality (3.5 hours)
**Goal**: Harden security and code quality

**Tasks**:
1. Security scanning (bandit)
2. Dependency auditing
3. Code formatting (black/ruff)
4. Type checking (mypy)
5. Pre-commit hooks

---

### Phase 7: Release (3 hours)
**Goal**: Prepare for production use

**Final steps**:
1. End-to-end testing
2. Version tagging
3. CHANGELOG creation
4. Docker image publishing
5. Final documentation review

---

## 🛠️ Key Technologies

### FastMCP (GoFastMCP)
- **Purpose**: MCP server framework
- **Usage**: Simplifies MCP protocol implementation
- **Features**: Tool definition, resource management, request handling

### google-cloud-bigquery
- **Purpose**: BigQuery Python client
- **Version**: 3.38.0+
- **Features**: Query execution, dataset management, authentication

### uv
- **Purpose**: Fast Python package manager
- **Benefits**: 
  - Faster than pip
  - Better dependency resolution
  - Compatible with pip/pypi
  - Generates lock files

### Docker
- **Purpose**: Containerization
- **Benefits**:
  - Consistent deployment
  - Isolated environment
  - Easy scaling
  - Portable across systems

---

## 🔐 Security Approach

### Bearer Token Authentication
```
Authorization: Bearer <YOUR_SECRET_TOKEN>
```

- Token stored in environment variable
- Validated on every request
- Logged for audit purposes
- Should be 32+ characters, randomly generated

### BigQuery Authentication
```
Service Account Key (JSON) → Environment/File → BigQuery Client
```

- Use dedicated service account
- Principle of least privilege
- Never commit credentials to git
- Mount securely in Docker

---

## 📁 Project Structure

```
ProjectMCP/
├── src/
│   └── mcp_bigquery/
│       ├── __init__.py          # Package initialization
│       ├── server.py            # FastMCP server (main entry)
│       ├── auth.py              # Authentication middleware
│       ├── bigquery_client.py   # BigQuery wrapper
│       └── config.py            # Configuration management
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── conftest.py              # Pytest configuration
├── docs/
│   ├── API.md                   # MCP tools documentation
│   └── DEPLOYMENT.md            # Deployment guide
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── .dockerignore                # Docker ignore rules
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Docker orchestration
├── pyproject.toml               # Python project config
├── uv.lock                      # Dependency lock file
├── README.md                    # Main documentation
└── tasks.md                     # Task tracking (this plan)
```

---

## 🎬 Getting Started - First Steps

### 1. Install uv
```bash
pip install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone/Initialize Repository
```bash
cd /Users/michal/Documents/workspace/ProjectMCP
git init
```

### 3. Create pyproject.toml
```bash
uv init
# Edit pyproject.toml to add dependencies
```

### 4. Install Dependencies
```bash
uv sync
```

### 5. Create .env File
```bash
cp .env.example .env
# Edit .env with your credentials
```

---

## 🧪 Development Workflow

1. **Feature branch**: Create branch for each phase
2. **Implement**: Write code following the task list
3. **Test**: Run tests locally
4. **Commit**: Use conventional commits
5. **Merge**: Merge to main when phase complete

---

## 📊 Success Metrics

- [ ] Server starts successfully in Docker
- [ ] Bearer token authentication works
- [ ] Can execute BigQuery queries
- [ ] Can list datasets and tables
- [ ] Error handling is robust
- [ ] Tests pass with >80% coverage
- [ ] Documentation is complete

---

## 🆘 Common Issues & Solutions

### Issue: uv not found
**Solution**: Install uv using pip or the official installer

### Issue: BigQuery authentication fails
**Solution**: Verify service account JSON is valid and GOOGLE_APPLICATION_CREDENTIALS points to correct file

### Issue: Docker build fails
**Solution**: Check Dockerfile syntax, ensure base images are available

### Issue: MCP client can't connect
**Solution**: Verify bearer token matches, check server logs

---

## 📚 Useful Resources

- **FastMCP Documentation**: [GitHub](https://github.com/jlowin/fastmcp)
- **BigQuery Python Client**: [Documentation](https://cloud.google.com/python/docs/reference/bigquery/latest)
- **MCP Protocol**: [Specification](https://modelcontextprotocol.io)
- **uv Package Manager**: [Documentation](https://github.com/astral-sh/uv)

---

## 🎯 Next Steps

1. ✅ Review `tasks.md` for detailed task breakdown
2. ✅ Review `projectbrief.md` for technical overview
3. 🚀 Start with **Phase 1: Project Setup**
4. 📝 Update task status as you progress
5. 🧪 Test each component before moving to next phase

**Ready to start?** Begin with Phase 1.1 in `tasks.md`!
