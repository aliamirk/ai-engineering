"""
Configuration management for Gate Pass AI Agent.

This module loads configuration from environment variables with sensible defaults
and supports environment-specific configuration (development, staging, production).
"""

import os
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """
    Configuration class for Gate Pass AI Agent.
    
    Attributes:
        api_base_url: Base URL for the Gate Pass Management API
        api_timeout: Timeout in seconds for API requests
        max_file_size: Maximum file size in bytes for photo uploads
        allowed_file_formats: List of allowed file formats for photo uploads
        environment: Current environment (development, staging, production)
        openai_api_key: OpenAI API key for LangChain LLM
        default_user_role: Default user role if not specified
    """
    api_base_url: str
    api_timeout: int
    max_file_size: int
    allowed_file_formats: List[str]
    environment: str
    openai_api_key: Optional[str]
    default_user_role: str


def load_config() -> Config:
    """
    Load configuration from environment variables with sensible defaults.
    
    Environment variables:
        - API_BASE_URL: Base URL for the Gate Pass Management API
        - API_TIMEOUT: Timeout in seconds for API requests
        - MAX_FILE_SIZE: Maximum file size in bytes for photo uploads
        - ALLOWED_FILE_FORMATS: Comma-separated list of allowed file formats
        - ENVIRONMENT: Current environment (development, staging, production)
        - OPENAI_API_KEY: OpenAI API key for LangChain LLM
        - DEFAULT_USER_ROLE: Default user role if not specified
    
    Returns:
        Config object with loaded configuration
    
    Raises:
        ValueError: If required configuration is missing or invalid
    """
    # Load environment from .env file if it exists (for development)
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        _load_env_file(env_file)
    
    # Get environment
    environment = os.getenv('ENVIRONMENT', 'development')
    
    # Load configuration with environment-specific defaults
    config = Config(
        api_base_url=_get_api_base_url(environment),
        api_timeout=_get_int_env('API_TIMEOUT', 30),
        max_file_size=_get_int_env('MAX_FILE_SIZE', 5242880),  # 5MB default
        allowed_file_formats=_get_list_env('ALLOWED_FILE_FORMATS', ['jpeg', 'jpg', 'png', 'heic']),
        environment=environment,
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        default_user_role=os.getenv('DEFAULT_USER_ROLE', 'HR_User')
    )
    
    # Validate configuration
    _validate_config(config)
    
    return config


def _get_api_base_url(environment: str) -> str:
    """
    Get API base URL with environment-specific defaults.
    
    Args:
        environment: Current environment (development, staging, production)
    
    Returns:
        API base URL
    """
    # Check if explicitly set in environment
    if 'API_BASE_URL' in os.environ:
        return os.getenv('API_BASE_URL')
    
    # Environment-specific defaults
    defaults = {
        'development': 'http://localhost:8000',
        'staging': 'https://staging-api.gatepass.example.com',
        'production': 'https://api.gatepass.example.com'
    }
    
    return defaults.get(environment, defaults['development'])


def _get_int_env(key: str, default: int) -> int:
    """
    Get integer value from environment variable.
    
    Args:
        key: Environment variable key
        default: Default value if not set
    
    Returns:
        Integer value
    
    Raises:
        ValueError: If value cannot be converted to integer
    """
    value = os.getenv(key)
    if value is None:
        return default
    
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid integer value for {key}: {value}")


def _get_list_env(key: str, default: List[str]) -> List[str]:
    """
    Get list value from environment variable (comma-separated).
    
    Args:
        key: Environment variable key
        default: Default value if not set
    
    Returns:
        List of strings
    """
    value = os.getenv(key)
    if value is None:
        return default
    
    # Split by comma and strip whitespace
    return [item.strip() for item in value.split(',') if item.strip()]


def _load_env_file(env_file: Path) -> None:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file
    """
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
    except Exception as e:
        # Silently fail if .env file cannot be read
        pass


def _validate_config(config: Config) -> None:
    """
    Validate configuration values.
    
    Args:
        config: Config object to validate
    
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate API base URL
    if not config.api_base_url:
        raise ValueError("API_BASE_URL is required")
    
    if not config.api_base_url.startswith(('http://', 'https://')):
        raise ValueError(f"Invalid API_BASE_URL: {config.api_base_url}. Must start with http:// or https://")
    
    # Validate API timeout
    if config.api_timeout <= 0:
        raise ValueError(f"Invalid API_TIMEOUT: {config.api_timeout}. Must be positive")
    
    # Validate max file size
    if config.max_file_size <= 0:
        raise ValueError(f"Invalid MAX_FILE_SIZE: {config.max_file_size}. Must be positive")
    
    # Validate allowed file formats
    if not config.allowed_file_formats:
        raise ValueError("ALLOWED_FILE_FORMATS cannot be empty")
    
    # Validate environment
    valid_environments = ['development', 'staging', 'production']
    if config.environment not in valid_environments:
        raise ValueError(
            f"Invalid ENVIRONMENT: {config.environment}. "
            f"Must be one of: {', '.join(valid_environments)}"
        )
    
    # Validate default user role
    valid_roles = ['HR_User', 'Admin_User', 'Gate_User']
    if config.default_user_role not in valid_roles:
        raise ValueError(
            f"Invalid DEFAULT_USER_ROLE: {config.default_user_role}. "
            f"Must be one of: {', '.join(valid_roles)}"
        )


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    This function loads the configuration on first call and caches it
    for subsequent calls.
    
    Returns:
        Config object with loaded configuration
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config() -> None:
    """
    Reset the global configuration instance.
    
    This is useful for testing when you need to reload configuration
    with different environment variables.
    """
    global _config
    _config = None
