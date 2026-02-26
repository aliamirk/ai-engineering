# Gate Pass AI Agent - Example Usage Guide

This guide accompanies the `example.py` script and provides a comprehensive overview of how to use the Gate Pass AI Agent for each user role.

## Quick Start

To run the example script:

```bash
# Ensure your environment is configured
cp .env.example .env
# Edit .env with your API_BASE_URL and OPENAI_API_KEY

# Run the examples
python example.py
```

## Example Scenarios Included

### 1. HR User Examples

The HR user examples demonstrate:

- **Creating gate passes** with complete information
- **Creating gate passes** with missing parameters (agent asks clarifying questions)
- **Listing gate passes** with status filtering
- **Context-aware follow-ups** (e.g., "print that pass")
- **Natural language variations** for the same operation
- **Checking notifications**
- **Generating QR codes**

**Key Conversation Patterns:**

```python
# Complete information provided
"Create a gate pass for John Doe to pick up equipment, and he will return"

# Incremental information gathering
"I need to create a gate pass for Jane Smith"
→ "She's going to the supplier to collect materials"
→ "Yes, she will return"

# Context-aware follow-up
"Show me all pending gate passes"
→ "Get me the details for GP-2024-0001"
→ "Print that pass"  # Uses context from previous query
```

### 2. Admin User Examples

The Admin user examples demonstrate:

- **Reviewing pending gate passes**
- **Approving gate passes** with explicit pass numbers
- **Approving with context** (pass number remembered from previous query)
- **Rejecting gate passes**
- **Multi-step approval workflow**
- **Deleting gate passes**
- **Filtering gate passes** by status
- **Checking admin notifications**

**Key Conversation Patterns:**

```python
# Explicit approval
"Approve gate pass GP-2024-0001, my name is Sarah Admin"

# Context-aware approval
"Get me details for gate pass GP-2024-0002"
→ "Approve it, I'm Sarah Admin"  # Uses pass number from context

# Multi-step workflow
"What gate passes are waiting for approval?"
→ "Show me details for the first one"
→ "Looks good, approve it. I'm Sarah Admin"
```

### 3. Gate User Examples

The Gate user examples demonstrate:

- **Scanning exits** with photo uploads
- **Scanning returns** with photo uploads
- **Looking up gate pass details** by pass number
- **Viewing gate pass photos**
- **Quick lookups** with minimal input
- **Handling invalid pass numbers**
- **Natural language variations** for scanning operations

**Key Conversation Patterns:**

```python
# Exit scanning
"Someone is exiting with gate pass GP-2024-0001"
→ (Agent prompts for photo)

# Return scanning
"Person returning with pass GP-2024-0001"
→ (Agent prompts for photo)

# Context-aware photo viewing
"Show me details for gate pass GP-2024-0001"
→ "Show me the photos for that pass"  # Uses context

# Natural variations
"Scan exit for GP-2024-0001"
"Person leaving with pass GP-2024-0001"
"Exit scan GP-2024-0001"
# All understood by the agent
```

### 4. Context Management Examples

Demonstrates how the agent maintains conversation context:

- **Multi-turn conversations** with context awareness
- **Context switching** between different gate passes
- **Context reset** and its effects
- **Implicit references** using stored context

**Example Flow:**

```python
"Create a gate pass for Michael Chen for client meeting, returnable"
→ "What's the pass number?"  # Agent knows which pass
→ "Print it"  # Agent uses stored pass number
→ "Generate a QR code for it"  # Still using same context
→ "Now show me details for GP-2024-0005"  # Context switches
→ "Print this one too"  # Uses new context
```

### 5. Error Handling Examples

Demonstrates how the agent handles errors gracefully:

- **Missing required parameters** (agent asks for them)
- **Invalid pass number formats** (agent provides guidance)
- **Non-existent gate passes** (clear error messages)
- **Unauthorized operations** (role-based restrictions explained)

**Example Scenarios:**

```python
# Missing parameter
"Approve gate pass GP-2024-0001"
→ Agent: "I need your name to approve the gate pass. What's your name?"

# Invalid format
"Show me details for pass 12345"
→ Agent: "Please provide a valid pass number in format GP-YYYY-NNNN"

# Non-existent pass
"Get details for GP-2024-9999"
→ Agent: "Gate pass GP-2024-9999 does not exist. Please check the pass number."

# Unauthorized operation (HR user trying to approve)
"Approve gate pass GP-2024-0001"
→ Agent: "HR users cannot approve gate passes. This operation requires Admin role."
```

