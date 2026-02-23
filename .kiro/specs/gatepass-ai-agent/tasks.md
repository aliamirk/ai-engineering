# Implementation Plan: Gate Pass AI Agent

## Overview

This implementation plan creates a conversational AI agent using LangChain that provides a natural language interface to the Gate Pass Management API. The agent uses a tool-based architecture where each API endpoint is exposed as a tool, with role-based access control filtering tools based on user roles (HR, Admin, Gate). The implementation follows the design document's architecture with comprehensive property-based testing using Hypothesis.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create strands_agent directory structure with subdirectories for core, tools, tests
  - Create pyproject.toml with dependencies: langchain, langchain-openai, requests, hypothesis, pytest
  - Create .env.example file for configuration template
  - Create README.md with project overview and setup instructions
  - _Requirements: 12.5, 12.6_

- [x] 2. Implement API client
  - [x] 2.1 Create GatePassAPIClient class with request method
    - Implement __init__ with base_url and timeout parameters
    - Implement request method supporting GET and POST with params, json_data, and files
    - Implement exponential backoff retry logic (3 attempts: 2s, 4s, 8s delays)
    - Implement timeout handling and connection error handling
    - _Requirements: 1.5, 1.6, 1.7, 1.8, 2.8, 2.9, 2.10, 2.11, 3.6, 3.7, 3.8, 3.9, 4.4, 4.5, 4.6, 5.2, 11.4_
  
  - [x] 2.2 Implement error handling and response parsing
    - Implement handle_error method to convert HTTP status codes to user-friendly messages
    - Handle 400, 403, 404, 422, 500 status codes with specific messages
    - Parse API response JSON and create APIResponse objects
    - _Requirements: 7.2, 7.5, 11.1, 11.2, 11.3, 11.5_
  
  - [ ]* 2.3 Write unit tests for API client
    - Test successful requests for GET and POST methods
    - Test error handling for each HTTP status code (400, 403, 404, 422, 500)
    - Test retry logic with transient failures using mocked responses
    - Test timeout handling and connection errors
    - Test multipart form data formatting
    - _Requirements: 1.5, 1.6, 1.7, 1.8, 2.8, 2.9, 2.10, 2.11, 3.6, 3.7, 11.1, 11.2, 11.3, 11.4_

- [x] 3. Implement data models
  - [x] 3.1 Create data model classes
    - Create GatePass dataclass with all fields (id, pass_number, person_name, description, is_returnable, status, timestamps)
    - Create Notification dataclass with all fields (id, message, type, created_at, is_read, related_pass_id)
    - Create APIResponse dataclass with success, status_code, data, error fields
    - Create ConversationContext dataclass with current_pass_number, current_pass_id, last_operation, pending_parameters
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ]* 3.2 Write property test for data model validation
    - **Property 9: Conversation Context Persistence**
    - **Validates: Requirements 10.3**
    - Test that conversation context data persists during session and clears on reset
    - _Requirements: 10.3_

- [x] 4. Implement file handling utilities
  - [x] 4.1 Create file validation functions
    - Implement validate_file_format function to check JPEG, PNG, HEIC formats
    - Implement validate_file_size function with configurable size limit
    - Implement prepare_multipart_data function to format files for API requests
    - _Requirements: 9.3, 9.4, 9.5_
  
  - [ ]* 4.2 Write property tests for file validation
    - **Property 7: File Format Validation**
    - **Validates: Requirements 9.3**
    - Test that valid formats (JPEG, PNG, HEIC) are accepted and invalid formats are rejected
    - _Requirements: 9.3_
  
  - [ ]* 4.3 Write property test for file size validation
    - **Property 8: File Size Validation**
    - **Validates: Requirements 9.5**
    - Test that files exceeding size limit are rejected with appropriate error
    - _Requirements: 9.5_
  
  - [ ]* 4.4 Write property test for multipart form data
    - **Property 10: Multipart Form Data File Inclusion**
    - **Validates: Requirements 3.6, 3.7, 9.4**
    - Test that scan operations include both pass_number and photo in multipart format
    - _Requirements: 3.6, 3.7, 9.4_

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement tool definitions for HR operations
  - [x] 6.1 Create HR tool definitions
    - Create create_gate_pass tool with person_name, description, is_returnable parameters
    - Create list_gate_passes tool with optional status parameter
    - Create get_gate_pass_details tool with pass_id parameter
    - Create print_gate_pass tool with pass_number parameter
    - Each tool must include name, description, parameter schema, required_role='HR_User', api_endpoint, http_method
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [x] 6.2 Implement HR tool execution handlers
    - Implement execution logic to call API client with correct endpoint and method
    - Implement response formatting for each tool
    - _Requirements: 1.5, 1.6, 1.7, 1.8, 7.1, 7.3_

