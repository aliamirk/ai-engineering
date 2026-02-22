"""
Unit tests for file handling utilities.
"""

import os
import tempfile
import pytest
from pathlib import Path

from core.file_handler import (
    FileValidationError,
    validate_file_format,
    validate_file_size,
    prepare_multipart_data,
)


class TestValidateFileFormat:
    """Tests for validate_file_format function."""
    
    def test_valid_jpeg_format(self, tmp_path):
        """Test that JPEG files are accepted."""
        file_path = tmp_path / "test.jpeg"
        file_path.touch()
        
        assert validate_file_format(str(file_path)) is True
    
    def test_valid_jpg_format(self, tmp_path):
        """Test that JPG files are accepted."""
        file_path = tmp_path / "test.jpg"
        file_path.touch()
        
        assert validate_file_format(str(file_path)) is True
    
    def test_valid_png_format(self, tmp_path):
        """Test that PNG files are accepted."""
        file_path = tmp_path / "test.png"
        file_path.touch()
        
        assert validate_file_format(str(file_path)) is True
    
    def test_valid_heic_format(self, tmp_path):
        """Test that HEIC files are accepted."""
        file_path = tmp_path / "test.heic"
        file_path.touch()
        
        assert validate_file_format(str(file_path)) is True
    
    def test_case_insensitive_format(self, tmp_path):
        """Test that format validation is case-insensitive."""
        file_path = tmp_path / "test.JPEG"
        file_path.touch()
        
        assert validate_file_format(str(file_path)) is True
    
    def test_invalid_format(self, tmp_path):
        """Test that invalid formats are rejected."""
        file_path = tmp_path / "test.gif"
        file_path.touch()
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_format(str(file_path))
        
        assert "Invalid file format: gif" in str(exc_info.value)
        assert "jpeg, jpg, png, heic" in str(exc_info.value)
    
    def test_no_extension(self, tmp_path):
        """Test that files without extension are rejected."""
        file_path = tmp_path / "test"
        file_path.touch()
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_format(str(file_path))
        
        assert "no extension" in str(exc_info.value)
    
    def test_custom_allowed_formats(self, tmp_path):
        """Test validation with custom allowed formats."""
        file_path = tmp_path / "test.gif"
        file_path.touch()
        
        # Should pass with custom formats
        assert validate_file_format(str(file_path), allowed_formats=['gif', 'bmp']) is True
        
        # Should fail with default formats
        with pytest.raises(FileValidationError):
            validate_file_format(str(file_path))


class TestValidateFileSize:
    """Tests for validate_file_size function."""
    
    def test_file_within_size_limit(self, tmp_path):
        """Test that files within size limit are accepted."""
        file_path = tmp_path / "test.jpg"
        
        # Create a 1MB file
        with open(file_path, 'wb') as f:
            f.write(b'0' * (1024 * 1024))
        
        # Should pass with 5MB limit
        assert validate_file_size(str(file_path), max_size_bytes=5 * 1024 * 1024) is True
    
    def test_file_at_size_limit(self, tmp_path):
        """Test that files exactly at size limit are accepted."""
        file_path = tmp_path / "test.jpg"
        max_size = 1024 * 1024  # 1MB
        
        # Create a file exactly at the limit
        with open(file_path, 'wb') as f:
            f.write(b'0' * max_size)
        
        assert validate_file_size(str(file_path), max_size_bytes=max_size) is True
    
    def test_file_exceeds_size_limit(self, tmp_path):
        """Test that files exceeding size limit are rejected."""
        file_path = tmp_path / "test.jpg"
        max_size = 1024 * 1024  # 1MB
        
        # Create a file larger than the limit
        with open(file_path, 'wb') as f:
            f.write(b'0' * (max_size + 1))
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_size(str(file_path), max_size_bytes=max_size)
        
        assert "exceeds maximum allowed size" in str(exc_info.value)
        assert "1.00MB" in str(exc_info.value)
    
    def test_default_size_limit(self, tmp_path):
        """Test that default size limit is 5MB."""
        file_path = tmp_path / "test.jpg"
        
        # Create a 6MB file
        with open(file_path, 'wb') as f:
            f.write(b'0' * (6 * 1024 * 1024))
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_size(str(file_path))
        
        assert "5.00MB" in str(exc_info.value)
    
    def test_file_not_found(self):
        """Test that non-existent files raise an error."""
        with pytest.raises(FileValidationError) as exc_info:
            validate_file_size("/nonexistent/file.jpg")
        
        assert "File not found" in str(exc_info.value)
    
    def test_empty_file(self, tmp_path):
        """Test that empty files are accepted."""
        file_path = tmp_path / "test.jpg"
        file_path.touch()
        
        assert validate_file_size(str(file_path)) is True


