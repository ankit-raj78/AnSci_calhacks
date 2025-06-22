"""
PDF Processor Service
Handles PDF upload, parsing, and section extraction
"""

import os
import logging
from typing import Dict, List, Optional, Any
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
from io import BytesIO

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.max_sections = int(os.getenv('MAX_SECTIONS_PER_DOCUMENT', '10'))
        logger.info("PDF processor initialized")

    def download_pdf(self, pdf_url: str) -> bytes:
        """Download PDF from Supabase storage URL"""
        # This would typically download from Supabase
        # For now, we'll assume the URL is accessible
        import requests
        try:
            response = requests.get(pdf_url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading PDF from {pdf_url}: {e}")
            raise

    def extract_text_pypdf2(self, pdf_content: bytes) -> str:
        """Extract text using PyPDF2"""
        try:
            pdf_file = BytesIO(pdf_content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            return ""

    def extract_text_pdfplumber(self, pdf_content: bytes) -> str:
        """Extract text using pdfplumber (better for tables and layout)"""
        try:
            pdf_file = BytesIO(pdf_content)
            text = ""
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
            return ""

    def extract_text_pymupdf(self, pdf_content: bytes) -> str:
        """Extract text using PyMuPDF (best for complex layouts)"""
        try:
            pdf_file = BytesIO(pdf_content)
            doc = fitz.open(stream=pdf_file, filetype="pdf")
            
            text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text() + "\n"
            
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text with PyMuPDF: {e}")
            return ""

    def extract_text_robust(self, pdf_content: bytes) -> str:
        """Extract text using multiple methods for best results"""
        # Try multiple extraction methods
        extractors = [
            ("PyMuPDF", self.extract_text_pymupdf),
            ("pdfplumber", self.extract_text_pdfplumber),
            ("PyPDF2", self.extract_text_pypdf2)
        ]
        
        for name, extractor in extractors:
            try:
                text = extractor(pdf_content)
                if text and len(text.strip()) > 100:  # Minimum viable text length
                    logger.info(f"Successfully extracted text using {name}")
                    return text
            except Exception as e:
                logger.warning(f"Text extraction failed with {name}: {e}")
                continue
        
        raise RuntimeError("All text extraction methods failed")

    def parse_into_sections(self, pdf_content: bytes, level: str) -> List[Dict[str, Any]]:
        """
        Parse PDF content into logical sections
        This is a simplified version - in production, you'd use Claude for this
        """
        try:
            # Extract text from PDF
            full_text = self.extract_text_robust(pdf_content)
            
            if not full_text.strip():
                raise ValueError("No text could be extracted from PDF")
            
            # Basic section detection using common academic paper patterns
            sections = self._detect_sections_simple(full_text, level)
            
            # Limit number of sections
            if len(sections) > self.max_sections:
                logger.warning(f"Too many sections ({len(sections)}), limiting to {self.max_sections}")
                sections = sections[:self.max_sections]
            
            logger.info(f"Parsed PDF into {len(sections)} sections")
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing PDF into sections: {e}")
            raise

    def _detect_sections_simple(self, text: str, level: str) -> List[Dict[str, Any]]:
        """
        Simple section detection based on common patterns
        In production, this would be handled by Claude API
        """
        lines = text.split('\n')
        sections = []
        current_section = []
        section_titles = []
        
        # Common section headers in academic papers
        section_patterns = [
            'abstract', 'introduction', 'background', 'methodology', 'methods',
            'results', 'discussion', 'conclusion', 'future work', 'references',
            'related work', 'literature review', 'experimental setup', 'evaluation',
            'analysis', 'implementation', 'design', 'architecture'
        ]
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            
            # Check if this line looks like a section header
            is_section_header = any(pattern in line_lower for pattern in section_patterns)
            is_section_header = is_section_header or (
                len(line.strip()) < 100 and 
                line.strip() and 
                (line.isupper() or line.istitle()) and
                not line.strip().endswith('.')
            )
            
            if is_section_header and len(current_section) > 10:  # Minimum section length
                # Save previous section
                if current_section:
                    section_content = '\n'.join(current_section)
                    sections.append(self._create_section_dict(
                        title=section_titles[-1] if section_titles else f"Section {len(sections) + 1}",
                        content=section_content,
                        level=level,
                        index=len(sections)
                    ))
                
                # Start new section
                current_section = [line]
                section_titles.append(line.strip())
            else:
                current_section.append(line)
        
        # Add the last section
        if current_section:
            section_content = '\n'.join(current_section)
            sections.append(self._create_section_dict(
                title=section_titles[-1] if section_titles else f"Section {len(sections) + 1}",
                content=section_content,
                level=level,
                index=len(sections)
            ))
        
        # If no sections were detected, create a single section
        if not sections:
            sections.append(self._create_section_dict(
                title="Complete Document",
                content=text[:2000],  # Limit content length
                level=level,
                index=0
            ))
        
        return sections

    def _create_section_dict(self, title: str, content: str, level: str, index: int) -> Dict[str, Any]:
        """Create a standardized section dictionary"""
        # Estimate complexity based on content
        complexity = self._estimate_complexity(content)
        
        # Adjust complexity based on level
        level_multiplier = {'beginner': 0.7, 'intermediate': 1.0, 'advanced': 1.3}
        adjusted_complexity = min(10, complexity * level_multiplier.get(level, 1.0))
        
        return {
            'title': title,
            'content': content[:1000],  # Limit content for processing
            'level': level,
            'index': index,
            'complexity': int(adjusted_complexity),
            'estimated_time': min(180, len(content.split()) * 0.5),  # Rough time estimate
            'word_count': len(content.split()),
            'dependencies': [],  # Would be filled by Claude
            'concepts': [],      # Would be filled by Claude
            'visual_elements': ['text', 'diagrams']  # Default visual elements
        }

    def _estimate_complexity(self, content: str) -> int:
        """Estimate content complexity (1-10 scale)"""
        # Simple heuristics for complexity
        word_count = len(content.split())
        
        # Check for mathematical content
        math_indicators = ['equation', 'formula', 'theorem', 'proof', '∑', '∫', '∂']
        math_score = sum(1 for indicator in math_indicators if indicator in content.lower())
        
        # Check for technical terms
        technical_indicators = ['algorithm', 'implementation', 'optimization', 'model', 'framework']
        tech_score = sum(1 for indicator in technical_indicators if indicator in content.lower())
        
        # Base complexity from word count
        base_complexity = min(8, word_count / 100)
        
        # Add complexity from math and technical content
        total_complexity = base_complexity + math_score * 0.5 + tech_score * 0.3
        
        return max(1, min(10, int(total_complexity)))

    def get_pdf_metadata(self, pdf_content: bytes) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        try:
            pdf_file = BytesIO(pdf_content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            metadata = {
                'page_count': len(reader.pages),
                'title': None,
                'author': None,
                'subject': None,
                'creator': None,
                'producer': None,
                'creation_date': None,
                'modification_date': None
            }
            
            if reader.metadata:
                metadata.update({
                    'title': reader.metadata.get('/Title'),
                    'author': reader.metadata.get('/Author'),
                    'subject': reader.metadata.get('/Subject'),
                    'creator': reader.metadata.get('/Creator'),
                    'producer': reader.metadata.get('/Producer'),
                    'creation_date': reader.metadata.get('/CreationDate'),
                    'modification_date': reader.metadata.get('/ModDate')
                })
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            return {'page_count': 0, 'error': str(e)}
