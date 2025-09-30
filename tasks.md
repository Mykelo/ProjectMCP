# MCP BigQuery Server - Task List

**Status Legend**: 🔴 Not Started | 🟡 In Progress | 🟢 Complete | ⏸️ Blocked

---

## Phase 1: Project Setup & Foundation 🔴

### 1.1 Initialize Project Structure
- [ ] 🔴 Create project root directory structure
- [ ] 🔴 Initialize git repository with .gitignore
- [ ] 🔴 Create README.md with project overview
- [ ] 🔴 Set up directory structure:
  ```
  ProjectMCP/
  ├── src/
  │   ├── mcp_bigquery/
  │   │   ├── __init__.py
  │   │   ├── server.py
  │   │   ├── auth.py
  │   │   ├── bigquery_client.py
  │   │   └── config.py
  ├── tests/
  ├── docs/
  ├── .env.example
  ├── pyproject.toml
  ├── Dockerfile
  ├── docker-compose.yml
  └── README.md
  ```

**Estimated Time**: 30 minutes

---

### 1.2 Configure uv Package Manager
- [ ] 🔴 Install uv on development machine
- [ ] 🔴 Create pyproject.toml with project metadata
- [ ] 🔴 Define dependencies:
  - fastmcp
  - google-cloud-bigquery>=3.38.0
  - python-dotenv
  - pydantic
  - pydantic-settings
- [ ] 🔴 Create uv.lock file
- [ ] 🔴 Test dependency installation

**Estimated Time**: 45 minutes

---

## Phase 2: Core MCP Server Implementation 🔴

### 2.1 Configuration Management
- [ ] 🔴 Create config.py with Pydantic Settings
- [ ] 🔴 Define environment variables:
  - BEARER_TOKEN
  - GOOGLE_APPLICATION_CREDENTIALS
  - GCP_PROJECT_ID
  - LOG_LEVEL
- [ ] 🔴 Create .env.example template
- [ ] 🔴 Add validation for required settings

**Estimated Time**: 1 hour

---

### 2.2 Bearer Token Authentication
- [ ] 🔴 Create auth.py module
- [ ] 🔴 Implement bearer token validation function
- [ ] 🔴 Create authentication decorator for MCP tools
- [ ] 🔴 Add token extraction from MCP context/headers
- [ ] 🔴 Implement error responses for invalid tokens (MCP error format)
- [ ] 🔴 Add logging for authentication attempts
- [ ] 🔴 Write unit tests for authentication

**Estimated Time**: 2 hours

---

### 2.3 BigQuery Client Wrapper
- [ ] 🔴 Create bigquery_client.py module
- [ ] 🔴 Initialize BigQuery client with credentials
- [ ] 🔴 Implement query execution function (QueryJob.result() → RowIterator)
- [ ] 🔴 Implement list datasets function (Client.list_datasets)
- [ ] 🔴 Implement get dataset info function (Client.get_dataset)
- [ ] 🔴 Implement list tables function (Client.list_tables)
- [ ] 🔴 Implement get table info function (Client.get_table)
- [ ] 🔴 Add error handling and logging
- [ ] 🔴 Write unit tests with mocked BigQuery client

**Estimated Time**: 3 hours

---

### 2.4 FastMCP Server Implementation
- [ ] 🔴 Create server.py with FastMCP app initialization
- [ ] 🔴 Define MCP tools with @mcp.tool decorator:
  - `list_datasets`: List BigQuery datasets (with pagination)
  - `get_dataset_info`: Get dataset metadata
  - `list_tables`: List tables in a dataset (with pagination)
  - `get_table_info`: Get table metadata and schema
  - `execute_query`: Execute SQL query and return results (with pagination)
- [ ] 🔴 Add Pydantic Field constraints for validation (FQID patterns, ranges)
- [ ] 🔴 Integrate bearer token authentication (decorator or middleware)
- [ ] 🔴 Integrate BigQuery client wrapper
- [ ] 🔴 Add comprehensive error handling (BigQuery exceptions → MCP errors)
- [ ] 🔴 Add structured logging
- [ ] 🔴 Implement pagination support (page_size, page_token, next_page_token)

