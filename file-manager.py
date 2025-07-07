#!/usr/bin/env python3
"""
File Manager for Enhanced Playwright Automation
Handles file uploads, content extraction, and context management
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# File processing imports
try:
    import PyPDF2
    import docx
    from PIL import Image
    import pytesseract
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

class FileManager:
    """Manages file uploads and content extraction for automation context"""
    
    def __init__(self):
        self.uploaded_files: Dict[str, Dict[str, Any]] = {}
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    def save_uploaded_file(self, filename: str, content: bytes) -> str:
        """Save uploaded file and extract content"""
        # Create safe filename
        safe_filename = self._make_safe_filename(filename)
        file_path = self.upload_dir / safe_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Extract content based on file type
        file_info = self._extract_file_content(file_path)
        self.uploaded_files[safe_filename] = file_info
        
        return str(file_path)
    
    def _make_safe_filename(self, filename: str) -> str:
        """Create a safe filename with timestamp"""
        name = Path(filename).stem
        ext = Path(filename).suffix
        timestamp = int(time.time())
        return f"{name}_{timestamp}{ext}"
    
    def _extract_file_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract content from uploaded file"""
        file_info = {
            'path': str(file_path),
            'name': file_path.name,
            'size': file_path.stat().st_size,
            'type': self._get_file_type(file_path),
            'content': '',
            'upload_time': time.time()
        }
        
        try:
            if file_path.suffix.lower() == '.pdf':
                file_info['content'] = self._extract_pdf_content(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                file_info['content'] = self._extract_docx_content(file_path)
            elif file_path.suffix.lower() in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                file_info['content'] = self._extract_text_content(file_path)
            elif file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                file_info['content'] = self._extract_image_content(file_path)
            else:
                file_info['content'] = f"File type {file_path.suffix} not supported for content extraction"
        
        except Exception as e:
            file_info['content'] = f"Error extracting content: {str(e)}"
        
        return file_info
    
    def _get_file_type(self, file_path: Path) -> str:
        """Determine file type from extension"""
        ext = file_path.suffix.lower()
        if ext == '.pdf':
            return 'PDF Document'
        elif ext in ['.docx', '.doc']:
            return 'Word Document'
        elif ext in ['.txt', '.md']:
            return 'Text Document'
        elif ext in ['.py', '.js', '.html', '.css']:
            return 'Code File'
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            return 'Image File'
        else:
            return 'Unknown'
    
    def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        if not PDF_SUPPORT:
            return "PDF processing not available (PyPDF2 not installed)"
        
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def _extract_docx_content(self, file_path: Path) -> str:
        """Extract text from Word document"""
        if not PDF_SUPPORT:
            return "Word document processing not available (python-docx not installed)"
        
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            return f"Error reading Word document: {str(e)}"
    
    def _extract_text_content(self, file_path: Path) -> str:
        """Extract content from text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                return f"Error reading text file: {str(e)}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def _extract_image_content(self, file_path: Path) -> str:
        """Extract text from image using OCR"""
        if not PDF_SUPPORT:
            return "Image OCR not available (PIL/pytesseract not installed)"
        
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip() if text.strip() else "No text found in image"
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def get_file_context(self) -> str:
        """Get formatted context from all uploaded files"""
        if not self.uploaded_files:
            return "No files uploaded"
        
        context = "=== UPLOADED FILE CONTEXT ===\n\n"
        for filename, info in self.uploaded_files.items():
            context += f"File: {info['name']} ({info['type']})\n"
            context += f"Content:\n{info['content'][:1000]}...\n\n"
        
        return context
    
    def clear_files(self):
        """Clear all uploaded files"""
        self.uploaded_files.clear()
        # Optionally clean up upload directory
        try:
            for file_path in self.upload_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
        except Exception:
            pass  # Ignore cleanup errors
    
    def get_file_list(self) -> List[str]:
        """Get list of uploaded file names"""
        return list(self.uploaded_files.keys())
