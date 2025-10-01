# MCP BigQuery Server

A secure Model Context Protocol (MCP) server that provides AI assistants with access to Google BigQuery through bearer token authentication, built with Python, FastMCP, and Docker.

## 🎯 Overview

This project implements an MCP server that enables AI assistants (like Claude) to interact with Google BigQuery datasets securely. The server uses bearer token authentication and is containerized with Docker for easy deployment.

## ✨ Features

- 🔐 **Secure Authentication**: Bearer token authentication for API access
- 🗄️ **BigQuery Integration**: Execute queries and explore datasets
- 🐳 **Containerized**: Docker-ready for consistent deployment
- ⚡ **Modern Tooling**: Built with uv package manager for fast, reliable builds
- 📊 **MCP Protocol**: Full Model Context Protocol compliance

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **MCP Framework**: [FastMCP](https://github.com/jlowin/fastmcp)
- **BigQuery Client**: [google-cloud-bigquery](https://pypi.org/project/google-cloud-bigquery/) v3.38.0+
- **Container**: Docker + Docker Compose
- **Testing**: pytest

## 📁 Project Structure

```
ProjectMCP/
├── src/mcp_bigquery/         # Main application code
│   ├── server.py             # FastMCP server
│   ├── auth.py               # Authentication middleware
│   ├── bigquery_client.py    # BigQuery wrapper
│   └── config.py             # Configuration
├── scripts/                  # Utility scripts
│   └── generate_jwt_token.py # JWT token generator for testing
├── tests/                    # Test suite
├── docs/                     # Documentation
├── Dockerfile                # Container definition
├── docker-compose.yml        # Orchestration
├── pyproject.toml            # Python dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker Desktop
- Google Cloud Project with BigQuery API enabled
- Service Account with BigQuery permissions
- uv package manager

### Installation

```bash
# Install uv
pip install uv

# Clone repository
git clone <repository-url>
cd ProjectMCP

# Install dependencies
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run with Docker
docker-compose up
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Detailed getting started guide
- **[tasks.md](tasks.md)** - Complete implementation task list
- **[projectbrief.md](projectbrief.md)** - Technical architecture and requirements

## 🔧 Configuration

The server requires the following environment variables:

```bash
BEARER_TOKEN=your-secret-token-here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_PROJECT_ID=your-gcp-project-id
LOG_LEVEL=INFO
```

## 🎯 Available MCP Tools

Once running, the server provides these MCP tools:

- **`execute_query`** - Execute SQL queries on BigQuery
- **`list_datasets`** - List all available datasets
- **`list_tables`** - List tables in a dataset
- **`get_table_schema`** - Retrieve table schema information

## 🧪 Development

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/mcp_bigquery

# Format code
uv run black src/ tests/

# Type checking
uv run mypy src/

# Generate JWT tokens and save keys to files
uv run python scripts/generate_jwt_token.py --public-key-file public_key.pem --private-key-file private_key.pem --token-file token.txt

# View help for all options
uv run python scripts/generate_jwt_token.py --help
```

## 📊 Implementation Progress

See [tasks.md](tasks.md) for detailed progress tracking.

**Current Status**: 🔴 Planning Phase

### Phases

1. ⏳ Phase 1: Project Setup (0/2 complete)
2. ⏳ Phase 2: Core Implementation (0/4 complete)
3. ⏳ Phase 3: Containerization (0/3 complete)
4. ⏳ Phase 4: Testing (0/3 complete)
5. ⏳ Phase 5: Documentation (0/3 complete)
6. ⏳ Phase 6: Security & Quality (0/2 complete)
7. ⏳ Phase 7: Release (0/2 complete)

## 🔐 Security

- Bearer tokens should be 32+ characters and randomly generated
- Service account credentials should never be committed to version control
- Use principle of least privilege for BigQuery permissions
- All authentication attempts are logged
- Docker containers run as non-root user

## 📝 License

[Add your license here]

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📧 Contact

[Add your contact information]

---

**Status**: This project is in planning/development phase. See [tasks.md](tasks.md) for current progress.
