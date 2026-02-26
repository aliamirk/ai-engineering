# Gate Pass AI Agent - API Documentation

## Overview

This document provides comprehensive API documentation for developers who want to understand the internal architecture and extend the Gate Pass AI Agent. The agent provides a natural language interface to the Gate Pass Management API using a tool-based architecture with role-based access control.

## Table of Contents

- [Core Classes](#core-classes)
  - [GatePassAgent](#gatepassagent)
  - [ToolRegistry](#toolregistry)
  - [GatePassAPIClient](#gatepassapiclient)
  - [ConversationMemory](#conversationmemory)
- [Data Models](#data-models)
- [Tool Definitions](#tool-definitions)
- [File Handling](#file-handling)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)

---

## Core Classes

### GatePassAgent

The main orchestrator class that integrates with LangChain to provide a conversational interface for gate pass operations.

**Module:** `strands_agent.core.agent`

#### Class Definition

```python
class GatePassAgent:
    """Conversational AI agent for Gate Pass Management API."""
```

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `api_client` | `GatePassAPIClient` | HTTP client for Gate Pass API |
| `tool_registry` | `ToolRegistry` | Registry of all available tools |
| `user_role` | `str` | Current user's role (HR_User, Admin_User, or Gate_User) |
| `conversation_memory` | `ConversationMemory` | Memory for maintaining conversation context |
| `llm` | `BaseChatModel` | LangChain language model for processing user input |
| `tools` | `List[StructuredTool]` | List of LangChain tools available to this agent |
| `chat_history` | `List[Any]` | List of conversation messages |


#### Constructor

```python
def __init__(
    self,
    api_base_url: str,
    llm: BaseChatModel,
    user_role: str
)
```

**Parameters:**
- `api_base_url` (str): Base URL for the Gate Pass Management API
- `llm` (BaseChatModel): LangChain language model instance (e.g., ChatOpenAI)
- `user_role` (str): User's role - must be one of: `HR_User`, `Admin_User`, `Gate_User`

**Raises:**
- `ValueError`: If user_role is not one of the valid roles

**Example:**
```python
from langchain_openai import ChatOpenAI
from strands_agent.core.agent import GatePassAgent

llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = GatePassAgent(
    api_base_url="https://api.example.com",
    llm=llm,
    user_role="HR_User"
)
```

#### Methods

##### `chat(user_input: str) -> str`

Process user input and return agent response.

**Parameters:**
- `user_input` (str): Natural language input from the user

**Returns:**
- `str`: Agent's natural language response

**Description:**
This method:
1. Processes natural language input
2. Uses LLM to identify intent and select appropriate tools
3. Extracts parameters from natural language
4. Asks clarifying questions if parameters are missing
5. Updates conversation context after each interaction

**Example:**
```python
response = agent.chat("Create a gate pass for John Doe to visit the warehouse")
print(response)
```

##### `reset_context() -> None`

Clear conversation context for a new session.

**Description:**
This method resets both the conversation memory and chat history, effectively starting a fresh conversation.

**Example:**
```python
agent.reset_context()
```

##### `get_available_tools() -> List[str]`

Get list of tool names available for the current user role.

**Returns:**
- `List[str]`: List of tool names that the current user can access

**Example:**
```python
tools = agent.get_available_tools()
print(f"Available tools: {', '.join(tools)}")
```

---

### ToolRegistry

Central registry for managing and filtering tools by user role.

**Module:** `strands_agent.core.tool_registry`

#### Class Definition

```python
class ToolRegistry:
    """Central registry for all gate pass management tools."""
```

#### Constructor

```python
def __init__(self, api_client: GatePassAPIClient)
```

**Parameters:**
- `api_client` (GatePassAPIClient): GatePassAPIClient instance for making API requests

**Example:**
```python
from strands_agent.core.api_client import GatePassAPIClient
from strands_agent.core.tool_registry import ToolRegistry

api_client = GatePassAPIClient(base_url="https://api.example.com")
registry = ToolRegistry(api_client=api_client)
```

#### Methods

##### `get_tools_for_role(user_role: str) -> List[Any]`

Filter tools by user role.

**Parameters:**
- `user_role` (str): The user's role (HR_User, Admin_User, or Gate_User)

**Returns:**
- `List[Any]`: List of tool instances authorized for the given role

**Description:**
Returns only the tools that the specified role is authorized to use. Tools can have:
- A specific role requirement (e.g., "HR_User")
- Multiple role requirements (e.g., ["HR_User", "Admin_User"])
- Universal access (role = "All")

**Example:**
```python
hr_tools = registry.get_tools_for_role("HR_User")
print(f"HR has access to {len(hr_tools)} tools")
```

##### `get_tool(tool_name: str) -> Optional[Any]`

Retrieve a specific tool by name.

**Parameters:**
- `tool_name` (str): The name of the tool to retrieve

**Returns:**
- `Optional[Any]`: The tool instance if found, None otherwise

**Example:**
```python
create_tool = registry.get_tool("create_gate_pass")
if create_tool:
    print(f"Found tool: {create_tool.description}")
```

##### `get_all_tools() -> Dict[str, Any]`

Get all registered tools.

**Returns:**
- `Dict[str, Any]`: Dictionary mapping tool names to tool instances

**Example:**
```python
all_tools = registry.get_all_tools()
print(f"Total tools registered: {len(all_tools)}")
```

##### `check_authorization(tool_name: str, user_role: str) -> Tuple[bool, Optional[str]]`

Verify user role before tool execution.

**Parameters:**
- `tool_name` (str): The name of the tool to check authorization for
- `user_role` (str): The user's role (HR_User, Admin_User, or Gate_User)

**Returns:**
- `Tuple[bool, Optional[str]]`: A tuple of (is_authorized, error_message)
  - `is_authorized`: True if the user is authorized, False otherwise
  - `error_message`: None if authorized, error message string if not authorized

**Description:**
This method checks if a user's role is authorized to use a specific tool before allowing execution. If unauthorized, it returns an error without making any API calls.

**Example:**
```python
is_authorized, error = registry.check_authorization("create_gate_pass", "Admin_User")
if not is_authorized:
    print(f"Authorization failed: {error}")
```

---

### GatePassAPIClient

HTTP client for Gate Pass Management API with retry logic and error handling.

**Module:** `strands_agent.core.api_client`

#### Class Definition

```python
class GatePassAPIClient:
    """HTTP client for Gate Pass Management API with retry logic and error handling."""
```

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `base_url` | `str` | Base URL for the Gate Pass API |
| `timeout` | `int` | Request timeout in seconds |
| `max_retries` | `int` | Maximum number of retry attempts (default: 3) |
| `retry_delays` | `List[int]` | Exponential backoff delays in seconds [2, 4, 8] |

#### Constructor

```python
def __init__(self, base_url: str, timeout: int = 30)
```

**Parameters:**
- `base_url` (str): Base URL for the Gate Pass API (e.g., "https://api.example.com")
- `timeout` (int): Request timeout in seconds (default: 30)

**Example:**
```python
from strands_agent.core.api_client import GatePassAPIClient

client = GatePassAPIClient(
    base_url="https://api.example.com",
    timeout=30
)
```

#### Methods

##### `request(method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None, files: Optional[Dict] = None) -> APIResponse`

Execute HTTP request with exponential backoff retry logic.

**Parameters:**
- `method` (str): HTTP method (GET or POST)
- `endpoint` (str): API endpoint path (e.g., "/hr/gatepass/create")
- `params` (Optional[Dict]): Query parameters for GET requests
- `json_data` (Optional[Dict]): JSON body for POST requests
- `files` (Optional[Dict]): Files for multipart form data uploads

**Returns:**
- `APIResponse`: APIResponse object with success status, status code, data, and error

**Description:**
Executes HTTP requests with automatic retry logic using exponential backoff (2s, 4s, 8s delays). Handles timeouts, connection errors, and API errors gracefully.

**Example:**
```python
# GET request
response = client.request(
    method="GET",
    endpoint="/hr/gatepass/list",
    params={"status": "pending"}
)

# POST request with JSON
response = client.request(
    method="POST",
    endpoint="/hr/gatepass/create",
    json_data={
        "person_name": "John Doe",
        "description": "Warehouse visit",
        "is_returnable": True
    }
)

# POST request with file upload
response = client.request(
    method="POST",
    endpoint="/gate/scan-exit",
    params={"pass_number": "GP-2024-0001"},
    files={"photo": ("photo.jpg", file_bytes, "image/jpeg")}
)
```

##### `handle_error(status_code: int, response_body: Optional[Dict] = None) -> str`

Convert HTTP status codes to user-friendly error messages.

**Parameters:**
- `status_code` (int): HTTP status code from the API response
- `response_body` (Optional[Dict]): Optional response body containing additional error details

**Returns:**
- `str`: User-friendly error message with context-specific guidance

**Supported Status Codes:**
- `400`: Bad Request - Invalid request format or parameters
- `403`: Forbidden - Operation not permitted for current gate pass state
- `404`: Not Found - Gate pass or resource does not exist
- `422`: Unprocessable Entity - Validation errors on input data
- `500`: Internal Server Error - Server-side error

**Example:**
```python
error_msg = client.handle_error(404, {"detail": "Gate pass not found"})
print(error_msg)
# Output: "Gate pass or resource does not exist. Details: Gate pass not found..."
```

---

### ConversationMemory

Manages conversation context to enable natural follow-up interactions.

**Module:** `strands_agent.core.conversation_memory`

#### Class Definition

```python
class ConversationMemory:
    """Manages conversation context to enable natural follow-up interactions."""
```

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_context` | `ConversationContext` | Internal conversation context storage |

#### Constructor

```python
def __init__(self)
```

**Description:**
Initializes empty conversation context.

**Example:**
```python
from strands_agent.core.conversation_memory import ConversationMemory

memory = ConversationMemory()
```

#### Methods

##### `store_pass_reference(pass_number: Optional[str] = None, pass_id: Optional[str] = None) -> None`

Save pass_number and pass_id to conversation context.

**Parameters:**
- `pass_number` (Optional[str]): The gate pass number (format: GP-YYYY-NNNN)
- `pass_id` (Optional[str]): The gate pass ID

**Example:**
```python
memory.store_pass_reference(pass_number="GP-2024-0001")
```

##### `get_current_pass() -> Dict[str, Optional[str]]`

Retrieve stored pass information.

**Returns:**
- `Dict[str, Optional[str]]`: Dictionary containing current_pass_number and current_pass_id

**Example:**
```python
current = memory.get_current_pass()
print(f"Current pass: {current['pass_number']}")
```

##### `update_context(last_operation: Optional[str] = None, pending_parameters: Optional[Dict] = None) -> None`

Update conversation variables.

**Parameters:**
- `last_operation` (Optional[str]): The last operation performed
- `pending_parameters` (Optional[Dict]): Dictionary of parameters being collected

**Example:**
```python
memory.update_context(
    last_operation="create_gate_pass",
    pending_parameters={"person_name": "John Doe"}
)
```

##### `clear() -> None`

Reset conversation context to empty state.

**Example:**
```python
memory.clear()
```

---

## Data Models

All data models are defined in `strands_agent.core.models`.

### GatePass

Gate pass data model representing a digital authorization document.

```python
@dataclass
class GatePass:
    id: str
    pass_number: str  # Format: GP-YYYY-NNNN
    person_name: str
    description: str
    is_returnable: bool
    status: str  # pending, approved, rejected, exited, returned
    created_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    exit_time: Optional[datetime] = None
    return_time: Optional[datetime] = None
    qr_code_url: Optional[str] = None
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier |
| `pass_number` | `str` | Pass number in format GP-YYYY-NNNN |
| `person_name` | `str` | Name of the person |
| `description` | `str` | Purpose of the pass |
| `is_returnable` | `bool` | Whether person will return |
| `status` | `str` | Status: pending, approved, rejected, exited, returned |
| `created_at` | `datetime` | Creation timestamp |
| `approved_at` | `Optional[datetime]` | Approval timestamp |
| `approved_by` | `Optional[str]` | Name of approver |
| `exit_time` | `Optional[datetime]` | Exit timestamp |
| `return_time` | `Optional[datetime]` | Return timestamp |
| `qr_code_url` | `Optional[str]` | URL to QR code image |

### Notification

Notification data model for gate pass events.

```python
@dataclass
class Notification:
    id: str
    message: str
    type: str
    created_at: datetime
    is_read: bool
    related_pass_id: Optional[str] = None
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier |
| `message` | `str` | Notification message |
| `type` | `str` | Notification type |
| `created_at` | `datetime` | Creation timestamp |
| `is_read` | `bool` | Read status |
| `related_pass_id` | `Optional[str]` | Associated gate pass ID |

### APIResponse

Structured API response object.

```python
@dataclass
class APIResponse:
    success: bool
    status_code: int
    data: Optional[Any] = None
    error: Optional[str] = None
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether request succeeded |
| `status_code` | `int` | HTTP status code |
| `data` | `Optional[Any]` | Response data |
| `error` | `Optional[str]` | Error message if failed |

### ConversationContext

Conversation context for maintaining state across interactions.

```python
@dataclass
class ConversationContext:
    current_pass_number: Optional[str] = None
    current_pass_id: Optional[str] = None
    last_operation: Optional[str] = None
    pending_parameters: Dict[str, Any] = field(default_factory=dict)
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `current_pass_number` | `Optional[str]` | Currently referenced pass number |
| `current_pass_id` | `Optional[str]` | Currently referenced pass ID |
| `last_operation` | `Optional[str]` | Last performed operation |
| `pending_parameters` | `Dict[str, Any]` | Parameters being collected |

---

## Tool Definitions

Tools are organized by user role and defined in the `strands_agent.tools` module.

### Tool Structure

All tools follow a common structure:

```python
class ToolDefinition:
    name: str                    # Unique tool identifier
    description: str             # Natural language description for LLM
    parameters: Dict[str, Any]   # JSON Schema for parameters
    required_role: str           # Role required to access this tool
    api_endpoint: str            # API endpoint to call
    http_method: str             # HTTP method (GET, POST)
    
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters."""
        
    def format_response(self, response: APIResponse) -> str:
        """Format API response into natural language."""
```

### HR Tools

**Module:** `strands_agent.tools.hr_tools`

| Tool Name | Description | Parameters | Endpoint |
|-----------|-------------|------------|----------|
| `create_gate_pass` | Create a new gate pass | person_name (str), description (str), is_returnable (bool) | POST /hr/gatepass/create |
| `list_gate_passes` | List gate passes with optional status filter | status (str, optional) | GET /hr/gatepass/list |
| `get_gate_pass_details` | Get gate pass details by ID | pass_id (str) | GET /hr/gatepass/{pass_id} |
| `print_gate_pass` | Generate printable gate pass | pass_number (str) | GET /hr/gatepass/{pass_number}/print |

**Example:**
```python
from strands_agent.tools.hr_tools import get_hr_tools

hr_tools = get_hr_tools(api_client)
for tool in hr_tools:
    print(f"{tool.name}: {tool.description}")
```

### Admin Tools

**Module:** `strands_agent.tools.admin_tools`

| Tool Name | Description | Parameters | Endpoint |
|-----------|-------------|------------|----------|
| `list_pending_gate_passes` | List pending gate passes | None | GET /admin/gatepass/pending |
| `get_gate_pass_by_number` | Get gate pass by number | pass_number (str) | GET /admin/gatepass/{pass_number} |
| `approve_gate_pass` | Approve a gate pass | pass_number (str), name (str) | POST /admin/gatepass/{pass_number}/approve |
| `reject_gate_pass` | Reject a gate pass | pass_number (str), name (str) | POST /admin/gatepass/{pass_number}/reject |
| `delete_gate_pass` | Delete a gate pass | pass_number (str), name (str) | POST /admin/gatepass/{pass_number}/delete |
| `list_all_gate_passes_admin` | List all gate passes | status (str, optional) | GET /admin/gatepass/list |
| `print_gate_pass_admin` | Generate printable gate pass | pass_number (str) | GET /admin/gatepass/{pass_number}/print |

**Example:**
```python
from strands_agent.tools.admin_tools import get_admin_tools

admin_tools = get_admin_tools(api_client)
```

### Gate Tools

**Module:** `strands_agent.tools.gate_tools`

| Tool Name | Description | Parameters | Endpoint |
|-----------|-------------|------------|----------|
| `scan_exit` | Record person's exit | pass_number (str), photo (file) | POST /gate/scan-exit |
| `scan_return` | Record person's return | pass_number (str), photo (file) | POST /gate/scan-return |
| `get_gate_pass_by_number_gate` | Get gate pass by number | pass_number (str) | GET /gate/gatepass/number/{pass_number} |
| `get_gate_pass_by_id_gate` | Get gate pass by ID | pass_id (str) | GET /gate/gatepass/id/{pass_id} |
| `get_gate_pass_photos` | Get gate pass photos | pass_number (str) | GET /gate/photos/{pass_number} |

**Example:**
```python
from strands_agent.tools.gate_tools import get_gate_tools

gate_tools = get_gate_tools(api_client)
```

### Notification and QR Code Tools

**Module:** `strands_agent.tools.notification_qr_tools`

| Tool Name | Description | Parameters | Required Role | Endpoint |
|-----------|-------------|------------|---------------|----------|
| `get_admin_notifications` | Get admin notifications | None | Admin_User | GET /notifications/admin |
| `get_hr_notifications` | Get HR notifications | None | HR_User | GET /notifications/hr |
| `mark_notification_read` | Mark notification as read | notification_id (str) | Admin_User, HR_User | GET /notifications/mark-read/{notification_id} |
| `get_qr_code` | Generate QR code | pass_number (str) | All | GET /qr/{pass_number} |

**Example:**
```python
from strands_agent.tools.notification_qr_tools import (
    get_notification_tools,
    get_qr_code_tools
)

notification_tools = get_notification_tools(api_client)
qr_tools = get_qr_code_tools(api_client)
```

---

## File Handling

**Module:** `strands_agent.core.file_handler`

### Functions

#### `validate_file_format(file_path: str, allowed_formats: Optional[List[str]] = None) -> bool`

Validate that a file is in an allowed image format.

**Parameters:**
- `file_path` (str): Path to the file to validate
- `allowed_formats` (Optional[List[str]]): List of allowed file extensions (default: ['jpeg', 'jpg', 'png', 'heic'])

**Returns:**
- `bool`: True if file format is valid

**Raises:**
- `FileValidationError`: If file format is not allowed

**Example:**
```python
from strands_agent.core.file_handler import validate_file_format

try:
    validate_file_format("photo.jpg")
    print("File format is valid")
except FileValidationError as e:
    print(f"Validation failed: {e}")
```

#### `validate_file_size(file_path: str, max_size_bytes: int = 5242880) -> bool`

Validate that a file does not exceed the maximum size limit.

**Parameters:**
- `file_path` (str): Path to the file to validate
- `max_size_bytes` (int): Maximum allowed file size in bytes (default: 5MB = 5242880 bytes)

**Returns:**
- `bool`: True if file size is valid

**Raises:**
- `FileValidationError`: If file size exceeds the limit

**Example:**
```python
from strands_agent.core.file_handler import validate_file_size

try:
    validate_file_size("photo.jpg", max_size_bytes=5242880)
    print("File size is valid")
except FileValidationError as e:
    print(f"Validation failed: {e}")
```

#### `prepare_multipart_data(pass_number: str, file_path: str, max_size_bytes: int = 5242880, allowed_formats: Optional[List[str]] = None) -> Tuple[Dict[str, str], Dict[str, Tuple[str, bytes, str]]]`

Prepare multipart form data for gate scan API requests.

**Parameters:**
- `pass_number` (str): The gate pass number
- `file_path` (str): Path to the photo file
- `max_size_bytes` (int): Maximum allowed file size in bytes (default: 5MB)
- `allowed_formats` (Optional[List[str]]): List of allowed file extensions

**Returns:**
- `Tuple[Dict[str, str], Dict[str, Tuple]]`: Tuple of (data_dict, files_dict) where:
  - data_dict contains the pass_number field
  - files_dict contains the photo file in format: {'photo': (filename, file_bytes, content_type)}

**Raises:**
- `FileValidationError`: If file validation fails

**Example:**
```python
from strands_agent.core.file_handler import prepare_multipart_data

try:
    data, files = prepare_multipart_data("GP-2024-0001", "photo.jpg")
    # Use data and files in API request
    response = api_client.request(
        method="POST",
        endpoint="/gate/scan-exit",
        params=data,
        files=files
    )
except FileValidationError as e:
    print(f"File preparation failed: {e}")
```

### FileValidationError

Exception raised when file validation fails.

```python
class FileValidationError(Exception):
    """Exception raised when file validation fails."""
```

---

## Error Handling

The agent provides comprehensive error handling at multiple levels:

### API Error Codes

| Status Code | Error Type | Description | User Guidance |
|-------------|------------|-------------|---------------|
| 400 | Bad Request | Invalid request format or parameters | Check that all required fields are provided with valid values |
| 403 | Forbidden | Operation not permitted for current gate pass state | Gate pass may need to be in a different status (e.g., approved, pending) |
| 404 | Not Found | Gate pass or resource does not exist | Verify the gate pass number or ID is correct |
| 422 | Unprocessable Entity | Validation errors on input data | Check the format and constraints for each field |
| 500 | Internal Server Error | Server-side error | Try again later; contact support if problem persists |

### Network Errors

| Error Type | Description | Retry Behavior |
|------------|-------------|----------------|
| Timeout | Request timeout | Automatic retry with exponential backoff (2s, 4s, 8s) |
| Connection Error | API server unreachable | Automatic retry with exponential backoff (2s, 4s, 8s) |
| DNS Resolution | Invalid API base URL | No retry; immediate failure |

### Client Errors

| Error Type | Description | Handling |
|------------|-------------|----------|
| Invalid File Format | Photo file not in JPEG, PNG, or HEIC format | Immediate validation failure before API call |
| File Too Large | Photo file exceeds size limit | Immediate validation failure before API call |
| Missing Required Parameter | Tool invoked without required parameter | LLM asks clarifying questions to collect parameter |
| Invalid Role | User role not recognized | Immediate failure during agent initialization |
| Unauthorized Tool Access | User attempts to use tool not authorized for their role | Blocked before API call with error message |

### Error Response Format

All errors are formatted into user-friendly messages by the agent:

```python
# Example error handling in tool execution
try:
    result = tool.execute(**params)
except FileValidationError as e:
    return f"File validation failed: {str(e)}"
except Exception as e:
    return f"Error executing tool: {str(e)}"
```

---

## Usage Examples

### Basic Agent Setup

```python
import os
from langchain_openai import ChatOpenAI
from strands_agent.core.agent import GatePassAgent

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Create agent for HR user
agent = GatePassAgent(
    api_base_url="https://api.example.com",
    llm=llm,
    user_role="HR_User"
)

# Start conversation
response = agent.chat("Create a gate pass for John Doe to visit the warehouse")
print(response)
```

### Multi-Turn Conversation with Context

```python
# First turn - create gate pass
response1 = agent.chat("Create a gate pass for Jane Smith")
print(response1)
# Agent asks: "What is the purpose of the gate pass?"

# Second turn - provide missing parameter
response2 = agent.chat("She needs to visit the data center")
print(response2)
# Agent asks: "Will Jane Smith be returning?"

# Third turn - complete the request
response3 = agent.chat("Yes, she will return")
print(response3)
# Agent creates the gate pass and returns: "Gate pass created successfully! Pass Number: GP-2024-0001..."

# Fourth turn - use context for follow-up
response4 = agent.chat("Print that pass")
print(response4)
# Agent uses GP-2024-0001 from context to print the gate pass
```

### Role-Based Access

```python
# HR User - can create gate passes
hr_agent = GatePassAgent(
    api_base_url="https://api.example.com",
    llm=llm,
    user_role="HR_User"
)

response = hr_agent.chat("Create a gate pass for Bob")
# Success - HR users can create gate passes

# Admin User - can approve gate passes
admin_agent = GatePassAgent(
    api_base_url="https://api.example.com",
    llm=llm,
    user_role="Admin_User"
)

response = admin_agent.chat("Show me pending gate passes")
# Success - Admin users can view pending passes

response = admin_agent.chat("Approve GP-2024-0001")
# Agent asks: "What is your name?" (required for approval)

response = admin_agent.chat("My name is Alice Johnson")
# Success - Gate pass approved by Alice Johnson
```

### Gate User with File Upload

```python
# Gate User - can scan exits and returns
gate_agent = GatePassAgent(
    api_base_url="https://api.example.com",
    llm=llm,
    user_role="Gate_User"
)

# Note: File upload requires special handling
# The agent expects file paths to be provided in the conversation
response = gate_agent.chat("Scan exit for GP-2024-0001 with photo at /path/to/photo.jpg")
# Agent processes the scan with the provided photo
```

### Direct API Client Usage

```python
from strands_agent.core.api_client import GatePassAPIClient

# Initialize client
client = GatePassAPIClient(base_url="https://api.example.com")

# Make a GET request
response = client.request(
    method="GET",
    endpoint="/hr/gatepass/list",
    params={"status": "pending"}
)

if response.success:
    print(f"Found {len(response.data)} gate passes")
else:
    print(f"Error: {response.error}")

# Make a POST request
response = client.request(
    method="POST",
    endpoint="/hr/gatepass/create",
    json_data={
        "person_name": "John Doe",
        "description": "Warehouse visit",
        "is_returnable": True
    }
)

if response.success:
    print(f"Created gate pass: {response.data['pass_number']}")
```

### Tool Registry Usage

```python
from strands_agent.core.api_client import GatePassAPIClient
from strands_agent.core.tool_registry import ToolRegistry

# Initialize
client = GatePassAPIClient(base_url="https://api.example.com")
registry = ToolRegistry(api_client=client)

# Get tools for a specific role
hr_tools = registry.get_tools_for_role("HR_User")
print(f"HR users have access to {len(hr_tools)} tools:")
for tool in hr_tools:
    print(f"  - {tool.name}: {tool.description}")

# Check authorization
is_authorized, error = registry.check_authorization("create_gate_pass", "Admin_User")
if not is_authorized:
    print(f"Authorization failed: {error}")
    # Output: "Access denied. Tool 'create_gate_pass' requires role 'HR_User'. Your role: Admin_User."

# Get a specific tool
tool = registry.get_tool("create_gate_pass")
if tool:
    # Execute the tool directly
    result = tool.execute(
        person_name="John Doe",
        description="Warehouse visit",
        is_returnable=True
    )
    print(result)
```

### File Handling

```python
from strands_agent.core.file_handler import (
    validate_file_format,
    validate_file_size,
    prepare_multipart_data,
    FileValidationError
)

# Validate file format
try:
    validate_file_format("photo.jpg")
    print("File format is valid")
except FileValidationError as e:
    print(f"Invalid format: {e}")

# Validate file size
try:
    validate_file_size("photo.jpg", max_size_bytes=5242880)  # 5MB
    print("File size is valid")
except FileValidationError as e:
    print(f"File too large: {e}")

# Prepare multipart data for upload
try:
    data, files = prepare_multipart_data(
        pass_number="GP-2024-0001",
        file_path="photo.jpg"
    )
    
    # Use in API request
    client = GatePassAPIClient(base_url="https://api.example.com")
    response = client.request(
        method="POST",
        endpoint="/gate/scan-exit",
        params=data,
        files=files
    )
    
    if response.success:
        print("Exit scan recorded successfully")
except FileValidationError as e:
    print(f"File validation failed: {e}")
```

### Conversation Memory

```python
from strands_agent.core.conversation_memory import ConversationMemory

# Initialize memory
memory = ConversationMemory()

# Store pass reference
memory.store_pass_reference(pass_number="GP-2024-0001")

# Retrieve current pass
current = memory.get_current_pass()
print(f"Current pass: {current['pass_number']}")  # Output: GP-2024-0001

# Update context
memory.update_context(
    last_operation="create_gate_pass",
    pending_parameters={"person_name": "John Doe"}
)

# Clear context for new session
memory.clear()
```

### Error Handling Example

```python
from strands_agent.core.agent import GatePassAgent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = GatePassAgent(
    api_base_url="https://api.example.com",
    llm=llm,
    user_role="HR_User"
)

# The agent handles errors gracefully
response = agent.chat("Show me details for GP-9999-9999")
# If gate pass doesn't exist, agent returns:
# "Failed to retrieve gate pass details: Gate pass or resource does not exist..."

# Invalid role during initialization
try:
    invalid_agent = GatePassAgent(
        api_base_url="https://api.example.com",
        llm=llm,
        user_role="InvalidRole"
    )
except ValueError as e:
    print(f"Error: {e}")
    # Output: "Invalid user_role 'InvalidRole'. Must be one of: HR_User, Admin_User, Gate_User"
```

---

## Extending the Agent

### Adding a New Tool

To add a new tool to the agent:

1. **Create a tool definition class** in the appropriate module (hr_tools.py, admin_tools.py, etc.):

```python
class MyNewTool(HRToolDefinition):
    @property
    def name(self) -> str:
        return "my_new_tool"
    
    @property
    def description(self) -> str:
        return "Description of what this tool does"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of param1"
                }
            },
            "required": ["param1"]
        }
    
    @property
    def api_endpoint(self) -> str:
        return "/api/endpoint"
    
    @property
    def http_method(self) -> str:
        return "POST"
    
    def execute(self, param1: str) -> str:
        response = self.api_client.request(
            method=self.http_method,
            endpoint=self.api_endpoint,
            json_data={"param1": param1}
        )
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        if not response.success:
            return f"Failed: {response.error}"
        return f"Success: {response.data}"
```

2. **Add the tool to the module's get_tools function**:

```python
def get_hr_tools(api_client: GatePassAPIClient) -> list:
    return [
        CreateGatePassTool(api_client),
        ListGatePassesTool(api_client),
        # ... existing tools ...
        MyNewTool(api_client),  # Add your new tool
    ]
```

3. **The tool will automatically be registered** in the ToolRegistry and available to users with the appropriate role.

---

## Configuration

Configuration is managed through environment variables. See `strands_agent.core.config` for details.

**Key Configuration Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Base URL for Gate Pass API | Required |
| `API_TIMEOUT` | Request timeout in seconds | 30 |
| `MAX_FILE_SIZE` | Maximum file size in bytes | 5242880 (5MB) |
| `ALLOWED_FILE_FORMATS` | Comma-separated list of allowed formats | jpeg,jpg,png,heic |
| `OPENAI_API_KEY` | OpenAI API key for LLM | Required |

**Example .env file:**

```bash
API_BASE_URL=https://api.example.com
API_TIMEOUT=30
MAX_FILE_SIZE=5242880
ALLOWED_FILE_FORMATS=jpeg,jpg,png,heic
OPENAI_API_KEY=sk-...
```

---

## Additional Resources

- **README.md**: Project overview and setup instructions
- **EXAMPLES.md**: Detailed usage examples and conversation flows
- **requirements.md**: Complete requirements specification
- **design.md**: Detailed design document with architecture and properties

For questions or issues, please refer to the project repository or contact the development team.