**Estimated Time**: 4 hours

---

## Phase 3: Containerization 🔴

### 3.1 Dockerfile Creation
- [ ] 🔴 Create multi-stage Dockerfile
- [ ] 🔴 Stage 1: Build stage with uv
- [ ] 🔴 Stage 2: Runtime stage (minimal image)
- [ ] 🔴 Copy application code
- [ ] 🔴 Set up proper user permissions (non-root)
- [ ] 🔴 Define ENTRYPOINT and CMD (fastmcp run or python -m mcp_bigquery)
- [ ] 🔴 Expose ports if using SSE transport (optional)
- [ ] 🔴 Test Docker build locally

**Estimated Time**: 2 hours

---

### 3.2 Docker Compose Setup
- [ ] 🔴 Create docker-compose.yml
- [ ] 🔴 Define service configuration
- [ ] 🔴 Set up volume mounts for credentials
- [ ] 🔴 Configure environment variables
- [ ] 🔴 Add health check configuration
- [ ] 🔴 Test with docker-compose up

**Estimated Time**: 1.5 hours

---

### 3.3 Container Optimization
- [ ] 🔴 Optimize image size
- [ ] 🔴 Add .dockerignore file
- [ ] 🔴 Implement proper logging for containers
- [ ] 🔴 Add container health checks
- [ ] 🔴 Document port mappings and volumes

**Estimated Time**: 1 hour

---

## Phase 4: Testing & Validation 🔴

### 4.1 Unit Tests
- [ ] 🔴 Set up pytest configuration
- [ ] 🔴 Write tests for auth module
- [ ] 🔴 Write tests for config module
- [ ] 🔴 Write tests for BigQuery client wrapper
- [ ] 🔴 Mock external BigQuery API calls
- [ ] 🔴 Achieve >80% code coverage

**Estimated Time**: 3 hours

---

### 4.2 Integration Tests
- [ ] 🔴 Test full MCP tool execution flow
- [ ] 🔴 Test authentication integration
- [ ] 🔴 Test BigQuery query execution (with test dataset)
- [ ] 🔴 Test error scenarios
- [ ] 🔴 Validate MCP protocol compliance

**Estimated Time**: 2 hours

---

### 4.3 Docker Testing
- [ ] 🔴 Test container builds successfully
- [ ] 🔴 Test container starts and runs
- [ ] 🔴 Test authentication in container
- [ ] 🔴 Test BigQuery connectivity from container
- [ ] 🔴 Test environment variable injection

**Estimated Time**: 1.5 hours

---

## Phase 5: Documentation 🔴

### 5.1 User Documentation
- [ ] 🔴 Write comprehensive README.md
- [ ] 🔴 Document installation steps
- [ ] 🔴 Document configuration options
- [ ] 🔴 Create quickstart guide
- [ ] 🔴 Document available MCP tools (reference docs/TOOLS.md)
- [ ] 🔴 Add MCP client setup instructions (Claude Desktop, etc.)
- [ ] 🔴 Add troubleshooting section

**Estimated Time**: 2 hours

---

### 5.2 Developer Documentation
- [ ] 🔴 Document code architecture
- [ ] 🔴 Add inline code comments
- [ ] 🔴 Create CONTRIBUTING.md
- [ ] 🔴 Document testing procedures
- [ ] 🔴 Add examples of common use cases

**Estimated Time**: 1.5 hours

---

### 5.3 Deployment Documentation
- [ ] 🔴 Document Docker deployment
- [ ] 🔴 Document environment setup
- [ ] 🔴 Document BigQuery service account setup
- [ ] 🔴 Create deployment checklist
- [ ] 🔴 Add security best practices

**Estimated Time**: 1 hour

---

## Phase 6: Security & Best Practices 🔴

### 6.1 Security Hardening
- [ ] 🔴 Implement secrets management best practices
- [ ] 🔴 Add input validation and sanitization
- [ ] 🔴 Implement rate limiting (if needed)
- [ ] 🔴 Security audit of dependencies
- [ ] 🔴 Add security headers
- [ ] 🔴 Document security considerations

