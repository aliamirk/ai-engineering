#!/usr/bin/env python3
"""
Example usage script for Gate Pass AI Agent.

This script demonstrates how to initialize and use the GatePassAgent for each user role
(HR, Admin, Gate) with realistic conversation flows showing natural language interactions,
parameter extraction, and context management.

Requirements: 12.4
"""

import os
from langchain_openai import ChatOpenAI
from strands_agent.core.agent import GatePassAgent
from strands_agent.core.config import get_config


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_conversation(user_input: str, agent_response: str):
    """Print a formatted conversation exchange."""
    print(f"👤 User: {user_input}")
    print(f"🤖 Agent: {agent_response}\n")


def example_hr_user():
    """Demonstrate HR user interactions."""
    print_section("HR User Examples")
    
    # Load configuration
    config = get_config()
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Create agent for HR user
    agent = GatePassAgent(
        api_base_url=config.api_base_url,
        llm=llm,
        user_role="HR_User"
    )
    
    print("Scenario 1: Creating a gate pass with all details provided")
    print("-" * 80)
    
    user_input = "Create a gate pass for John Doe to pick up equipment from the warehouse, and he will return"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 2: Creating a gate pass with missing information")
    print("-" * 80)
    
    # Reset context for new scenario
    agent.reset_context()
    
    user_input = "I need to create a gate pass for Jane Smith"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # Agent should ask for missing parameters
    user_input = "She's going to the supplier to collect materials"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    user_input = "Yes, she will return"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 3: Listing gate passes with context-aware follow-up")
    print("-" * 80)
    
    agent.reset_context()
    
    user_input = "Show me all pending gate passes"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # Follow-up using context (assuming GP-2024-0001 was in the list)
    user_input = "Get me the details for GP-2024-0001"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # Another follow-up using stored context
    user_input = "Print that pass"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 4: Natural language variations")
    print("-" * 80)
    
    agent.reset_context()
    
    # Different ways to ask for the same thing
    variations = [
        "Can you show me gate passes that have been approved?",
        "I want to see all the approved passes",
        "List approved gate passes"
    ]
    
    for variation in variations:
        response = agent.chat(variation)
        print_conversation(variation, response)
    
    print("\nScenario 5: Checking notifications")
    print("-" * 80)
    
    agent.reset_context()
    
    user_input = "Do I have any notifications?"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 6: Generating QR code")
    print("-" * 80)
    
    user_input = "Generate a QR code for gate pass GP-2024-0001"
    response = agent.chat(user_input)
    print_conversation(user_input, response)


def example_admin_user():
    """Demonstrate Admin user interactions."""
    print_section("Admin User Examples")
    
    # Load configuration
    config = get_config()
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Create agent for Admin user
    agent = GatePassAgent(
        api_base_url=config.api_base_url,
        llm=llm,
        user_role="Admin_User"
    )
    
    print("Scenario 1: Reviewing and approving pending gate passes")
    print("-" * 80)
    
    user_input = "Show me all pending gate passes that need approval"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # Approve a specific pass
    user_input = "Approve gate pass GP-2024-0001, my name is Sarah Admin"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 2: Approving with context (pass number remembered)")
    print("-" * 80)
    
    agent.reset_context()
    
    user_input = "Get me details for gate pass GP-2024-0002"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # Approve using context - no need to repeat pass number
    user_input = "Approve it, I'm Sarah Admin"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 3: Rejecting a gate pass")
    print("-" * 80)
    
    agent.reset_context()
    
    user_input = "I need to reject gate pass GP-2024-0003, my name is Sarah Admin"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 4: Multi-step approval workflow")
    print("-" * 80)
    
    agent.reset_context()
    
    user_input = "What gate passes are waiting for approval?"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    user_input = "Show me details for the first one"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    user_input = "Looks good, approve it. I'm Sarah Admin"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 5: Deleting a gate pass")
    print("-" * 80)
    
    agent.reset_context()
    
    user_input = "Delete gate pass GP-2024-0005, my name is Sarah Admin"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 6: Listing all gate passes with filtering")
    print("-" * 80)
    
    user_input = "Show me all gate passes that have been rejected"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 7: Checking admin notifications")
    print("-" * 80)
    
    user_input = "Check my notifications"
    response = agent.chat(user_input)
    print_conversation(user_input, response)


def example_gate_user():
    """Demonstrate Gate user interactions."""
    print_section("Gate User Examples")
    
    # Load configuration
    config = get_config()
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Create agent for Gate user
    agent = GatePassAgent(
        api_base_url=config.api_base_url,
        llm=llm,
        user_role="Gate_User"
    )
    
    print("Scenario 1: Scanning exit with photo")
    print("-" * 80)
    print("Note: In a real application, the photo would be provided as a file.")
    print("The agent will prompt for the photo if not provided initially.\n")
    
    user_input = "Someone is exiting with gate pass GP-2024-0001"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # In a real scenario, the user would provide the photo file
    # For this example, we show what the conversation would look like
    print("(User would provide photo file here)")
    print("🤖 Agent: Exit scan recorded successfully for GP-2024-0001\n")
    
    print("\nScenario 2: Scanning return")
    print("-" * 80)
    
    agent.reset_context()
    
    user_input = "Person returning with pass GP-2024-0001"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("(User would provide photo file here)")
    print("🤖 Agent: Return scan recorded successfully for GP-2024-0001\n")
    
    print("\nScenario 3: Looking up gate pass details")
    print("-" * 80)
    
    agent.reset_context()
    
    user_input = "Show me details for gate pass GP-2024-0001"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 4: Viewing gate pass photos")
    print("-" * 80)
    
    # Using context from previous query
    user_input = "Show me the photos for that pass"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 5: Quick lookup by pass number")
    print("-" * 80)
    
    agent.reset_context()
    
    user_input = "Look up GP-2024-0002"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 6: Handling invalid pass numbers")
    print("-" * 80)
    
    user_input = "Check gate pass GP-2024-9999"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 7: Natural language variations for scanning")
    print("-" * 80)
    
    agent.reset_context()
    
    variations = [
        "Scan exit for GP-2024-0001",
        "Person leaving with pass GP-2024-0001",
        "Exit scan GP-2024-0001",
        "Someone is going out with gate pass GP-2024-0001"
    ]
    
    print("Different ways to request an exit scan:\n")
    for variation in variations:
        print(f"👤 User: {variation}")
    print("\n🤖 Agent: (Would process any of these variations and prompt for photo)\n")


