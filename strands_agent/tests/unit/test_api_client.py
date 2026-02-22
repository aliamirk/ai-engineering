"""Unit tests for GatePassAPIClient."""

import pytest
import responses
from requests.exceptions import Timeout, ConnectionError
from strands_agent.core.api_client import GatePassAPIClient, APIResponse


class TestGatePassAPIClient:
    """Test suite for GatePassAPIClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.base_url = "https://api.example.com"
        self.client = GatePassAPIClient(base_url=self.base_url, timeout=5)
    
    @responses.activate
    def test_successful_get_request(self):
        """Test successful GET request returns data."""
        responses.add(
            responses.GET,
            f"{self.base_url}/test/endpoint",
            json={"result": "success", "data": "test_data"},
            status=200
        )
        
        response = self.client.request("GET", "/test/endpoint")
        
        assert response.success is True
        assert response.status_code == 200
        assert response.data == {"result": "success", "data": "test_data"}
        assert response.error is None
    
    @responses.activate
    def test_successful_post_request_with_json(self):
        """Test successful POST request with JSON data."""
        responses.add(
            responses.POST,
            f"{self.base_url}/test/create",
            json={"id": "123", "status": "created"},
            status=201
        )
        
        response = self.client.request(
            "POST",
            "/test/create",
            json_data={"name": "test", "value": "data"}
        )
        
        assert response.success is True
        assert response.status_code == 201
        assert response.data == {"id": "123", "status": "created"}
    
    @responses.activate
    def test_get_request_with_params(self):
        """Test GET request with query parameters."""
        responses.add(
            responses.GET,
            f"{self.base_url}/test/list",
            json={"items": []},
            status=200
        )
        
        response = self.client.request(
            "GET",
            "/test/list",
            params={"status": "pending", "limit": 10}
        )
        
        assert response.success is True
        assert len(responses.calls) == 1
        assert "status=pending" in responses.calls[0].request.url
        assert "limit=10" in responses.calls[0].request.url
    
    @responses.activate
    def test_post_request_with_files(self):
        """Test POST request with multipart form data."""
        responses.add(
            responses.POST,
            f"{self.base_url}/test/upload",
            json={"uploaded": True},
            status=200
        )
        
        files = {"photo": ("test.jpg", b"fake_image_data", "image/jpeg")}
        response = self.client.request(
            "POST",
            "/test/upload",
            params={"pass_number": "GP-2024-0001"},
            files=files
        )
        
        assert response.success is True
        assert response.data == {"uploaded": True}
    
    @responses.activate
    def test_api_error_response(self):
        """Test handling of API error responses."""
        responses.add(
            responses.GET,
            f"{self.base_url}/test/notfound",
            json={"error": "Resource not found"},
            status=404
        )
        
        response = self.client.request("GET", "/test/notfound")
        
        assert response.success is False
        assert response.status_code == 404
        # Now uses user-friendly error message from handle_error
        assert "does not exist" in response.error
        assert "verify" in response.error
    
    @responses.activate
    def test_validation_error_response(self):
        """Test handling of validation error (422)."""
        responses.add(
            responses.POST,
            f"{self.base_url}/test/create",
            json={"message": "Validation failed", "errors": {"name": "required"}},
            status=422
        )
        
        response = self.client.request("POST", "/test/create", json_data={})
        
        assert response.success is False
        assert response.status_code == 422
        assert "Validation failed" in response.error
    
    @responses.activate
    def test_timeout_with_retry(self):
        """Test timeout handling with exponential backoff retry."""
        # All attempts will timeout
        responses.add(
            responses.GET,
            f"{self.base_url}/test/slow",
            body=Timeout()
        )
        responses.add(
            responses.GET,
            f"{self.base_url}/test/slow",
            body=Timeout()
        )
        responses.add(
            responses.GET,
            f"{self.base_url}/test/slow",
            body=Timeout()
        )
        
        response = self.client.request("GET", "/test/slow")
        
        assert response.success is False
        assert response.status_code == 0
        assert "timeout" in response.error.lower()
        assert "3 attempts" in response.error
        assert len(responses.calls) == 3
    
    @responses.activate
    def test_connection_error_with_retry(self):
        """Test connection error handling with exponential backoff retry."""
        # All attempts will fail with connection error
        responses.add(
            responses.GET,
            f"{self.base_url}/test/unreachable",
            body=ConnectionError()
        )
        responses.add(
            responses.GET,
            f"{self.base_url}/test/unreachable",
            body=ConnectionError()
        )
        responses.add(
            responses.GET,
            f"{self.base_url}/test/unreachable",
            body=ConnectionError()
        )
        
        response = self.client.request("GET", "/test/unreachable")
        
        assert response.success is False
        assert response.status_code == 0
        assert "connection error" in response.error.lower()
        assert "3 attempts" in response.error
        assert len(responses.calls) == 3
    
    @responses.activate
    def test_retry_success_on_second_attempt(self):
        """Test successful retry after initial failure."""
        # First attempt times out, second succeeds
        responses.add(
            responses.GET,
            f"{self.base_url}/test/flaky",
            body=Timeout()
        )
        responses.add(
            responses.GET,
            f"{self.base_url}/test/flaky",
            json={"result": "success"},
            status=200
        )
        
        response = self.client.request("GET", "/test/flaky")
        
        assert response.success is True
        assert response.status_code == 200
        assert response.data == {"result": "success"}
        assert len(responses.calls) == 2
    
    def test_unsupported_http_method(self):
        """Test handling of unsupported HTTP methods."""
        response = self.client.request("DELETE", "/test/endpoint")
        
        assert response.success is False
        assert response.status_code == 0
        assert "Unsupported HTTP method" in response.error
    
    @responses.activate
    def test_non_json_response(self):
        """Test handling of non-JSON responses."""
        responses.add(
            responses.GET,
            f"{self.base_url}/test/binary",
            body=b"binary_data",
            status=200,
            content_type="application/octet-stream"
        )
        
        response = self.client.request("GET", "/test/binary")
        
        assert response.success is True
        assert response.status_code == 200
        assert response.data == b"binary_data"
    
    @responses.activate
    def test_base_url_trailing_slash_handling(self):
        """Test that trailing slashes in base_url are handled correctly."""
        client_with_slash = GatePassAPIClient(base_url="https://api.example.com/", timeout=5)
        
        responses.add(
            responses.GET,
            "https://api.example.com/test",
            json={"result": "ok"},
            status=200
        )
        
        response = client_with_slash.request("GET", "/test")
        
        assert response.success is True
        assert len(responses.calls) == 1
    
    def test_initialization_with_custom_timeout(self):
        """Test client initialization with custom timeout."""
        client = GatePassAPIClient(base_url=self.base_url, timeout=60)
        
        assert client.timeout == 60
        assert client.base_url == self.base_url
        assert client.max_retries == 3
        assert client.retry_delays == [2, 4, 8]
    
    def test_initialization_with_default_timeout(self):
        """Test client initialization with default timeout."""
        client = GatePassAPIClient(base_url=self.base_url)
        
        assert client.timeout == 30


class TestHandleError:
    """Test suite for handle_error method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = GatePassAPIClient(base_url="https://api.example.com")
    
    def test_handle_error_400_bad_request(self):
        """Test error handling for 400 Bad Request."""
        error_msg = self.client.handle_error(400)
        
        assert "Invalid request format or parameters" in error_msg
        assert "required fields" in error_msg
        assert "valid values" in error_msg
    
    def test_handle_error_400_with_details(self):
        """Test error handling for 400 with response body details."""
        response_body = {"detail": "Missing required field: person_name"}
        error_msg = self.client.handle_error(400, response_body)
        
        assert "Invalid request format or parameters" in error_msg
        assert "Missing required field: person_name" in error_msg
    
    def test_handle_error_403_forbidden(self):
        """Test error handling for 403 Forbidden."""
        error_msg = self.client.handle_error(403)
        
        assert "Operation not permitted" in error_msg
        assert "gate pass state" in error_msg
        assert "status" in error_msg
    
    def test_handle_error_403_with_details(self):
        """Test error handling for 403 with response body details."""
        response_body = {"message": "Gate pass must be approved before scanning"}
        error_msg = self.client.handle_error(403, response_body)
        
        assert "Operation not permitted" in error_msg
        assert "Gate pass must be approved before scanning" in error_msg
    
    def test_handle_error_404_not_found(self):
        """Test error handling for 404 Not Found."""
        error_msg = self.client.handle_error(404)
        
        assert "does not exist" in error_msg
        assert "verify" in error_msg
        assert "gate pass number or ID" in error_msg
    
    def test_handle_error_404_with_details(self):
        """Test error handling for 404 with response body details."""
        response_body = {"detail": "Gate pass GP-2024-9999 not found"}
        error_msg = self.client.handle_error(404, response_body)
        
        assert "does not exist" in error_msg
        assert "GP-2024-9999 not found" in error_msg
    
    def test_handle_error_422_validation_error(self):
        """Test error handling for 422 Unprocessable Entity."""
        error_msg = self.client.handle_error(422)
        
        assert "Validation errors" in error_msg
        assert "invalid values" in error_msg
        assert "format and constraints" in error_msg
    
    def test_handle_error_422_with_details(self):
        """Test error handling for 422 with response body details."""
        response_body = {"detail": "person_name must be at least 2 characters"}
        error_msg = self.client.handle_error(422, response_body)
        
        assert "Validation errors" in error_msg
        assert "person_name must be at least 2 characters" in error_msg
    
    def test_handle_error_500_internal_server_error(self):
        """Test error handling for 500 Internal Server Error."""
        error_msg = self.client.handle_error(500)
        
        assert "Server-side error" in error_msg
        assert "try again later" in error_msg
        assert "contact system support" in error_msg
    
    def test_handle_error_500_with_details(self):
        """Test error handling for 500 with response body details."""
        response_body = {"message": "Database connection failed"}
        error_msg = self.client.handle_error(500, response_body)
        
        assert "Server-side error" in error_msg
        assert "Database connection failed" in error_msg
    
    def test_handle_error_unknown_status_code(self):
        """Test error handling for unknown status codes."""
        error_msg = self.client.handle_error(418)
        
        assert "Unexpected error" in error_msg
        assert "418" in error_msg
    
    def test_handle_error_with_non_dict_response_body(self):
        """Test error handling with non-dictionary response body."""
        error_msg = self.client.handle_error(400, "string error")
        
        assert "Invalid request format or parameters" in error_msg
        # Should not crash with non-dict response body
    
    def test_handle_error_with_none_response_body(self):
        """Test error handling with None response body."""
        error_msg = self.client.handle_error(404, None)
        
        assert "does not exist" in error_msg
        # Should handle None gracefully