**Estimated Time**: 2 hours

---

### 6.2 Code Quality
- [ ] 🔴 Add pre-commit hooks
- [ ] 🔴 Configure code formatting (black/ruff)
- [ ] 🔴 Configure linting (ruff/pylint)
- [ ] 🔴 Add type checking with mypy
- [ ] 🔴 Run security scanner (bandit)

**Estimated Time**: 1.5 hours

---

## Phase 7: Final Polish & Release 🔴

### 7.1 Final Testing
- [ ] 🔴 End-to-end testing
- [ ] 🔴 Performance testing
- [ ] 🔴 Load testing (if applicable)
- [ ] 🔴 Security testing
- [ ] 🔴 Documentation review

**Estimated Time**: 2 hours

---

### 7.2 Release Preparation
- [ ] 🔴 Version tagging
- [ ] 🔴 Create CHANGELOG.md
- [ ] 🔴 Prepare release notes
- [ ] 🔴 Build and tag Docker image
- [ ] 🔴 Final documentation review

**Estimated Time**: 1 hour

---

## Summary

**Total Estimated Time**: ~30 hours
**Recommended Timeline**: 5-7 days (with 4-6 hours per day)

### Phases Breakdown:
1. **Phase 1** (Setup): 1.25 hours
2. **Phase 2** (Core Implementation): 10 hours
3. **Phase 3** (Containerization): 4.5 hours
4. **Phase 4** (Testing): 6.5 hours
5. **Phase 5** (Documentation): 4.5 hours
6. **Phase 6** (Security): 3.5 hours
7. **Phase 7** (Release): 3 hours

### Critical Path:
1. Project Setup → 2. Core Implementation → 3. Containerization → 4. Testing

### Dependencies:
- BigQuery service account JSON credentials
- Docker installed on development machine
- GCP project with BigQuery API enabled
- uv package manager installed
- MCP client (e.g., Claude Desktop) for testing

### Reference Documentation:
- Tool specifications: `docs/TOOLS.md`
- FastMCP tools guide: https://gofastmcp.com/servers/tools
- BigQuery Python client: https://cloud.google.com/python/docs/reference/bigquery/latest/summary_method

---

## Notes & Considerations

### MCP Tools Implementation
The server will expose 5 FastMCP tools:
1. **list_datasets** - List BigQuery datasets with pagination
2. **get_dataset_info** - Get dataset metadata (location, description, labels, access)
3. **list_tables** - List tables in a dataset with pagination
4. **get_table_info** - Get table metadata (schema, rows, bytes, partitioning, clustering)
5. **execute_query** - Execute SQL queries with pagination and statistics

All tools use:
- Type annotations for automatic schema generation
- Pydantic Field constraints for validation (patterns, ranges)
- Bearer token authentication (decorator/middleware)
- Consistent error handling (BigQuery exceptions → MCP errors)

### BigQuery API Quotas
- Be aware of BigQuery API quotas and limits
- Consider implementing query result caching
- Add query timeout configurations

### MCP Protocol Compliance
- Follow FastMCP best practices (use @mcp.tool decorator)
- Ensure proper error message formatting (MCP error results)
- Use type annotations and Pydantic Field for schema generation
- Implement standard MCP response structures (dict returns)
- Support pagination with page_size, page_token, next_page_token

### Bearer Token Security
- Generate secure random tokens (32+ characters)
- Consider token rotation strategy
- Document token generation process

### Future Enhancements (Post-MVP)
- [ ] Add query result streaming (to_arrow_iterable, to_dataframe_iterable)
- [ ] Implement query result caching
- [ ] Add support for parameterized queries (ScalarQueryParameter, arrays, structs)
- [ ] Add BigQuery job management tools (list jobs, cancel job, get job details)
- [ ] Use BigQuery Storage API for faster reads (bqstorage_client)
- [ ] Add MCP resources (in addition to tools) for browsing datasets/tables
- [ ] Multi-tenant support with multiple bearer tokens
- [ ] Add dataset/table creation and modification tools
