# Gate Pass AI Agent

A conversational AI agent that provides a natural language interface to the Gate Pass Management API. Built with LangChain, the agent enables users with different roles (HR, Admin, Gate personnel) to perform gate pass operations through natural conversations.

## Features

- **Natural Language Interface**: Interact with the Gate Pass API using conversational language
- **Role-Based Access Control**: Tools are filtered based on user roles (HR, Admin, Gate)
- **Multi-Turn Conversations**: Maintains context across conversation turns
- **Comprehensive Error Handling**: User-friendly error messages with recovery guidance
- **File Upload Support**: Handle photo uploads for gate scanning operations
- **Property-Based Testing**: Extensive test coverage using Hypothesis

## Architecture

The agent uses a tool-based architecture where each API endpoint is exposed as a tool:

- **HR Tools**: Create, list, view, and print gate passes
- **Admin Tools**: Approve, reject, delete, and manage gate passes
- **Gate Tools**: Scan exits/returns with photo uploads, view gate pass details
- **Notification Tools**: Check and manage notifications
- **QR Code Tools**: Generate QR codes for gate passes

## Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (for LangChain LLM)
- Access to Gate Pass Management API

### Setup

1. Clone the repository and navigate to the project directory:

```bash
cd strands_agent
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -e .
```

4. Install development dependencies (for testing):

```bash
pip install -e ".[dev]"
```

5. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `API_BASE_URL`: Base URL of the Gate Pass Management API
- `OPENAI_API_KEY`: Your OpenAI API key
- `API_TIMEOUT`: Request timeout in seconds (default: 30)
- `MAX_FILE_SIZE`: Maximum file size for uploads in bytes (default: 5MB)
- `ALLOWED_FILE_FORMATS`: Comma-separated list of allowed file formats

## Usage

### Basic Example

```python
from strands_agent import GatePassAgent
from langchain_openai import ChatOpenAI

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create agent for HR user
agent = GatePassAgent(
    api_base_url="http://localhost:8000",
    llm=llm,
    user_role="HR_User"
)

# Start conversation
response = agent.chat("Create a gate pass for John Doe to visit the warehouse")
print(response)

# Follow-up in same context
response = agent.chat("Make it returnable")
print(response)
```

### Role-Specific Examples

#### HR User

```python
agent = GatePassAgent(api_base_url="...", llm=llm, user_role="HR_User")

# Create a gate pass
agent.chat("Create a gate pass for Jane Smith for equipment pickup, non-returnable")

# List gate passes
agent.chat("Show me all pending gate passes")

# Get details
agent.chat("Get details for gate pass GP-2024-0001")

# Print gate pass
agent.chat("Print gate pass GP-2024-0001")
```

#### Admin User

```python
agent = GatePassAgent(api_base_url="...", llm=llm, user_role="Admin_User")

# List pending approvals
agent.chat("Show me all pending gate passes")

# Approve a gate pass
agent.chat("Approve gate pass GP-2024-0001, my name is Admin Smith")

# Reject a gate pass
agent.chat("Reject gate pass GP-2024-0002, my name is Admin Smith")

# Delete a gate pass
agent.chat("Delete gate pass GP-2024-0003, my name is Admin Smith")
```

#### Gate User

```python
agent = GatePassAgent(api_base_url="...", llm=llm, user_role="Gate_User")

# Scan exit (with photo)
agent.chat("Scan exit for gate pass GP-2024-0001")
# Agent will prompt for photo file

# Scan return
agent.chat("Scan return for gate pass GP-2024-0001")
# Agent will prompt for photo file

# Get gate pass details
agent.chat("Show me details for GP-2024-0001")

# View photos
agent.chat("Show me photos for GP-2024-0001")
```

## Project Structure

```
strands_agent/
├── core/                   # Core agent components
│   ├── __init__.py
│   ├── agent.py           # Main GatePassAgent class
│   ├── api_client.py      # API client with retry logic
│   ├── models.py          # Data models
│   ├── conversation_memory.py  # Conversation memory
│   ├── file_handler.py    # File validation utilities
│   ├── tool_registry.py   # Tool registry with role filtering
│   └── config.py          # Configuration management
├── tools/                  # Tool definitions
│   ├── __init__.py
│   ├── hr_tools.py        # HR operation tools
│   ├── admin_tools.py     # Admin operation tools
│   ├── gate_tools.py      # Gate operation tools
│   └── notification_qr_tools.py  # Notification and QR code tools
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── property/          # Property-based tests
│   └── integration/       # Integration tests
├── pyproject.toml         # Project dependencies
├── .env.example           # Environment configuration template
└── README.md              # This file
```

## Testing

The project uses both unit tests and property-based tests for comprehensive coverage.

### Run All Tests

```bash
pytest
```

### Run Unit Tests Only

```bash
pytest tests/unit/
```

### Run Property-Based Tests Only

```bash
pytest tests/property/ -m property_test
```

### Run with Coverage

```bash
pytest --cov=strands_agent --cov-report=html
```

### Property-Based Testing

