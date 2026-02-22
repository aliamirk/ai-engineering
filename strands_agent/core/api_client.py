"""Gate Pass API Client for HTTP communication with the Gate Pass Management API."""

import time
from typing import Any, Dict, Optional
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

from .models import APIResponse


class GatePassAPIClient:
    """HTTP client for Gate Pass Management API with retry logic and error handling."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize API client with base URL and timeout.
        
        Args:
            base_url: Base URL for the Gate Pass API (e.g., "https://api.example.com")
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = 3
        self.retry_delays = [2, 4, 8]  # Exponential backoff delays in seconds
    
    def handle_error(self, status_code: int, response_body: Optional[Dict[str, Any]] = None) -> str:
        """Convert HTTP status codes to user-friendly error messages.
        
        Args:
            status_code: HTTP status code from the API response
            response_body: Optional response body containing additional error details
            
        Returns:
            User-friendly error message with context-specific guidance
        """
        # Extract additional error details from response body if available
        detail = ""
        if response_body and isinstance(response_body, dict):
            detail = response_body.get('detail', response_body.get('message', ''))
            if detail:
                detail = f" Details: {detail}"
        
        # Map status codes to user-friendly messages
        if status_code == 400:
            return (
                f"Invalid request format or parameters.{detail} "
                "Please check that all required fields are provided with valid values."
            )
        elif status_code == 403:
            return (
                f"Operation not permitted for current gate pass state.{detail} "
                "The gate pass may need to be in a different status (e.g., approved, pending) "
                "to perform this operation. Check the gate pass status and try again."
            )
        elif status_code == 404:
            return (
                f"Gate pass or resource does not exist.{detail} "
                "Please verify the gate pass number or ID is correct. "
                "You can list available gate passes to find the correct identifier."
            )
        elif status_code == 422:
            return (
                f"Validation errors on input data.{detail} "
                "One or more fields contain invalid values. "
                "Please check the format and constraints for each field and try again."
            )
        elif status_code == 500:
            return (
                f"Server-side error occurred.{detail} "
                "This is an internal server error. Please try again later. "
                "If the problem persists, contact system support."
            )
        else:
            return f"Unexpected error (HTTP {status_code}).{detail}"
    
    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Execute HTTP request with exponential backoff retry logic.
        
        Args:
            method: HTTP method (GET or POST)
            endpoint: API endpoint path (e.g., "/hr/gatepass/create")
            params: Query parameters for GET requests
            json_data: JSON body for POST requests
            files: Files for multipart form data uploads
            
        Returns:
            APIResponse object with success status, status code, data, and error
        """
        method = method.upper()
        if method not in ['GET', 'POST']:
            return APIResponse(
                success=False,
                status_code=0,
                error=f"Unsupported HTTP method: {method}"
            )
        
        url = f"{self.base_url}{endpoint}"
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Make the HTTP request
                if method == 'GET':
                    response = requests.get(
                        url,
                        params=params,
                        timeout=self.timeout
                    )
                else:  # POST
                    if files:
                        # Multipart form data request
                        response = requests.post(
                            url,
                            data=params,  # Form data goes in data parameter
                            files=files,
                            timeout=self.timeout
                        )
                    else:
                        # JSON request
                        response = requests.post(
                            url,
                            json=json_data,
                            timeout=self.timeout
                        )
                
                # Check if request was successful
                if response.status_code >= 200 and response.status_code < 300:
                    try:
                        data = response.json()
                    except ValueError:
                        # Response is not JSON, return raw content
                        data = response.content
                    
                    return APIResponse(
                        success=True,
                        status_code=response.status_code,
                        data=data
                    )
                else:
                    # API returned an error status code
                    try:
                        error_data = response.json()
                    except ValueError:
                        error_data = None
                    
                    # Use handle_error to create user-friendly error message
                    error_message = self.handle_error(response.status_code, error_data)
                    
                    return APIResponse(
                        success=False,
                        status_code=response.status_code,
                        error=error_message,
                        data=error_data
                    )
            
            except Timeout:
                # Timeout error - retry with exponential backoff
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    time.sleep(delay)
                    continue
                else:
                    return APIResponse(
                        success=False,
                        status_code=0,
                        error=f"Request timeout after {self.max_retries} attempts"
                    )
            
            except ConnectionError:
                # Connection error - retry with exponential backoff
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    time.sleep(delay)
                    continue
                else:
                    return APIResponse(
                        success=False,
                        status_code=0,
                        error=f"Connection error after {self.max_retries} attempts"
                    )
            
            except RequestException as e:
                # Other request exceptions - retry with exponential backoff
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    time.sleep(delay)
                    continue
                else:
                    return APIResponse(
                        success=False,
                        status_code=0,
                        error=f"Request failed after {self.max_retries} attempts: {str(e)}"
                    )
        
        # Should not reach here, but just in case
        return APIResponse(
            success=False,
            status_code=0,
            error="Unexpected error in request execution"
        )