class TestPrepareMultipartData:
    """Tests for prepare_multipart_data function."""
    
    def test_prepare_valid_file(self, tmp_path):
        """Test preparing multipart data with valid file."""
        file_path = tmp_path / "test.jpg"
        file_content = b'fake image content'
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        data, files = prepare_multipart_data("GP-2024-0001", str(file_path))
        
        # Check data dictionary
        assert data == {'pass_number': 'GP-2024-0001'}
        
        # Check files dictionary
        assert 'photo' in files
        filename, content, content_type = files['photo']
        assert filename == 'test.jpg'
        assert content == file_content
        assert content_type == 'image/jpeg'
    
    def test_prepare_png_file(self, tmp_path):
        """Test preparing multipart data with PNG file."""
        file_path = tmp_path / "test.png"
        file_content = b'fake png content'
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        data, files = prepare_multipart_data("GP-2024-0002", str(file_path))
        
        filename, content, content_type = files['photo']
        assert content_type == 'image/png'
    
    def test_prepare_heic_file(self, tmp_path):
        """Test preparing multipart data with HEIC file."""
        file_path = tmp_path / "test.heic"
        file_content = b'fake heic content'
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        data, files = prepare_multipart_data("GP-2024-0003", str(file_path))
        
        filename, content, content_type = files['photo']
        assert content_type == 'image/heic'
    
    def test_prepare_invalid_format(self, tmp_path):
        """Test that invalid file format raises error."""
        file_path = tmp_path / "test.gif"
        file_path.touch()
        
        with pytest.raises(FileValidationError) as exc_info:
            prepare_multipart_data("GP-2024-0004", str(file_path))
        
        assert "Invalid file format" in str(exc_info.value)
    
    def test_prepare_oversized_file(self, tmp_path):
        """Test that oversized file raises error."""
        file_path = tmp_path / "test.jpg"
        
        # Create a 6MB file
        with open(file_path, 'wb') as f:
            f.write(b'0' * (6 * 1024 * 1024))
        
        with pytest.raises(FileValidationError) as exc_info:
            prepare_multipart_data("GP-2024-0005", str(file_path))
        
        assert "exceeds maximum allowed size" in str(exc_info.value)
    
    def test_prepare_with_custom_limits(self, tmp_path):
        """Test preparing with custom size and format limits."""
        file_path = tmp_path / "test.jpg"
        file_content = b'0' * (2 * 1024 * 1024)  # 2MB
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Should pass with 3MB limit
        data, files = prepare_multipart_data(
            "GP-2024-0006",
            str(file_path),
            max_size_bytes=3 * 1024 * 1024,
            allowed_formats=['jpg', 'jpeg']
        )
        
        assert data['pass_number'] == 'GP-2024-0006'
        assert 'photo' in files
    
    def test_prepare_preserves_filename(self, tmp_path):
        """Test that original filename is preserved."""
        file_path = tmp_path / "my_photo_2024.jpeg"
        file_path.write_bytes(b'content')
        
        data, files = prepare_multipart_data("GP-2024-0007", str(file_path))
        
        filename, _, _ = files['photo']
        assert filename == 'my_photo_2024.jpeg'
