"""
Document Parser for EditScribe
Supports .docx, .txt, .md, .pdf files
"""

from pathlib import Path
from docx import Document
import markdown
import re


class DocumentParser:
    """Parse various document formats into plain text"""
    
    @staticmethod
    def parse(file_path: str) -> str:
        """
        Parse document and return plain text.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Plain text content
        """
        ext = Path(file_path).suffix.lower()
        
        if ext == '.docx':
            doc = Document(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.pdf':
            return DocumentParser._parse_pdf(file_path)
        
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """Parse PDF with improved text extraction and cleanup"""
        try:
            # Try pdfminer first for better text extraction
            from pdfminer.high_level import extract_text
            text = extract_text(file_path)
            print(f"📄 PDF parsed with pdfminer: {len(text)} characters")
        except ImportError:
            # Fallback to pypdf
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text())
            text = '\n'.join(pages)
            print(f"📄 PDF parsed with pypdf: {len(text)} characters")
        except Exception as e:
            print(f"⚠️ PDF parsing error: {e}")
            # Final fallback
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text())
            text = '\n'.join(pages)
        
        # Clean up common PDF extraction issues
        text = DocumentParser._clean_pdf_text(text)
        
        return text
    
    @staticmethod
    def _clean_pdf_text(text: str) -> str:
        """Clean up common PDF text extraction issues"""
        
        # Fix common character substitutions from embedded fonts
        replacements = {
            'H': "'",  # Often H is substituted for apostrophe
            'x': '',   # Stray x characters
            '?': '',   # Question marks as garbage
            'O': '',   # O used as garbage character
            '': "'",   # Replacement character to apostrophe
            '＇': "'",  # Fullwidth apostrophe
            '"': '"',  # Smart quotes
            '"': '"',
            ''': "'",
            ''': "'",
            '–': '-',  # En dash
            '—': '-',  # Em dash
            '\x00': '', # Null characters
            '\ufeff': '', # BOM
        }
        
        # Only apply H-to-apostrophe replacement in specific contexts
        # H followed by s (possessive) or t (contractions like "don't")
        text = re.sub(r"(\w)H(s|t|m|re|ll|ve|d)\b", r"\1'\2", text)
        
        # Fix "coxee" -> "coffee" and similar OCR errors
        ocr_fixes = {
            r'\bcoxee\b': 'coffee',
            r'\bNingle\b': 'Jingle',
            r'\bRer\b': 'Her',
            r'\bRere\b': 'Here',
            r'\bLoor\b': 'floor',
            r'\bWHm\b': "I'm",
            r'\bsIueaky\b': 'squeaky',
            r'\bmi\'ing\b': 'mixing',
            r"\bmi'ing\b": 'mixing',
            r"\bAngel BabyHs\b": "Angel Baby's",
            r'\be\'citing\b': 'exciting',
            r'\bNat up\b': 'Eat up',
            r'\b\?ook\b': 'Look',
        }
        
        for pattern, replacement in ocr_fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Clean standard replacements
        for old, new in replacements.items():
            if old and old in text:  # Only for simple character replacements
                # Be careful with single character replacements
                if len(old) > 1:
                    text = text.replace(old, new)
        
        # Remove multiple consecutive spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove lines that are mostly garbage (high ratio of special chars)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if len(line) == 0:
                cleaned_lines.append(line)
                continue
            # Count alphanumeric characters
            alpha_count = sum(1 for c in line if c.isalnum() or c.isspace())
            ratio = alpha_count / len(line) if len(line) > 0 else 0
            if ratio > 0.7:  # Keep lines that are mostly readable
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        print(f"✨ PDF text cleaned: {len(text)} characters")
        return text
    
    @staticmethod
    def get_word_count(text: str) -> int:
        """Get word count of text"""
        return len(text.split())
    
    @staticmethod
    def get_chapter_count(text: str) -> int:
        """Estimate chapter count (looks for chapter headings)"""
        import re
        chapter_pattern = r'(?i)(chapter\s+\d+|#\s+chapter\s+\d+)'
        return len(re.findall(chapter_pattern, text))

