from difflib import Differ, unified_diff
from typing import List, Dict, Any, Tuple
import json

class DocumentComparator:
    """Enhanced document comparison with structured analysis."""
    
    def __init__(self):
        self.differ = Differ()
    
    def compare_texts(self, text1: str, text2: str) -> str:
        """Basic text comparison showing differences."""
        diff = list(self.differ.compare(text1.split(), text2.split()))
        changes = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]
        return '\n'.join(changes)
    
    def unified_diff(self, text1: str, text2: str, name1: str = "Document 1", name2: str = "Document 2") -> str:
        """Generate unified diff format comparison."""
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        diff = unified_diff(lines1, lines2, fromfile=name1, tofile=name2, lineterm='')
        return ''.join(diff)
    
    def create_structured_comparison(self, extractions: List[Dict[str, Any]]) -> str:
        """Create a structured comparison from extracted data."""
        if len(extractions) < 2:
            return "Need at least 2 documents for comparison."
        
        result = f"## Document Comparison\n\n"
        result += f"Comparing {len(extractions)} documents:\n\n"
        
        for i, extraction in enumerate(extractions, 1):
            result += f"### Document {i}: {extraction.get('document_name', 'Unknown')}\n"
            extractions_list = extraction.get('extractions', [])
            for ext in extractions_list[:5]:  # Limit display
                question = ext.get('question', 'N/A')
                answer = ext.get('answer', 'N/A')
                result += f"- **{question}**: {answer}\n"
            result += "\n"
        
        return result
    
    def find_key_differences(self, extractions: List[Dict[str, Any]]) -> List[str]:
        """Identify key differences between documents."""
        if len(extractions) < 2:
            return []
        
        differences = []
        # Group extractions by question
        questions = {}
        
        for extraction in extractions:
            doc_name = extraction.get('document_name', 'Unknown')
            for ext in extraction.get('extractions', []):
                question = ext.get('question', '')
                answer = ext.get('answer', '')
                
                if question not in questions:
                    questions[question] = {}
                questions[question][doc_name] = answer
        
        # Find differences
        for question, answers in questions.items():
            if len(set(answers.values())) > 1:  # Different answers
                diff_desc = f"**{question}**: "
                for doc, answer in answers.items():
                    diff_desc += f"{doc}: {answer[:100]}{'...' if len(answer) > 100 else ''}; "
                differences.append(diff_desc.rstrip('; '))
        
        return differences

def parse_document_sections(doc_text: str) -> List[Tuple[str, str]]:
    """Parse document text into sections by filename."""
    pdf_contents = []
    if not doc_text:
        return pdf_contents
    
    sections = doc_text.split('\n\n--- ')
    for section in sections:
        if section.startswith('--- '):
            section = section[4:]  # Remove leading '--- '
        
        if ' ---\n' in section:
            filename, content = section.split(' ---\n', 1)
            pdf_contents.append((filename, content.strip()))
    
    return pdf_contents