class TestAPIResponseParsing:
    """Test suite for API response parsing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = GatePassAPIClient(base_url="https://api.example.com")
    
    @responses.activate
    def test_error_response_uses_handle_error(self):
        """Test that error responses use handle_error for user-friendly messages."""
        responses.add(
            responses.GET,
            "https://api.example.com/test/notfound",
            json={"detail": "Gate pass GP-2024-0001 not found"},
            status=404
        )
        
        response = self.client.request("GET", "/test/notfound")
        
        assert response.success is False
        assert response.status_code == 404
        assert "does not exist" in response.error
        assert "GP-2024-0001 not found" in response.error
        assert "verify" in response.error
    
    @responses.activate
    def test_validation_error_uses_handle_error(self):
        """Test that validation errors use handle_error for user-friendly messages."""
        responses.add(
            responses.POST,
            "https://api.example.com/test/create",
            json={"detail": "person_name is required"},
            status=422
        )
        
        response = self.client.request("POST", "/test/create", json_data={})
        
        assert response.success is False
        assert response.status_code == 422
        assert "Validation errors" in response.error
        assert "person_name is required" in response.error
    
    @responses.activate
    def test_forbidden_error_uses_handle_error(self):
        """Test that forbidden errors use handle_error for user-friendly messages."""
        responses.add(
            responses.POST,
            "https://api.example.com/test/approve",
            json={"message": "Gate pass must be in pending state"},
            status=403
        )
        
        response = self.client.request("POST", "/test/approve", json_data={})
        
        assert response.success is False
        assert response.status_code == 403
        assert "Operation not permitted" in response.error
        assert "Gate pass must be in pending state" in response.error
    
    @responses.activate
    def test_error_response_includes_data(self):
        """Test that error responses include the error data for further processing."""
        error_data = {
            "detail": "Validation failed",
            "errors": {
                "person_name": "required",
                "description": "too short"
            }
        }
        responses.add(
            responses.POST,
            "https://api.example.com/test/create",
            json=error_data,
            status=422
        )
        
        response = self.client.request("POST", "/test/create", json_data={})
        
        assert response.success is False
        assert response.status_code == 422
        assert response.data == error_data
        assert "Validation errors" in response.error
