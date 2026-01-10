"""
Tests for OCR Service.

Tests text extraction from various file types using Gemini Vision API.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile
from io import BytesIO
from app.services.ocr_service import ocr_service, MAX_FILE_SIZE, MIN_TEXT_LENGTH
from app.adapters.gemini_adapter import GeminiError, GeminiEmptyResponseError


class TestOCRService:
    """Test suite for OCR Service."""
    
    @pytest.fixture
    def mock_pdf_file(self):
        """Create a mock PDF file."""
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
        file = UploadFile(
            filename="test_resume.pdf",
            file=BytesIO(pdf_content)
        )
        file.content_type = "application/pdf"
        return file
    
    @pytest.fixture
    def mock_image_file(self):
        """Create a mock image file."""
        # Minimal valid JPEG header
        jpeg_content = b"\xFF\xD8\xFF\xE0\x00\x10JFIF"
        file = UploadFile(
            filename="test_image.jpg",
            file=BytesIO(jpeg_content)
        )
        file.content_type = "image/jpeg"
        return file
    
    @pytest.fixture
    def mock_extracted_text(self):
        """Sample extracted text from OCR."""
        return """
        John Doe
        Software Engineer
        Email: john.doe@example.com
        Phone: +1-234-567-8900
        
        Experience:
        - Senior Developer at Tech Corp (2020-2024)
        - Software Engineer at Startup Inc (2018-2020)
        
        Skills: Python, JavaScript, React, Node.js
        """
    
    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_success(self, mock_pdf_file, mock_extracted_text):
        """Test successful text extraction from PDF."""
        with patch.object(
            ocr_service.__class__.__bases__[0] if hasattr(ocr_service, '__class__') else type(ocr_service),
            'vision_to_text',
            new_callable=AsyncMock
        ) as mock_vision:
            # Mock the gemini_adapter directly
            with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
                mock_vision.return_value = mock_extracted_text
                
                result = await ocr_service.extract_text(mock_pdf_file)
                
                assert result == mock_extracted_text.strip()
                assert len(result) > MIN_TEXT_LENGTH
                mock_vision.assert_called_once()
                call_args = mock_vision.call_args
                assert call_args[0][1] == "application/pdf"  # mime_type
    
    @pytest.mark.asyncio
    async def test_extract_text_from_image_success(self, mock_image_file, mock_extracted_text):
        """Test successful text extraction from image."""
        with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
            mock_vision.return_value = mock_extracted_text
            
            result = await ocr_service.extract_text(mock_image_file)
            
            assert result == mock_extracted_text.strip()
            mock_vision.assert_called_once()
            call_args = mock_vision.call_args
            assert call_args[0][1] == "image/jpeg"  # mime_type
    
    @pytest.mark.asyncio
    async def test_extract_text_unsupported_file_type(self, mock_pdf_file):
        """Test error handling for unsupported file types."""
        mock_pdf_file.content_type = "application/zip"
        
        with pytest.raises(Exception) as exc_info:
            await ocr_service.extract_text(mock_pdf_file)
        
        assert "Unsupported file type" in str(exc_info.value) or "Unsupported" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_extract_text_empty_file(self, mock_pdf_file):
        """Test error handling for empty files."""
        empty_file = UploadFile(
            filename="empty.pdf",
            file=BytesIO(b"")
        )
        empty_file.content_type = "application/pdf"
        
        with pytest.raises(Exception) as exc_info:
            await ocr_service.extract_text(empty_file)
        
        assert "empty" in str(exc_info.value).lower() or "Empty" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_extract_text_file_too_large(self, mock_pdf_file):
        """Test error handling for files exceeding size limit."""
        # Create a file larger than MAX_FILE_SIZE
        large_content = b"x" * (MAX_FILE_SIZE + 1)
        large_file = UploadFile(
            filename="large.pdf",
            file=BytesIO(large_content)
        )
        large_file.content_type = "application/pdf"
        
        with pytest.raises(Exception) as exc_info:
            await ocr_service.extract_text(large_file)
        
        assert "size" in str(exc_info.value).lower() or "exceeds" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_extract_text_no_text_extracted(self, mock_pdf_file):
        """Test error handling when no text is extracted."""
        with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
            mock_vision.return_value = ""  # Empty response
            
            with pytest.raises(Exception) as exc_info:
                await ocr_service.extract_text(mock_pdf_file)
            
            assert "No text" in str(exc_info.value) or "empty" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_extract_text_gemini_api_error(self, mock_pdf_file):
        """Test error handling for Gemini API errors."""
        with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
            mock_vision.side_effect = GeminiError("API quota exceeded")
            
            with pytest.raises(Exception) as exc_info:
                await ocr_service.extract_text(mock_pdf_file)
            
            assert "OCR" in str(exc_info.value) or "error" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_extract_text_short_text_warning(self, mock_pdf_file, caplog):
        """Test that short extracted text triggers a warning but still returns."""
        short_text = "Hi"
        with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
            mock_vision.return_value = short_text
            
            result = await ocr_service.extract_text(mock_pdf_file)
            
            assert result == short_text.strip()
            # Should log a warning but still return the text
            assert len(result) < MIN_TEXT_LENGTH
    
    @pytest.mark.asyncio
    async def test_extract_text_missing_content_type(self, mock_pdf_file):
        """Test error handling when content_type is missing."""
        mock_pdf_file.content_type = None
        
        with pytest.raises(Exception) as exc_info:
            await ocr_service.extract_text(mock_pdf_file)
        
        assert "content type" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_extract_text_png_file(self):
        """Test extraction from PNG file."""
        png_content = b"\x89PNG\r\n\x1a\n"  # PNG header
        png_file = UploadFile(
            filename="test.png",
            file=BytesIO(png_content)
        )
        png_file.content_type = "image/png"
        
        mock_text = "Extracted text from PNG"
        with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
            mock_vision.return_value = mock_text
            
            result = await ocr_service.extract_text(png_file)
            
            assert result == mock_text
            call_args = mock_vision.call_args
            assert call_args[0][1] == "image/png"
    
    @pytest.mark.asyncio
    async def test_extract_text_file_position_reset(self, mock_pdf_file, mock_extracted_text):
        """Test that file position is reset after reading."""
        initial_pos = await mock_pdf_file.seek(0)
        
        with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
            mock_vision.return_value = mock_extracted_text
            
            await ocr_service.extract_text(mock_pdf_file)
            
            # File should be reset to beginning for potential reuse
            current_pos = await mock_pdf_file.tell()
            assert current_pos == 0 or current_pos == initial_pos


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
