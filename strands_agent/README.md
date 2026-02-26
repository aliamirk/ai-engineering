# Gate Pass AI Agent

A conversational AI agent that provides a natural language interface to the Gate Pass Management API. Built with LangChain, the agent enables users with different roles (HR, Admin, Gate personnel) to perform gate pass operations through natural conversations.

## Quick Start

```bash
# Install
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your API_BASE_URL and OPENAI_API_KEY

# Use
python
>>> from strands_agent import GatePassAgent
>>> from langchain_openai import ChatOpenAI
>>> llm = ChatOpenAI(model="gpt-4", temperature=0)
>>> agent = GatePassAgent(api_base_url="http://localhost:8000", llm=llm, user_role="HR_User")
>>> agent.chat("Create a gate pass for John Doe to pick up equipment, returnable")
```

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Tool Reference](#tool-reference)
- [Error Handling](#error-handling)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [Development](#development)
- [Contributing](#contributing)

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

### Conversation Context

The agent maintains conversation context across multiple turns, allowing for natural multi-turn conversations:

**Context Awareness**:
- The agent remembers the last gate pass mentioned
- You can use pronouns like "it", "that pass", "this one"
- Context persists until explicitly reset or session ends

**Example Flow**:
```python
agent.chat("Create a gate pass for Jane Smith for equipment pickup, returnable")
# Agent creates pass GP-2024-0001

agent.chat("What's the pass number?")
# Agent responds with GP-2024-0001 from context

agent.chat("Print it")
# Agent prints GP-2024-0001 using stored context

agent.chat("Generate a QR code for it")
# Agent generates QR code for GP-2024-0001

agent.chat("Now show me details for GP-2024-0005")
# Context switches to GP-2024-0005

agent.chat("Print this one too")
# Agent prints GP-2024-0005 (new context)
```

**Resetting Context**:
```python
# Clear conversation context for a new conversation
agent.reset_context()

# Now the agent has no memory of previous gate passes
agent.chat("Print it")  # Will ask which gate pass to print
```

**Checking Available Tools**:
```python
# See what operations are available for your role
tools = agent.get_available_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")
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

## API Integration

### Gate Pass Management API

The agent integrates with the Gate Pass Management API, which must be running and accessible. The API provides the following endpoint categories:

**HR Endpoints** (`/hr/*`):
- Create, list, view, and print gate passes
- Requires HR role authentication

**Admin Endpoints** (`/admin/*`):
- Approve, reject, delete, and manage gate passes
- List pending approvals
- Requires Admin role authentication

**Gate Endpoints** (`/gate/*`):
- Scan exits and returns with photo uploads
- View gate pass details and photos
- Requires Gate role authentication

**Notification Endpoints** (`/notifications/*`):
- Retrieve role-specific notifications
- Mark notifications as read
- Available to HR and Admin roles

**QR Code Endpoints** (`/qr/*`):
- Generate QR codes for gate passes
- Available to all roles

### API Authentication

The current implementation assumes the API handles authentication separately. To add authentication to the agent:

```python
from strands_agent.core.api_client import GatePassAPIClient

# Extend the API client with authentication
class AuthenticatedAPIClient(GatePassAPIClient):
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        super().__init__(base_url, timeout)
        self.api_key = api_key
    
    def request(self, method: str, endpoint: str, **kwargs):
        # Add authentication header
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.api_key}'
        kwargs['headers'] = headers
        return super().request(method, endpoint, **kwargs)

# Use authenticated client
from strands_agent.core.agent import GatePassAgent
agent = GatePassAgent(
    api_base_url="http://localhost:8000",
    llm=llm,
    user_role="HR_User",
    api_client=AuthenticatedAPIClient("http://localhost:8000", "your-api-key")
)
```

### Deployment Considerations

**Production Deployment**:

1. **Environment Configuration**:
   ```bash
   ENVIRONMENT=production
   API_BASE_URL=https://api.gatepass.example.com
   API_TIMEOUT=30
   MAX_FILE_SIZE=5242880
   OPENAI_API_KEY=your-production-key
   ```

2. **Security**:
   - Use HTTPS for API communication
   - Store API keys securely (use secrets management)
   - Implement rate limiting on API calls
   - Validate all file uploads
   - Log all operations for audit trails

3. **Scalability**:
   - Use connection pooling for API requests
   - Implement caching for frequently accessed data
   - Consider async operations for file uploads
   - Monitor API response times and error rates

4. **Monitoring**:
   ```python
   import logging
   
   # Configure production logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('gatepass_agent.log'),
           logging.StreamHandler()
       ]
   )
   ```

5. **Error Tracking**:
   - Integrate with error tracking services (Sentry, Rollbar)
   - Log all API errors with context
   - Set up alerts for critical failures
   - Monitor retry rates and success rates

**Docker Deployment**:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY strands_agent/ ./strands_agent/
COPY .env .env

CMD ["python", "your_app.py"]
```

**Kubernetes Deployment**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gatepass-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gatepass-agent
  template:
    metadata:
      labels:
        app: gatepass-agent
    spec:
      containers:
      - name: agent
        image: gatepass-agent:latest
        env:
        - name: API_BASE_URL
          valueFrom:
            configMapKeyRef:
              name: gatepass-config
              key: api_base_url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gatepass-secrets
              key: openai_api_key
```

## Tool Reference

The agent exposes API operations as tools that can be invoked through natural language. Each tool is filtered based on user role to ensure proper authorization.

### HR Tools

#### create_gate_pass

**Description**: Create a new gate pass for a person. Requires person name, description of purpose, and whether the person will return.

**Parameters**:
- `person_name` (string, required): Name of the person receiving the gate pass
- `description` (string, required): Purpose or reason for the gate pass
- `is_returnable` (boolean, required): Whether the person will return to the facility

**API Endpoint**: `POST /hr/gatepass/create`

**Example Usage**:
```python
agent.chat("Create a gate pass for John Doe to pick up equipment, and he will return")
agent.chat("Make a pass for Jane Smith for supplier visit, non-returnable")
```

#### list_gate_passes

**Description**: List all gate passes with optional status filtering. Status can be 'pending', 'approved', 'rejected', 'exited', or 'returned'.

**Parameters**:
- `status` (string, optional): Filter by gate pass status

**API Endpoint**: `GET /hr/gatepass/list`

**Example Usage**:
```python
agent.chat("Show me all gate passes")
agent.chat("List all pending gate passes")
agent.chat("Show me approved gate passes")
```

#### get_gate_pass_details

**Description**: Get detailed information about a specific gate pass using its ID.

**Parameters**:
- `pass_id` (string, required): The gate pass ID (UUID format)

**API Endpoint**: `GET /hr/gatepass/{pass_id}`

**Example Usage**:
```python
agent.chat("Get details for gate pass with ID abc123-def456")
agent.chat("Show me information about pass ID xyz789")
```

#### print_gate_pass

**Description**: Generate a printable version of a gate pass using its pass number.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN

**API Endpoint**: `GET /hr/gatepass/{pass_number}/print`

**Example Usage**:
```python
agent.chat("Print gate pass GP-2024-0001")
agent.chat("Generate printable version of GP-2024-0042")
```

### Admin Tools

#### list_pending_gate_passes

**Description**: List all gate passes that are pending approval.

**Parameters**: None

**API Endpoint**: `GET /admin/gatepass/pending`

**Example Usage**:
```python
agent.chat("Show me all pending gate passes")
agent.chat("What gate passes need approval?")
```

#### get_gate_pass_by_number

**Description**: Get detailed information about a gate pass using its pass number.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN

**API Endpoint**: `GET /admin/gatepass/{pass_number}`

**Example Usage**:
```python
agent.chat("Get details for gate pass GP-2024-0001")
agent.chat("Show me information about GP-2024-0042")
```

#### approve_gate_pass

**Description**: Approve a pending gate pass. Requires the pass number and admin name.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN
- `name` (string, required): Name of the approving admin

**API Endpoint**: `POST /admin/gatepass/{pass_number}/approve`

**Example Usage**:
```python
agent.chat("Approve gate pass GP-2024-0001, my name is Sarah Admin")
agent.chat("Approve GP-2024-0042, I'm John Smith")
```

#### reject_gate_pass

**Description**: Reject a pending gate pass. Requires the pass number and admin name.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN
- `name` (string, required): Name of the rejecting admin

**API Endpoint**: `POST /admin/gatepass/{pass_number}/reject`

**Example Usage**:
```python
agent.chat("Reject gate pass GP-2024-0001, my name is Sarah Admin")
agent.chat("Reject GP-2024-0042, I'm John Smith")
```

#### delete_gate_pass

**Description**: Delete a gate pass. Requires the pass number and admin name.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN
- `name` (string, required): Name of the admin performing deletion

**API Endpoint**: `POST /admin/gatepass/{pass_number}/delete`

**Example Usage**:
```python
agent.chat("Delete gate pass GP-2024-0001, my name is Sarah Admin")
agent.chat("Remove GP-2024-0042, I'm John Smith")
```

#### list_all_gate_passes_admin

**Description**: List all gate passes with optional status filtering.

**Parameters**:
- `status` (string, optional): Filter by gate pass status

**API Endpoint**: `GET /admin/gatepass/list`

**Example Usage**:
```python
agent.chat("Show me all gate passes")
agent.chat("List all approved gate passes")
```

#### print_gate_pass_admin

**Description**: Generate a printable version of a gate pass.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN

**API Endpoint**: `GET /admin/gatepass/{pass_number}/print`

**Example Usage**:
```python
agent.chat("Print gate pass GP-2024-0001")
```

### Gate Tools

#### scan_exit

**Description**: Record a person's exit from the facility. Requires the gate pass number and a photo of the person.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN
- `photo` (file, required): Photo of the person exiting (JPEG, PNG, or HEIC format, max 5MB)

**API Endpoint**: `POST /gate/scan-exit`

**Example Usage**:
```python
agent.chat("Scan exit for gate pass GP-2024-0001")
# Agent will prompt for photo file
agent.chat("Person is leaving with pass GP-2024-0042")
```

#### scan_return

**Description**: Record a person's return to the facility. Requires the gate pass number and a photo of the person.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN
- `photo` (file, required): Photo of the person returning (JPEG, PNG, or HEIC format, max 5MB)

**API Endpoint**: `POST /gate/scan-return`

**Example Usage**:
```python
agent.chat("Scan return for gate pass GP-2024-0001")
# Agent will prompt for photo file
agent.chat("Person returning with pass GP-2024-0042")
```

#### get_gate_pass_by_number_gate

**Description**: Get gate pass details using the pass number.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN

**API Endpoint**: `GET /gate/gatepass/number/{pass_number}`

**Example Usage**:
```python
agent.chat("Show me details for GP-2024-0001")
agent.chat("Look up gate pass GP-2024-0042")
```

#### get_gate_pass_by_id_gate

**Description**: Get gate pass details using the pass ID.

**Parameters**:
- `pass_id` (string, required): The gate pass ID (UUID format)

**API Endpoint**: `GET /gate/gatepass/id/{pass_id}`

**Example Usage**:
```python
agent.chat("Get details for pass ID abc123-def456")
```

#### get_gate_pass_photos

**Description**: Retrieve photos associated with a gate pass.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN

**API Endpoint**: `GET /gate/photos/{pass_number}`

**Example Usage**:
```python
agent.chat("Show me photos for gate pass GP-2024-0001")
agent.chat("Get photos for GP-2024-0042")
```

### Notification Tools

#### get_admin_notifications

**Description**: Retrieve notifications for admin users.

**Parameters**: None

**API Endpoint**: `GET /notifications/admin`

**Role**: Admin_User

**Example Usage**:
```python
agent.chat("Show me my notifications")
agent.chat("Check notifications")
```

#### get_hr_notifications

**Description**: Retrieve notifications for HR users.

**Parameters**: None

**API Endpoint**: `GET /notifications/hr`

**Role**: HR_User

**Example Usage**:
```python
agent.chat("Show me my notifications")
agent.chat("Check notifications")
```

#### mark_notification_read

**Description**: Mark a notification as read.

**Parameters**:
- `notification_id` (string, required): The notification ID

**API Endpoint**: `GET /notifications/mark-read/{notification_id}`

**Role**: Admin_User, HR_User

**Example Usage**:
```python
agent.chat("Mark notification abc123 as read")
agent.chat("I've read notification xyz789")
```

### QR Code Tools

#### get_qr_code

**Description**: Generate a QR code for a gate pass.

**Parameters**:
- `pass_number` (string, required): The gate pass number in format GP-YYYY-NNNN

**API Endpoint**: `GET /qr/{pass_number}`

**Role**: All roles

**Example Usage**:
```python
agent.chat("Generate QR code for gate pass GP-2024-0001")
agent.chat("Get QR code for GP-2024-0042")
```

## Error Handling

The agent provides user-friendly error messages for common scenarios:

### API Errors

- **400 Bad Request**: "The request format is invalid. Please check your input parameters."
- **403 Forbidden**: "This operation is not allowed for the current gate pass state. The gate pass may need to be in a different status."
- **404 Not Found**: "The gate pass GP-2024-0001 does not exist. Please check the pass number."
- **422 Validation Error**: "The person_name field is required and cannot be empty." (Specific field mentioned)
- **500 Internal Server Error**: "The server encountered an error. Please try again later."

### Network Errors

- **Connection Timeout**: "Unable to connect to the API. The request timed out. Please check your connection and try again."
- **Connection Refused**: "Unable to connect to the API server. Please ensure the API is running."
- **DNS Resolution Failure**: "Unable to resolve the API URL. Please check the API_BASE_URL configuration."

### Client Errors

- **Invalid File Format**: "The photo file must be in JPEG, PNG, or HEIC format. Please provide a valid image file."
- **File Too Large**: "The photo file exceeds the maximum size limit of 5MB. Please provide a smaller file."
- **Missing Required Parameter**: "The [parameter_name] is required for this operation. Please provide it."
- **Invalid Role**: "This operation requires [required_role] role. Your current role is [current_role]."

### Error Recovery

The agent implements automatic retry logic for transient network failures:
- **Retry Strategy**: Exponential backoff with 3 attempts (2s, 4s, 8s delays)
- **Retryable Errors**: Connection timeouts, temporary network failures
- **Non-Retryable Errors**: 400, 403, 404, 422 status codes (require user correction)

After maximum retries, the agent provides guidance:
```
"Unable to complete the operation after 3 attempts. Please check your network connection and try again manually."
```

## Troubleshooting

### Common Issues

#### "OPENAI_API_KEY environment variable is not set"

**Cause**: The OpenAI API key is not configured.

**Solution**:
```bash
# Set in environment
export OPENAI_API_KEY='your-api-key-here'

# Or add to .env file
echo "OPENAI_API_KEY=your-api-key-here" >> .env
```

#### "Unable to connect to the API"

**Cause**: The Gate Pass Management API is not reachable.

**Solutions**:
1. Ensure the API server is running
2. Check the `API_BASE_URL` in your `.env` file
3. Verify network connectivity
4. Check firewall settings

```bash
# Test API connectivity
curl http://localhost:8000/health

# Check .env configuration
cat .env | grep API_BASE_URL
```

#### "Invalid user_role"

**Cause**: The user role provided is not recognized.

**Solution**: User role must be one of: `HR_User`, `Admin_User`, `Gate_User` (case-sensitive).

```python
# Correct
agent = GatePassAgent(api_base_url="...", llm=llm, user_role="HR_User")

# Incorrect
agent = GatePassAgent(api_base_url="...", llm=llm, user_role="hr_user")  # Wrong case
agent = GatePassAgent(api_base_url="...", llm=llm, user_role="HR")  # Wrong format
```

#### "The photo file must be in JPEG, PNG, or HEIC format"

**Cause**: Attempting to upload a file with an unsupported format.

**Solution**: Convert the image to a supported format (JPEG, PNG, or HEIC) before uploading.

```bash
# Convert using ImageMagick
convert input.bmp output.jpg

# Or use Python
from PIL import Image
img = Image.open('input.bmp')
img.save('output.jpg', 'JPEG')
```

#### "The photo file exceeds the maximum size limit"

**Cause**: The uploaded file is larger than the configured maximum (default 5MB).

**Solutions**:
1. Compress the image before uploading
2. Increase the `MAX_FILE_SIZE` limit in configuration (if appropriate)

```bash
# Compress using ImageMagick
convert input.jpg -quality 85 -resize 1920x1920\> output.jpg

# Or increase limit in .env
MAX_FILE_SIZE=10485760  # 10MB
```

#### Agent doesn't understand my request

**Cause**: The request may be ambiguous or missing key information.

**Solutions**:
1. Include the pass number in GP-YYYY-NNNN format
2. Specify the operation clearly (create, approve, list, etc.)
3. Provide required parameters explicitly

```python
# Vague
agent.chat("Do something with the pass")

# Clear
agent.chat("Approve gate pass GP-2024-0001, my name is Sarah Admin")
```

#### "This operation requires [role] role"

**Cause**: Attempting to perform an operation not authorized for your current role.

**Solution**: Use an agent instance with the appropriate role, or contact an administrator.

```python
# HR user cannot approve
hr_agent = GatePassAgent(api_base_url="...", llm=llm, user_role="HR_User")
hr_agent.chat("Approve GP-2024-0001")  # Will fail

# Use Admin agent instead
admin_agent = GatePassAgent(api_base_url="...", llm=llm, user_role="Admin_User")
admin_agent.chat("Approve GP-2024-0001, my name is Sarah Admin")  # Will succeed
```

#### Tests are failing

**Cause**: Various reasons including missing dependencies, configuration issues, or code changes.

**Solutions**:

```bash
# Reinstall dependencies
pip install -e ".[dev]"

# Clear pytest cache
pytest --cache-clear

# Run tests with verbose output to see details
pytest -v

# Run specific failing test
pytest tests/unit/test_api_client.py::test_specific_function -v

# Check test coverage
pytest --cov=strands_agent --cov-report=term-missing
```

#### Property-based tests are slow

**Cause**: Hypothesis runs 100+ iterations per test by default.

**Solutions**:

```bash
# Run with fewer iterations during development
pytest tests/property/ --hypothesis-max-examples=10

# Or set in pytest.ini
[tool.pytest.ini_options]
hypothesis_max_examples = 10
```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Create agent
agent = GatePassAgent(api_base_url="...", llm=llm, user_role="HR_User")

# Now all API calls and agent decisions will be logged
agent.chat("Create a gate pass for John Doe")
```

### Getting Help

If you encounter issues not covered here:

1. Check the [EXAMPLES.md](EXAMPLES.md) for usage patterns
2. Review the [design document](.kiro/specs/gatepass-ai-agent/design.md)
3. Check the [requirements document](.kiro/specs/gatepass-ai-agent/requirements.md)
4. Open an issue on the repository with:
   - Error message and stack trace
   - Steps to reproduce
   - Environment details (Python version, OS, etc.)
   - Configuration (with sensitive data removed)

## Development

### Adding New Tools

1. Define the tool in the appropriate tools file (e.g., `tools/hr_tools.py`)
2. Register the tool in `core/tool_registry.py`
3. Add property tests to verify tool schema and behavior
4. Update this README with tool documentation
5. Add examples to EXAMPLES.md

**Example: Adding a new HR tool**

```python
# In tools/hr_tools.py
def create_new_tool():
    return {
        "name": "new_tool_name",
        "description": "Clear description for the LLM",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Parameter description"},
                "param2": {"type": "boolean", "description": "Parameter description"}
            },
            "required": ["param1"]
        },
        "required_role": "HR_User",
        "api_endpoint": "/hr/new-endpoint",
        "http_method": "POST"
    }

# In core/tool_registry.py
from tools.hr_tools import create_new_tool

class ToolRegistry:
    def __init__(self):
        self.tools = {
            # ... existing tools ...
            "new_tool_name": create_new_tool(),
        }
```

### Running Tests During Development

```bash
# Watch mode for continuous testing (requires pytest-watch)
ptw

# Run specific test file
pytest tests/unit/test_api_client.py

# Run with verbose output
pytest -v

# Run only property tests
pytest tests/property/ -m property_test

# Run with coverage
pytest --cov=strands_agent --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Code Quality

```bash
# Format code with black
black strands_agent/

# Lint with flake8
flake8 strands_agent/

# Type checking with mypy
mypy strands_agent/

# Run all quality checks
black strands_agent/ && flake8 strands_agent/ && mypy strands_agent/ && pytest
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