- [x] 7. Implement tool definitions for Admin operations
  - [x] 7.1 Create Admin tool definitions
    - Create list_pending_gate_passes tool with no parameters
    - Create get_gate_pass_by_number tool with pass_number parameter
    - Create approve_gate_pass tool with pass_number and name parameters
    - Create reject_gate_pass tool with pass_number and name parameters
    - Create delete_gate_pass tool with pass_number and name parameters
    - Create list_all_gate_passes_admin tool with optional status parameter
    - Create print_gate_pass_admin tool with pass_number parameter
    - Each tool must include name, description, parameter schema, required_role='Admin_User', api_endpoint, http_method
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_
  
  - [x] 7.2 Implement Admin tool execution handlers
    - Implement execution logic to call API client with correct endpoint and method
    - Implement response formatting for each tool
    - _Requirements: 2.8, 2.9, 2.10, 2.11, 7.1, 7.3_

- [x] 8. Implement tool definitions for Gate operations
  - [x] 8.1 Create Gate tool definitions
    - Create scan_exit tool with pass_number and photo file parameters
    - Create scan_return tool with pass_number and photo file parameters
    - Create get_gate_pass_by_number_gate tool with pass_number parameter
    - Create get_gate_pass_by_id_gate tool with pass_id parameter
    - Create get_gate_pass_photos tool with pass_number parameter
    - Each tool must include name, description, parameter schema, required_role='Gate_User', api_endpoint, http_method
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 8.2 Implement Gate tool execution handlers with file upload support
    - Implement execution logic to call API client with multipart form data for scan operations
    - Integrate file validation before API calls
    - Implement response formatting for each tool
    - _Requirements: 3.6, 3.7, 3.8, 3.9, 7.1, 7.3, 9.1, 9.2, 9.4_

- [ ] 9. Implement tool definitions for Notification and QR Code operations
  - [x] 9.1 Create Notification and QR Code tool definitions
    - Create get_admin_notifications tool with no parameters, required_role='Admin_User'
    - Create get_hr_notifications tool with no parameters, required_role='HR_User'
    - Create mark_notification_read tool with notification_id parameter, required_role=['Admin_User', 'HR_User']
    - Create get_qr_code tool with pass_number parameter, required_role='All'
    - Each tool must include name, description, parameter schema, required_role, api_endpoint, http_method
    - _Requirements: 4.1, 4.2, 4.3, 5.1_
  
  - [x] 9.2 Implement Notification and QR Code tool execution handlers
    - Implement execution logic to call API client with correct endpoint and method
    - Implement response formatting, ensuring QR code image data is returned without modification
    - _Requirements: 4.4, 4.5, 4.6, 5.2, 5.3_
  
  - [ ]* 9.3 Write property test for QR code data return
    - **Property 6: QR Code Data Return**
    - **Validates: Requirements 5.3**
    - Test that QR code image data is returned without modification
    - _Requirements: 5.3_

- [x] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement tool registry with role-based filtering
  - [x] 11.1 Create ToolRegistry class
    - Implement __init__ to register all tools
    - Implement get_tools_for_role method to filter tools by user role
    - Implement get_tool method to retrieve specific tool by name
    - Store all tool definitions in a structured format
    - _Requirements: 8.1, 8.4, 8.5, 8.6, 12.1, 12.2, 12.3_
  
  - [x] 11.2 Implement role-based authorization enforcement
    - Implement check_authorization method to verify user role before tool execution
    - Block tool execution if role doesn't match, return error before API call
    - _Requirements: 8.2, 8.3_
  
  - [ ]* 11.3 Write property test for tool schema validation
    - **Property 1: Tool Schema Validation**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 5.1, 12.1, 12.2, 12.3**
    - Test that all tools have required fields: name, description, parameters, required_role, api_endpoint, http_method
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 5.1, 12.1, 12.2, 12.3_
  
  - [ ]* 11.4 Write property test for tool-to-API endpoint mapping
    - **Property 2: Tool-to-API Endpoint Mapping**
    - **Validates: Requirements 1.5, 1.6, 1.7, 1.8, 2.8, 2.9, 2.10, 2.11, 3.6, 3.7, 3.8, 3.9, 4.4, 4.5, 4.6, 5.2**
    - Test that tool invocations result in correct API calls with correct endpoint, method, and parameters
    - _Requirements: 1.5, 1.6, 1.7, 1.8, 2.8, 2.9, 2.10, 2.11, 3.6, 3.7, 3.8, 3.9, 4.4, 4.5, 4.6, 5.2_
  
  - [ ]* 11.5 Write property test for role-based tool filtering
    - **Property 3: Role-Based Tool Filtering**
    - **Validates: Requirements 8.4, 8.5, 8.6**
    - Test that each role only receives authorized tools
    - _Requirements: 8.4, 8.5, 8.6_
  
  - [ ]* 11.6 Write property test for role context persistence
    - **Property 4: Role Context Persistence**
    - **Validates: Requirements 8.1**
    - Test that role persists throughout session until changed or session ends
    - _Requirements: 8.1_
  
  - [ ]* 11.7 Write property test for role-based authorization enforcement
    - **Property 5: Role-Based Authorization Enforcement**
    - **Validates: Requirements 8.2**
    - Test that tool execution is blocked before API call if role doesn't match
    - _Requirements: 8.2_