def example_context_management():
    """Demonstrate conversation context management across multiple turns."""
    print_section("Context Management Examples")
    
    # Load configuration
    config = get_config()
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Create agent for HR user
    agent = GatePassAgent(
        api_base_url=config.api_base_url,
        llm=llm,
        user_role="HR_User"
    )
    
    print("Scenario: Multi-turn conversation with context awareness")
    print("-" * 80)
    
    # Turn 1: Create a gate pass
    user_input = "Create a gate pass for Michael Chen for client meeting, returnable"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # Turn 2: Ask about the created pass (using context)
    user_input = "What's the pass number?"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # Turn 3: Print the pass (using context)
    user_input = "Print it"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # Turn 4: Generate QR code (using context)
    user_input = "Generate a QR code for it"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # Turn 5: Switch to a different pass
    user_input = "Now show me details for GP-2024-0005"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    # Turn 6: Print the new pass (context updated)
    user_input = "Print this one too"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nDemonstrating context reset:")
    print("-" * 80)
    
    agent.reset_context()
    print("Context has been reset.\n")
    
    user_input = "Print it"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    print("(Agent should ask which pass to print since context was cleared)")


def example_error_handling():
    """Demonstrate error handling and recovery."""
    print_section("Error Handling Examples")
    
    # Load configuration
    config = get_config()
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Create agent for Admin user
    agent = GatePassAgent(
        api_base_url=config.api_base_url,
        llm=llm,
        user_role="Admin_User"
    )
    
    print("Scenario 1: Missing required parameters")
    print("-" * 80)
    
    user_input = "Approve gate pass GP-2024-0001"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    print("(Agent should ask for the admin name)")
    
    user_input = "My name is Alex Admin"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    
    print("\nScenario 2: Invalid pass number format")
    print("-" * 80)
    
    agent.reset_context()
    
    user_input = "Show me details for pass 12345"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    print("(Agent should handle invalid format gracefully)")
    
    print("\nScenario 3: Non-existent gate pass")
    print("-" * 80)
    
    user_input = "Get details for GP-2024-9999"
    response = agent.chat(user_input)
    print_conversation(user_input, response)
    print("(Agent should explain that the pass doesn't exist)")
    
    print("\nScenario 4: Unauthorized operation")
    print("-" * 80)
    
    # Create HR agent to demonstrate role restrictions
    hr_agent = GatePassAgent(
        api_base_url=config.api_base_url,
        llm=llm,
        user_role="HR_User"
    )
    
    user_input = "Approve gate pass GP-2024-0001"
    response = hr_agent.chat(user_input)
    print_conversation(user_input, response)
    print("(Agent should explain that HR users cannot approve gate passes)")


def example_available_tools():
    """Demonstrate checking available tools for each role."""
    print_section("Available Tools by Role")
    
    # Load configuration
    config = get_config()
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    roles = ["HR_User", "Admin_User", "Gate_User"]
    
    for role in roles:
        agent = GatePassAgent(
            api_base_url=config.api_base_url,
            llm=llm,
            user_role=role
        )
        
        tools = agent.get_available_tools()
        
        print(f"\n{role} has access to {len(tools)} tools:")
        print("-" * 80)
        for tool in tools:
            print(f"  • {tool}")


def main():
    """Run all example scenarios."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "Gate Pass AI Agent - Example Usage" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    
    print("\nThis script demonstrates the Gate Pass AI Agent with realistic conversation")
    print("flows for each user role (HR, Admin, Gate). Each scenario shows how the agent")
    print("handles natural language input, extracts parameters, and manages context.")
    
    print("\n" + "⚠" * 40)
    print("NOTE: These examples show the conversation flow and expected behavior.")
    print("To run against a real API, ensure the Gate Pass Management API is running")
    print("and configure the API_BASE_URL in your .env file.")
    print("⚠" * 40)
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("\n❌ ERROR: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key in the .env file or environment.")
        print("\nExample:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # Run all example scenarios
        example_hr_user()
        example_admin_user()
        example_gate_user()
        example_context_management()
        example_error_handling()
        example_available_tools()
        
        print_section("Summary")
        print("✅ All example scenarios completed!")
        print("\nKey Takeaways:")
        print("  • The agent understands natural language variations")
        print("  • Context is maintained across conversation turns")
        print("  • Missing parameters trigger clarifying questions")
        print("  • Role-based access control restricts available tools")
        print("  • Error handling provides user-friendly guidance")
        print("\nFor more information, see the README.md file.")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("\nThis might be because:")
        print("  • The Gate Pass Management API is not running")
        print("  • The API_BASE_URL is not configured correctly")
        print("  • The OpenAI API key is invalid")
        print("\nTo run these examples, ensure your environment is properly configured.")


if __name__ == "__main__":
    main()
