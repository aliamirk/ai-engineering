"""Main GatePassAgent class with LangChain integration."""

from typing import Optional, Any, Dict, List
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough

from .api_client import GatePassAPIClient
from .conversation_memory import ConversationMemory
from .tool_registry import ToolRegistry


class GatePassAgent:
    """Conversational AI agent for Gate Pass Management API.
    
    This agent integrates with LangChain to provide a natural language interface
    for gate pass operations. It filters tools based on user role and maintains
    conversation context across interactions.
    
    Attributes:
        api_client: HTTP client for Gate Pass API
        tool_registry: Registry of all available tools
        user_role: Current user's role (HR_User, Admin_User, or Gate_User)
        conversation_memory: Memory for maintaining conversation context
        llm: LangChain language model for processing user input
        tools: List of LangChain tools available to this agent
        chat_history: List of conversation messages
    """
    
    def __init__(
        self,
        api_base_url: str,
        llm: BaseChatModel,
        user_role: str
    ):
        """Initialize the Gate Pass AI Agent.
        
        Args:
            api_base_url: Base URL for the Gate Pass Management API
            llm: LangChain language model instance (e.g., ChatOpenAI)
            user_role: User's role - must be one of: HR_User, Admin_User, Gate_User
            
        Raises:
            ValueError: If user_role is not one of the valid roles
        """
        # Validate user role
        valid_roles = ["HR_User", "Admin_User", "Gate_User"]
        if user_role not in valid_roles:
            raise ValueError(
                f"Invalid user_role '{user_role}'. Must be one of: {', '.join(valid_roles)}"
            )
        
        # Store user role
        self.user_role = user_role
        
        # Initialize API client
        self.api_client = GatePassAPIClient(base_url=api_base_url)
        
        # Initialize tool registry with API client
        self.tool_registry = ToolRegistry(api_client=self.api_client)
        
        # Initialize conversation memory
        self.conversation_memory = ConversationMemory()
        
        # Get tools filtered by user role
        role_tools = self.tool_registry.get_tools_for_role(user_role)
        
        # Convert tool definitions to LangChain StructuredTool format
        self.tools = self._convert_to_langchain_tools(role_tools)
        
        # Store LLM
        self.llm = llm
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Initialize chat history
        self.chat_history: List[Any] = []
    
    def _get_system_prompt(self) -> str:
        """Generate system prompt based on user role.
        
        Returns:
            System prompt string with role-specific instructions
        """
        base_prompt = """You are a helpful AI assistant for the Gate Pass Management System.
You help users manage gate passes through natural conversation.

Your role: {role}

Guidelines:
- Be conversational and friendly
- Extract parameters from the user's natural language input
- If required parameters are missing, ask specific clarifying questions
- Use context from previous messages - if a pass number or ID was mentioned, you can reference it
- When context contains a current pass, you can use it for follow-up operations
- Provide clear, concise responses
- Format gate pass information in a readable way
- Explain errors in user-friendly language

Parameter Extraction:
- Listen for person names, descriptions, pass numbers (GP-YYYY-NNNN format), and other relevant details
- If a user says "approve it" or "print that pass", use the pass number from context
- Ask for missing required parameters one at a time to keep the conversation natural
- When asking for parameters, explain why you need them

Context Awareness:
- Remember pass numbers and IDs mentioned in the conversation
- Use stored context for follow-up questions like "show me details" or "approve it"
- If context is ambiguous (multiple passes mentioned), ask for clarification
"""
        
        role_specific = {
            "HR_User": """
As an HR user, you can:
- Create new gate passes for people (need: person_name, description, is_returnable)
- List and view gate pass details
- Print gate passes (need: pass_number)
- Check HR notifications
- Generate QR codes for gate passes (need: pass_number)
""",
            "Admin_User": """
As an Admin user, you can:
- View pending gate passes awaiting approval
- Approve or reject gate passes (need: pass_number, your name)
- Delete gate passes (need: pass_number, your name)
- List and view all gate passes
- Print gate passes (need: pass_number)
- Check admin notifications
- Generate QR codes for gate passes (need: pass_number)
""",
            "Gate_User": """
As a Gate user, you can:
- Scan people exiting the facility (need: pass_number, photo)
- Scan people returning to the facility (need: pass_number, photo)
- View gate pass details by number or ID
- View photos associated with gate passes (need: pass_number)
- Generate QR codes for gate passes (need: pass_number)
"""
        }
        
        return base_prompt.format(role=self.user_role) + role_specific.get(self.user_role, "")
    
    def _convert_to_langchain_tools(self, tool_definitions: list) -> list:
        """Convert tool definitions to LangChain StructuredTool format.
        
        Args:
            tool_definitions: List of tool definition objects
            
        Returns:
            List of LangChain StructuredTool instances
        """
        langchain_tools = []
        
        for tool_def in tool_definitions:
            # Create a StructuredTool from the tool definition
            structured_tool = StructuredTool(
                name=tool_def.name,
                description=tool_def.description,
                func=tool_def.execute,
                args_schema=self._create_args_schema(tool_def)
            )
            langchain_tools.append(structured_tool)
        
        return langchain_tools
    
    def _create_args_schema(self, tool_def):
        """Create Pydantic model for tool arguments from JSON schema.
        
        Args:
            tool_def: Tool definition object with parameters property
            
        Returns:
            Pydantic BaseModel class for tool arguments
        """
        from pydantic import BaseModel, Field, create_model
        from typing import Optional as TypingOptional
        
        # Get parameter schema
        params_schema = tool_def.parameters
        properties = params_schema.get("properties", {})
        required_fields = params_schema.get("required", [])
        
        # Build field definitions for Pydantic model
        field_definitions = {}
        
        for param_name, param_info in properties.items():
            param_type = param_info.get("type", "string")
            param_description = param_info.get("description", "")
            
            # Map JSON schema types to Python types
            type_mapping = {
                "string": str,
                "integer": int,
                "number": float,
                "boolean": bool,
                "array": list,
                "object": dict
            }
            
            python_type = type_mapping.get(param_type, str)
            
            # Make optional if not in required list
            if param_name not in required_fields:
                python_type = TypingOptional[python_type]
                field_definitions[param_name] = (python_type, Field(default=None, description=param_description))
            else:
                field_definitions[param_name] = (python_type, Field(description=param_description))
        
        # Create and return Pydantic model
        return create_model(
            f"{tool_def.name}_args",
            **field_definitions
        )
    
    def _extract_pass_references(self, text: str) -> Dict[str, Optional[str]]:
        """Extract pass_number and pass_id from text using regex.
        
        Args:
            text: Text that may contain pass references
            
        Returns:
            Dictionary with extracted pass_number and pass_id (if found)
        """
        import re
        
        result = {"pass_number": None, "pass_id": None}
        
        # Pattern for pass_number: GP-YYYY-NNNN
        pass_number_pattern = r'GP-\d{4}-\d{4}'
        pass_number_match = re.search(pass_number_pattern, text)
        if pass_number_match:
            result["pass_number"] = pass_number_match.group(0)
        
        # Pattern for pass_id: look for "id": "..." or 'id': '...' in JSON-like text
        pass_id_pattern = r'"id"\s*:\s*"([^"]+)"'
        pass_id_match = re.search(pass_id_pattern, text)
        if pass_id_match:
            result["pass_id"] = pass_id_match.group(1)
        
        return result
    
    def _update_context_from_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        result: str
    ) -> None:
        """Update conversation context based on tool execution.
        
        Extracts pass references from tool arguments and results, and updates
        the conversation memory to enable natural follow-up interactions.
        
        Args:
            tool_name: Name of the executed tool
            tool_args: Arguments passed to the tool
            result: Result returned by the tool
        """
        # Store the last operation
        self.conversation_memory.update_context(last_operation=tool_name)
        
        # Extract pass references from tool arguments
        if "pass_number" in tool_args and tool_args["pass_number"]:
            self.conversation_memory.store_pass_reference(
                pass_number=tool_args["pass_number"]
            )
        
        if "pass_id" in tool_args and tool_args["pass_id"]:
            self.conversation_memory.store_pass_reference(
                pass_id=tool_args["pass_id"]
            )
        
        # Extract pass references from result text
        extracted = self._extract_pass_references(result)
        if extracted["pass_number"]:
            self.conversation_memory.store_pass_reference(
                pass_number=extracted["pass_number"]
            )
        if extracted["pass_id"]:
            self.conversation_memory.store_pass_reference(
                pass_id=extracted["pass_id"]
            )
    
    def _get_context_info(self) -> str:
        """Get current conversation context as a formatted string.
        
        Returns:
            Formatted string describing current context
        """
        current_pass = self.conversation_memory.get_current_pass()
        context_parts = []
        
        if current_pass["pass_number"]:
            context_parts.append(f"Current pass number: {current_pass['pass_number']}")
        
        if current_pass["pass_id"]:
            context_parts.append(f"Current pass ID: {current_pass['pass_id']}")
        
        if context_parts:
            return "\n\nContext: " + ", ".join(context_parts)
        
        return ""

    
    def _execute_tool_calls(self, tool_calls: List[Any]) -> List[str]:
        """Execute tool calls and return results.
        
        Args:
            tool_calls: List of tool call objects from LLM
            
        Returns:
            List of tool execution results
        """
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Find the tool
            tool = None
            for t in self.tools:
                if t.name == tool_name:
                    tool = t
                    break
            
            if tool:
                try:
                    # Execute the tool
                    result = tool.func(**tool_args)
                    results.append(result)
                    
                    # Update conversation context after tool execution
                    self._update_context_from_tool_call(tool_name, tool_args, result)
                    
                except Exception as e:
                    results.append(f"Error executing {tool_name}: {str(e)}")
            else:
                results.append(f"Tool {tool_name} not found")
        
        return results
    
    def chat(self, user_input: str) -> str:
        """Process user input and return agent response.
        
        This method:
        1. Processes natural language input
        2. Uses LLM to identify intent and select appropriate tools
        3. Extracts parameters from natural language
        4. Asks clarifying questions if parameters are missing
        5. Updates conversation context after each interaction
        
        Args:
            user_input: Natural language input from the user
            
        Returns:
            Agent's natural language response
        """
        try:
            # Add system message on first turn
            if not self.chat_history:
                system_prompt = self._get_system_prompt()
                self.chat_history.append(SystemMessage(content=system_prompt))
            
            # Add context information to user input if available
            context_info = self._get_context_info()
            enhanced_input = user_input
            if context_info:
                # Prepend context to help LLM use stored information
                enhanced_input = f"{user_input}{context_info}"
            
            # Add user message to history
            self.chat_history.append(HumanMessage(content=enhanced_input))
            
            # Get LLM response with tool calls
            response = self.llm_with_tools.invoke(self.chat_history)
            
            # Check if LLM wants to call tools
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Execute tool calls (this also updates context)
                tool_results = self._execute_tool_calls(response.tool_calls)
                
                # Add AI response with tool calls to history
                self.chat_history.append(response)
                
                # Create a message with tool results
                tool_result_message = HumanMessage(
                    content=f"Tool execution results: {' '.join(tool_results)}"
                )
                self.chat_history.append(tool_result_message)
                
                # Get final response from LLM with updated context
                final_response = self.llm.invoke(self.chat_history)
                self.chat_history.append(final_response)
                
                return final_response.content
            else:
                # No tool calls - LLM might be asking clarifying questions
                # or providing information based on context
                self.chat_history.append(response)
                return response.content
            
        except Exception as e:
            # Handle any unexpected errors gracefully
            error_message = f"I encountered an error while processing your request: {str(e)}"
            return error_message
    
    def reset_context(self) -> None:
        """Clear conversation context for a new session.
        
        This method resets both the conversation memory and chat history,
        effectively starting a fresh conversation.
        """
        self.conversation_memory.clear()
        self.chat_history = []
    
    def get_available_tools(self) -> List[str]:
        """Get list of tool names available for the current user role.
        
        Returns:
            List of tool names that the current user can access
        """
        return [tool.name for tool in self.tools]
