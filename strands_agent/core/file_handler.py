"""
File handling utilities for Gate Pass AI Agent.

This module provides functions for validating and preparing file uploads
for gate scanning operations.
"""

import os
from typing import Dict, Tuple, Optional
from pathlib import Path


class FileValidationError(Exception):
    """Exception raised when file validation fails."""
    pass


def validate_file_format(file_path: str, allowed_formats: Optional[list] = None) -> bool:
    """
    Validate that a file is in an allowed image format.
    
    Args:
        file_path: Path to the file to validate
        allowed_formats: List of allowed file extensions (default: ['jpeg', 'jpg', 'png', 'heic'])
    
    Returns:
        True if file format is valid
    
    Raises:
        FileValidationError: If file format is not allowed
    """
    if allowed_formats is None:
        allowed_formats = ['jpeg', 'jpg', 'png', 'heic']
    
    # Normalize formats to lowercase
    allowed_formats = [fmt.lower() for fmt in allowed_formats]
    
    # Get file extension
    file_extension = Path(file_path).suffix.lstrip('.').lower()
    
    if not file_extension:
        raise FileValidationError("File has no extension")
    
    if file_extension not in allowed_formats:
        raise FileValidationError(
            f"Invalid file format: {file_extension}. "
            f"Allowed formats: {', '.join(allowed_formats)}"
        )
    
    return True


def validate_file_size(file_path: str, max_size_bytes: int = 5242880) -> bool:
    """
    Validate that a file does not exceed the maximum size limit.
    
    Args:
        file_path: Path to the file to validate
        max_size_bytes: Maximum allowed file size in bytes (default: 5MB = 5242880 bytes)
    
    Returns:
        True if file size is valid
    
    Raises:
        FileValidationError: If file size exceeds the limit
    """
    if not os.path.exists(file_path):
        raise FileValidationError(f"File not found: {file_path}")
    
    file_size = os.path.getsize(file_path)
    
    if file_size > max_size_bytes:
        max_size_mb = max_size_bytes / (1024 * 1024)
        actual_size_mb = file_size / (1024 * 1024)
        raise FileValidationError(
            f"File size ({actual_size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb:.2f}MB)"
        )
    
    return True


def prepare_multipart_data(
    pass_number: str,
    file_path: str,
    max_size_bytes: int = 5242880,
    allowed_formats: Optional[list] = None
) -> Tuple[Dict[str, str], Dict[str, Tuple[str, bytes, str]]]:
    """
    Prepare multipart form data for gate scan API requests.
    
    This function validates the file and prepares it in the format required
    for multipart/form-data HTTP requests.
    
    Args:
        pass_number: The gate pass number
        file_path: Path to the photo file
        max_size_bytes: Maximum allowed file size in bytes (default: 5MB)
        allowed_formats: List of allowed file extensions (default: ['jpeg', 'jpg', 'png', 'heic'])
    
    Returns:
        Tuple of (data_dict, files_dict) where:
        - data_dict contains the pass_number field
        - files_dict contains the photo file in format: {'photo': (filename, file_bytes, content_type)}
    
    Raises:
        FileValidationError: If file validation fails
    """
    # Validate file format
    validate_file_format(file_path, allowed_formats)
    
    # Validate file size
    validate_file_size(file_path, max_size_bytes)
    
    # Read file content
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Get filename and determine content type
    filename = os.path.basename(file_path)
    file_extension = Path(file_path).suffix.lstrip('.').lower()
    
    # Map file extensions to MIME types
    content_type_map = {
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'png': 'image/png',
        'heic': 'image/heic'
    }
    content_type = content_type_map.get(file_extension, 'application/octet-stream')
    
    # Prepare data and files dictionaries
    data = {'pass_number': pass_number}
    files = {'photo': (filename, file_content, content_type)}
    
    return data, files