- [x] 12. Implement conversation memory and context management
  - [x] 12.1 Create ConversationMemory class
    - Implement __init__ to initialize empty context
    - Implement store_pass_reference method to save pass_number and pass_id
    - Implement get_current_pass method to retrieve stored pass information
    - Implement update_context method to update conversation variables
    - Implement clear method to reset context
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 12.2 Write unit tests for conversation memory
    - Test storing and retrieving pass references
    - Test context updates and clearing
    - Test handling of ambiguous references
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 13. Implement main GatePassAgent class
  - [x] 13.1 Create GatePassAgent with LangChain integration
    - Implement __init__ with api_base_url, llm, and user_role parameters
    - Initialize API client, tool registry, and conversation memory
    - Filter tools based on user role during initialization
    - Create LangChain agent with filtered tools and conversation memory
    - _Requirements: 6.1, 8.1, 12.1, 12.2, 12.3_
  
  - [x] 13.2 Implement chat method for natural language processing
    - Implement chat method to process user input
    - Integrate with LangChain agent to identify intent and select tools
    - Extract parameters from natural language using LLM
    - Handle missing parameters by asking clarifying questions
    - Update conversation context after each interaction
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.3, 7.4_
  
  - [x] 13.3 Implement session management methods
    - Implement reset_context method to clear conversation memory
    - Implement get_available_tools method to list tools for current role
    - _Requirements: 10.3_
  
  - [ ]* 13.4 Write integration tests for GatePassAgent
    - Test agent initialization with different roles
    - Test end-to-end conversation flow for HR user creating gate pass
    - Test end-to-end conversation flow for Admin user approving gate pass
    - Test end-to-end conversation flow for Gate user scanning exit
    - Test conversation context persistence across multiple turns
    - Test role-based tool access restrictions
    - Use mocked API client and LLM for deterministic testing
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 7.1, 7.3, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 10.1, 10.2, 10.3_

- [x] 14. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Create configuration and deployment files
  - [x] 15.1 Create configuration management
    - Create config.py to load configuration from environment variables
    - Define API_BASE_URL, API_TIMEOUT, MAX_FILE_SIZE, ALLOWED_FILE_FORMATS
    - Support environment-specific configuration (development, staging, production)
    - _Requirements: 12.5, 12.6_
  
  - [~] 15.2 Create example usage script
    - Create example.py demonstrating agent initialization and usage
    - Include examples for each user role (HR, Admin, Gate)
    - Include example conversations showing natural language interactions
    - _Requirements: 12.4_
  
  - [ ]* 15.3 Write unit tests for configuration loading
    - Test loading configuration from environment variables
    - Test handling of missing configuration values
    - Test environment-specific configuration
    - _Requirements: 12.5, 12.6_

- [ ] 16. Create documentation
  - [~] 16.1 Update README with comprehensive documentation
    - Document installation and setup instructions
    - Document configuration options and environment variables
    - Document usage examples for each user role
    - Document tool definitions and their parameters
    - Document error handling and troubleshooting
    - _Requirements: 12.1, 12.2, 12.3, 12.4_
  
  - [~] 16.2 Create API documentation
    - Document GatePassAgent class and its methods
    - Document ToolRegistry class and tool filtering
    - Document API client interface and error handling
    - Document data models and their fields
    - _Requirements: 12.1, 12.2, 12.3_

- [~] 17. Final checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify test coverage meets target (>80%)
  - Ensure all integration tests pass
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis framework with minimum 100 iterations
- All property tests are tagged with feature name and property number
- Checkpoints ensure incremental validation throughout implementation
- Implementation uses Python with LangChain framework as specified in design
- File uploads use multipart form data format for scan operations
- Role-based access control is enforced at tool registry level before API calls
