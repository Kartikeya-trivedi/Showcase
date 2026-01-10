"""
Test script for PyMuPDF text extraction.
Run this to verify PDF text extraction works before testing the full API.
"""
import sys
import os
from pathlib import Path
from io import BytesIO

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_pymupdf_import():
    """Test if PyMuPDF is installed."""
    try:
        import fitz
        print(f"[OK] PyMuPDF imported successfully")
        print(f"     Version: {fitz.version}")
        return True
    except ImportError:
        print("[ERROR] PyMuPDF (fitz) is not installed")
        print("     Install it with: pip install pymupdf")
        return False

def test_pdf_extraction(pdf_path: str):
    """Test extracting text from a PDF file."""
    try:
        import fitz
        
        # Clean up path: remove quotes and normalize
        pdf_path = pdf_path.strip().strip('"').strip("'")
        pdf_path = os.path.normpath(pdf_path)
        
        if not os.path.exists(pdf_path):
            print(f"[ERROR] PDF file not found: {pdf_path}")
            print(f"        Current directory: {os.getcwd()}")
            print(f"        Please check the path and try again")
            return False
        
        print(f"\n[TEST] Extracting text from: {pdf_path}")
        
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        print(f"     File size: {len(pdf_bytes) / 1024:.2f} KB")
        
        # Open PDF from bytes (same way the service does it)
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        print(f"     Pages: {pdf_document.page_count}")
        
        if pdf_document.page_count == 0:
            print("[ERROR] PDF has no pages")
            pdf_document.close()
            return False
        
        # Extract text from all pages
        text_parts = []
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(page_text)
                print(f"     Page {page_num + 1}: {len(page_text)} characters")
        
        pdf_document.close()
        
        if not text_parts:
            print("[ERROR] No text found in PDF")
            return False
        
        extracted_text = "\n\n".join(text_parts)
        
        print(f"\n[OK] Text extraction successful!")
        print(f"     Total characters: {len(extracted_text)}")
        print(f"     Total words: {len(extracted_text.split())}")
        
        # Show preview
        preview = extracted_text[:500].replace('\n', ' ')
        print(f"\n[PREVIEW] First 500 characters:")
        print(f"     {preview}...")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] PDF extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ocr_service():
    """Test the OCR service with a mock file."""
    try:
        from app.services.ocr_service import ocr_service
        from fastapi import UploadFile
        from io import BytesIO
        
        print("\n[TEST] Testing OCR service with mock PDF...")
        
        # You need to provide a test PDF file
        test_pdf_path = input("\nEnter path to a test PDF file (or press Enter to skip): ").strip()
        
        if not test_pdf_path:
            print("[SKIP] No PDF file provided, skipping service test")
            return True
        
        # Clean up path
        test_pdf_path = test_pdf_path.strip('"').strip("'")
        test_pdf_path = os.path.normpath(test_pdf_path)
        
        if not os.path.exists(test_pdf_path):
            print(f"[ERROR] File not found: {test_pdf_path}")
            print(f"        Current directory: {os.getcwd()}")
            return False
        
        # Read PDF
        with open(test_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        # Create mock UploadFile
        file = UploadFile(
            filename=os.path.basename(test_pdf_path),
            file=BytesIO(pdf_bytes),
            headers={"content-type": "application/pdf"}
        )
        
        print(f"     File: {file.filename}")
        print(f"     Size: {len(pdf_bytes) / 1024:.2f} KB")
        
        # Test extraction (this is async, so we need to run it)
        import asyncio
        
        async def run_test():
            try:
                extracted_text = await ocr_service.extract_text(file)
                print(f"\n[OK] OCR service test successful!")
                print(f"     Extracted {len(extracted_text)} characters")
                print(f"\n[PREVIEW] First 500 characters:")
                preview = extracted_text[:500].replace('\n', ' ')
                print(f"     {preview}...")
                return True
            except Exception as e:
                print(f"[ERROR] OCR service test failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        return asyncio.run(run_test())
        
    except Exception as e:
        print(f"[ERROR] OCR service test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 70)
    print("PyMuPDF Text Extraction Test")
    print("=" * 70)
    
    # Test 1: Import
    if not test_pymupdf_import():
        print("\n[STOP] Cannot continue without PyMuPDF")
        return
    
    # Test 2: Direct PDF extraction (if file provided)
    print("\n" + "=" * 70)
    print("Test 1: Direct PyMuPDF Extraction")
    print("=" * 70)
    
    test_pdf = input("\nEnter path to a test PDF file (or press Enter to skip): ").strip()
    
    if test_pdf:
        # Clean up path
        test_pdf = test_pdf.strip('"').strip("'")
        if not test_pdf_extraction(test_pdf):
            print("\n[FAIL] Direct extraction test failed")
            return
    else:
        print("[SKIP] No PDF file provided")
    
    # Test 3: OCR Service
    print("\n" + "=" * 70)
    print("Test 2: OCR Service Integration")
    print("=" * 70)
    
    # Check if we can import the service
    try:
        from app.services.ocr_service import ocr_service
        print("[OK] OCR service imported successfully")
        
        # Ask if user wants to test the service
        test_service = input("\nTest OCR service with a PDF? (y/n): ").strip().lower()
        if test_service == 'y':
            test_ocr_service()
        else:
            print("[SKIP] Service test skipped")
            
    except Exception as e:
        print(f"[ERROR] Could not import OCR service: {e}")
        print("     Make sure you're running from the project root")
    
    print("\n" + "=" * 70)
    print("Testing Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Start your server: uvicorn app.main:app --reload")
    print("2. Upload a PDF resume via the API")
    print("3. Check job status: python check_database.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[STOP] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
