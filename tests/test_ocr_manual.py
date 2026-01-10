"""
Manual test script for OCR service.
Run with: python test_ocr_manual.py
"""
import asyncio
import sys
from io import BytesIO
from fastapi import UploadFile
from unittest.mock import AsyncMock, patch

# Add project root to path
sys.path.insert(0, '.')

from app.services.ocr_service import ocr_service
from app.adapters.gemini_adapter import GeminiError


async def test_ocr_extraction():
    """Test OCR extraction with mock data."""
    print("=" * 60)
    print("Testing OCR Service")
    print("=" * 60)
    
    # Test 1: PDF file
    print("\n[Test 1] Testing PDF extraction...")
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
    pdf_file = UploadFile(
        filename="test_resume.pdf",
        file=BytesIO(pdf_content),
        headers={"content-type": "application/pdf"}
    )
    
    mock_extracted_text = """
    John Doe
    Software Engineer
    Email: john.doe@example.com
    Phone: +1-234-567-8900
    
    Experience:
    - Senior Developer at Tech Corp (2020-2024)
    - Software Engineer at Startup Inc (2018-2020)
    
    Skills: Python, JavaScript, React, Node.js
    """
    
    try:
        with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
            mock_vision.return_value = mock_extracted_text
            
            result = await ocr_service.extract_text(pdf_file)
            
            assert result == mock_extracted_text.strip()
            assert len(result) > 10
            print("[OK] PDF extraction test passed")
            print(f"  Extracted {len(result)} characters")
    except Exception as e:
        print(f"[FAIL] PDF extraction test failed: {e}")
        return False
    
    # Test 2: Image file
    print("\n[Test 2] Testing image extraction...")
    jpeg_content = b"\xFF\xD8\xFF\xE0\x00\x10JFIF"
    image_file = UploadFile(
        filename="test_image.jpg",
        file=BytesIO(jpeg_content),
        headers={"content-type": "image/jpeg"}
    )
    
    try:
        with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
            mock_vision.return_value = "Extracted text from image"
            
            result = await ocr_service.extract_text(image_file)
            
            assert result == "Extracted text from image"
            print("[OK] Image extraction test passed")
    except Exception as e:
        print(f"[FAIL] Image extraction test failed: {e}")
        return False
    
    # Test 3: Unsupported file type
    print("\n[Test 3] Testing unsupported file type...")
    unsupported_file = UploadFile(
        filename="test.zip",
        file=BytesIO(b"PK\x03\x04"),
        headers={"content-type": "application/zip"}
    )
    
    try:
        await ocr_service.extract_text(unsupported_file)
        print("[FAIL] Should have raised an error for unsupported file type")
        return False
    except Exception as e:
        if "Unsupported" in str(e) or "unsupported" in str(e).lower():
            print("[OK] Unsupported file type correctly rejected")
        else:
            print(f"[FAIL] Wrong error type: {e}")
            return False
    
    # Test 4: Empty file
    print("\n[Test 4] Testing empty file...")
    empty_file = UploadFile(
        filename="empty.pdf",
        file=BytesIO(b""),
        headers={"content-type": "application/pdf"}
    )
    
    try:
        await ocr_service.extract_text(empty_file)
        print("[FAIL] Should have raised an error for empty file")
        return False
    except Exception as e:
        if "empty" in str(e).lower() or "Empty" in str(e):
            print("[OK] Empty file correctly rejected")
        else:
            print(f"[FAIL] Wrong error type: {e}")
            return False
    
    # Test 5: No text extracted
    print("\n[Test 5] Testing empty text extraction...")
    pdf_file2 = UploadFile(
        filename="test.pdf",
        file=BytesIO(pdf_content),
        headers={"content-type": "application/pdf"}
    )
    
    try:
        with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
            mock_vision.return_value = ""  # Empty response
            
            await ocr_service.extract_text(pdf_file2)
            print("[FAIL] Should have raised an error for empty text")
            return False
    except Exception as e:
        if "No text" in str(e) or "empty" in str(e).lower():
            print("[OK] Empty text extraction correctly rejected")
        else:
            print(f"[FAIL] Wrong error type: {e}")
            return False
    
    # Test 6: Gemini API error
    print("\n[Test 6] Testing Gemini API error handling...")
    pdf_file3 = UploadFile(
        filename="test.pdf",
        file=BytesIO(pdf_content),
        headers={"content-type": "application/pdf"}
    )
    
    try:
        with patch('app.services.ocr_service.gemini_adapter.vision_to_text', new_callable=AsyncMock) as mock_vision:
            mock_vision.side_effect = GeminiError("API quota exceeded")
            
            await ocr_service.extract_text(pdf_file3)
            print("[FAIL] Should have raised an error for API error")
            return False
    except Exception as e:
        if "OCR" in str(e) or "error" in str(e).lower():
            print("[OK] API error correctly handled")
        else:
            print(f"[FAIL] Wrong error type: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("All tests passed! [OK]")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_ocr_extraction())
    sys.exit(0 if success else 1)