The project uses Hypothesis for property-based testing to verify universal properties:

- **Property 1**: Tool Schema Validation - All tools have required fields
- **Property 2**: Tool-to-API Endpoint Mapping - Tool invocations map to correct API calls
- **Property 3**: Role-Based Tool Filtering - Each role only receives authorized tools
- **Property 4**: Role Context Persistence - Role persists throughout session
- **Property 5**: Role-Based Authorization - Unauthorized tool execution is blocked
- **Property 6**: QR Code Data Return - QR code data is returned without modification
- **Property 7**: File Format Validation - Valid formats accepted, invalid rejected
- **Property 8**: File Size Validation - Oversized files rejected
- **Property 9**: Conversation Context Persistence - Context persists during session
- **Property 10**: Multipart Form Data - Files included correctly in requests

## Configuration

The agent uses a centralized configuration management system that loads settings from environment variables with sensible defaults.

### Configuration Module

The configuration module (`core/config.py`) provides:

- **Environment Variable Loading**: Automatically loads from `.env` file in development
- **Environment-Specific Defaults**: Different defaults for development, staging, and production
- **Type Validation**: Ensures all configuration values are valid
- **Global Configuration Instance**: Singleton pattern for consistent configuration access

### Using Configuration in Code

```python
from strands_agent.core import get_config

# Get the global configuration instance
config = get_config()

# Access configuration values
print(config.api_base_url)      # http://localhost:8000
print(config.api_timeout)       # 30
print(config.max_file_size)     # 5242880 (5MB)
print(config.allowed_file_formats)  # ['jpeg', 'jpg', 'png', 'heic']
print(config.environment)       # development
```

### Configuration Values

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_BASE_URL` | Base URL for Gate Pass API | Environment-specific | Yes |
| `API_TIMEOUT` | Request timeout in seconds | 30 | No |
| `MAX_FILE_SIZE` | Max file size in bytes | 5242880 (5MB) | No |
| `ALLOWED_FILE_FORMATS` | Comma-separated file formats | jpeg,jpg,png,heic | No |
| `ENVIRONMENT` | Current environment | development | No |
| `OPENAI_API_KEY` | OpenAI API key for LLM | None | Yes (for LLM) |
| `DEFAULT_USER_ROLE` | Default user role | HR_User | No |

### Environment-Specific Configuration

The agent supports different configurations for development, staging, and production:

**Development** (default):
```bash
ENVIRONMENT=development
# API_BASE_URL defaults to http://localhost:8000
```

**Staging**:
```bash
ENVIRONMENT=staging
# API_BASE_URL defaults to https://staging-api.gatepass.example.com
```

**Production**:
```bash
ENVIRONMENT=production
# API_BASE_URL defaults to https://api.gatepass.example.com
```

You can override the default API URL by explicitly setting `API_BASE_URL`:

```bash
ENVIRONMENT=production
API_BASE_URL=https://custom-api.example.com
```

### File Upload Configuration

Configure file upload restrictions:

```bash
MAX_FILE_SIZE=5242880  # 5MB in bytes
ALLOWED_FILE_FORMATS=jpeg,jpg,png,heic
```

To change limits:

```bash
# Allow 10MB files
MAX_FILE_SIZE=10485760

# Only allow JPEG and PNG
ALLOWED_FILE_FORMATS=jpeg,jpg,png
```

### Configuration Validation

The configuration module validates all values on load:

- `API_BASE_URL` must start with `http://` or `https://`
- `API_TIMEOUT` must be positive
- `MAX_FILE_SIZE` must be positive
- `ALLOWED_FILE_FORMATS` cannot be empty
- `ENVIRONMENT` must be one of: development, staging, production
- `DEFAULT_USER_ROLE` must be one of: HR_User, Admin_User, Gate_User

Invalid configuration will raise a `ValueError` with a descriptive message.

### Testing with Different Configurations

For testing, you can reset and reload configuration:

```python
from strands_agent.core import reset_config, get_config
import os

# Change environment variable
os.environ['API_TIMEOUT'] = '60'

# Reset and reload configuration
reset_config()
config = get_config()

print(config.api_timeout)  # 60
```

## Error Handling

The agent provides user-friendly error messages for common scenarios:

- **404 Not Found**: "The gate pass GP-2024-0001 does not exist. Please check the pass number."
- **403 Forbidden**: "This operation is not allowed for the current gate pass state."
- **422 Validation Error**: "The person_name field is required and cannot be empty."
- **Network Errors**: "Unable to connect to the API. Please check your connection and try again."

## Development

### Adding New Tools

1. Define the tool in the appropriate tools file (e.g., `tools/hr_tools.py`)
2. Register the tool in `tools/registry.py`
3. Add property tests to verify tool schema and behavior
4. Update documentation

### Running Tests During Development

```bash
# Watch mode for continuous testing
pytest --watch

# Run specific test file
pytest tests/unit/test_api_client.py

# Run with verbose output
pytest -v
```

## License

MIT License

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting a pull request.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## Support

For issues and questions, please open an issue on the repository.