### 6. Available Tools by Role

Shows which tools are available to each user role:

- **HR_User**: create_gate_pass, list_gate_passes, get_gate_pass_details, print_gate_pass, get_hr_notifications, mark_notification_read, get_qr_code
- **Admin_User**: list_pending_gate_passes, get_gate_pass_by_number, approve_gate_pass, reject_gate_pass, delete_gate_pass, list_all_gate_passes_admin, print_gate_pass_admin, get_admin_notifications, mark_notification_read, get_qr_code
- **Gate_User**: scan_exit, scan_return, get_gate_pass_by_number_gate, get_gate_pass_by_id_gate, get_gate_pass_photos, get_qr_code

## Running Individual Examples

You can modify `example.py` to run specific scenarios:

```python
if __name__ == "__main__":
    # Run only HR examples
    example_hr_user()
    
    # Or run only Admin examples
    # example_admin_user()
    
    # Or run only Gate examples
    # example_gate_user()
```

## Customizing Examples

To create your own examples:

```python
from langchain_openai import ChatOpenAI
from strands_agent.core.agent import GatePassAgent
from strands_agent.core.config import get_config

# Load configuration
config = get_config()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create agent for your role
agent = GatePassAgent(
    api_base_url=config.api_base_url,
    llm=llm,
    user_role="HR_User"  # or "Admin_User" or "Gate_User"
)

# Start chatting
response = agent.chat("Your natural language request here")
print(response)

# Continue conversation
response = agent.chat("Follow-up question")
print(response)

# Reset context when starting a new conversation
agent.reset_context()
```

## Tips for Natural Conversations

1. **Be conversational**: The agent understands natural language, so you don't need to use specific commands or syntax.

2. **Use context**: After mentioning a gate pass, you can refer to it as "it", "that pass", "this one", etc.

3. **Provide information incrementally**: You don't need to provide all information at once. The agent will ask for missing details.

4. **Try variations**: There are many ways to express the same intent. The agent understands variations like:
   - "Create a gate pass" / "I need a new gate pass" / "Make a pass for..."
   - "Show me" / "List" / "Get me" / "Display"
   - "Approve it" / "Approve this pass" / "Give approval"

5. **Check available tools**: Use `agent.get_available_tools()` to see what operations are available for your role.

6. **Reset context**: Use `agent.reset_context()` when starting a completely new conversation to clear stored references.

## Common Patterns

### Pattern 1: Create and Follow-up
```python
"Create a gate pass for [name] for [purpose], [returnable/non-returnable]"
→ "What's the pass number?"
→ "Print it"
→ "Generate a QR code"
```

### Pattern 2: List and Select
```python
"Show me all [status] gate passes"
→ "Get details for [pass_number]"
→ "Approve/Reject/Print it"
```

### Pattern 3: Quick Lookup
```python
"Look up [pass_number]"
→ "Show me the photos"
→ "Generate QR code"
```

### Pattern 4: Incremental Creation
```python
"Create a gate pass for [name]"
→ Agent asks: "What's the purpose?"
→ "[purpose]"
→ Agent asks: "Will they return?"
→ "Yes/No"
```

## Troubleshooting

### "OPENAI_API_KEY environment variable is not set"
Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
# Or add it to your .env file
```

### "Unable to connect to the API"
Ensure the Gate Pass Management API is running and the `API_BASE_URL` is correct in your `.env` file.

### "Invalid user_role"
User role must be one of: `HR_User`, `Admin_User`, `Gate_User` (case-sensitive).

### Agent doesn't understand my request
Try rephrasing with more explicit information:
- Include the pass number in GP-YYYY-NNNN format
- Specify the operation clearly (create, approve, list, etc.)
- Provide required parameters (name, description, etc.)

## Next Steps

- Read the [README.md](README.md) for installation and setup instructions
- Review the [design document](.kiro/specs/gatepass-ai-agent/design.md) for architecture details
- Check the [requirements document](.kiro/specs/gatepass-ai-agent/requirements.md) for complete specifications
- Run the test suite: `pytest tests/`

## Support

For issues or questions:
1. Check the README.md troubleshooting section
2. Review the example scenarios in this guide
3. Open an issue on the repository
