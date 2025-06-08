import warnings
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    print("Warning: docling not available. Install with: pip install docling")
    DocumentConverter = None

class DocumentExtractor:
    """Enhanced document text extraction using docling."""
    
    def __init__(self):
        if DocumentConverter is None:
            raise ImportError("docling is required but not installed. Install with: pip install docling")
        self.converter = DocumentConverter()
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from various document formats using docling."""
        if not file_path or not Path(file_path).exists():
            return ""
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = self.converter.convert(file_path)
                return result.document.export_to_markdown().strip()
        except Exception as exc:
            return f"(error extracting text: {exc})"
    
    def extract_from_multiple(self, file_paths: List[str]) -> List[Tuple[str, str]]:
        """Extract text from multiple files."""
        results = []
        for file_path in file_paths:
            filename = Path(file_path).name
            text = self.extract_text(file_path)
            results.append((filename, text))
        return results
    
    def save_text(self, text: str, output_file: str = "output.txt") -> bool:
        """Save extracted text to file."""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            return True
        except Exception:
            return False

def process_file_upload(file_list) -> Tuple[str, bool]:
    """Process uploaded files and extract text."""
    if not file_list:
        return "", False
    
    extractor = DocumentExtractor()
    files = file_list if isinstance(file_list, list) else [file_list]
    
    all_text = []
    successful_files = 0
    
    for file_obj in files:
        if file_obj is None:
            continue
        
        try:
            file_path = getattr(file_obj, 'name', str(file_obj))
            if not Path(file_path).exists():
                continue
            
            extracted_text = extractor.extract_text(file_path)
            filename = Path(file_path).name
            
            if extracted_text and not extracted_text.startswith("(error"):
                all_text.append(f"--- {filename} ---\n{extracted_text}")
            else:
                all_text.append(f"--- {filename} ---\n(Could not extract text from this file)")
            
            successful_files += 1
            
        except Exception:
            continue
    
    combined_text = "\n\n".join(all_text) if all_text else ""
    return combined_text, successful_files > 0
