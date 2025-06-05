import json
from typing import List, Dict, Any, Tuple
from agent_manager import AgentManager
from document_comparator import DocumentComparator
from config import AppConfig, DocumentType

class PDFProcessor:
    """Handles PDF comparison workflow using multiple agents."""
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.comparator = DocumentComparator()
    
    async def process_comparison(self, prompt: str, pdf_contents: List[Tuple[str, str]]) -> str:
        """Process PDF comparison using sequential agents."""
        if len(pdf_contents) < 2:
            return "I need at least 2 PDF files to perform a comparison."
        
        await self.agent_manager.initialize()
        
        # Step 1: Generate questions
        questions = await self._generate_questions(prompt, pdf_contents)
        
        # Step 2: Extract information from each PDF
        all_extractions = await self._extract_information(questions, pdf_contents)
        
        if not all_extractions:
            return "Could not extract information from the documents due to rate limits. Please try again later."
        
        # Step 3: Create comparison
        return self._create_comparison_result(prompt, all_extractions)
    
    async def _generate_questions(self, prompt: str, pdf_contents: List[Tuple[str, str]]) -> List[str]:
        """Generate relevant questions for document analysis."""
        question_prompt = f'Based on this user request: "{prompt}"'
        
        questions_response = await self.agent_manager.run_agent(
            self.agent_manager.question_generator_agent, 
            question_prompt
        )
        
        questions_data = await self.agent_manager.parse_json_response(questions_response)
        questions = questions_data.get('questions', [])
        
        # Fallback to predefined questions if generation fails
        if not questions:
            questions = self.agent_manager.get_fallback_questions(prompt, pdf_contents)
        
        return questions[:AppConfig.MAX_QUESTIONS]  # Limit questions
    
    async def _extract_information(self, questions: List[str], pdf_contents: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Extract information from each PDF based on questions."""
        all_extractions = []
        
        for filename, content in pdf_contents:
            # Truncate content to avoid rate limits
            truncated_content = content[:AppConfig.MAX_CONTENT_LENGTH]
            if len(content) > AppConfig.MAX_CONTENT_LENGTH:
                truncated_content += "\\n\\n[Content truncated due to length...]"
            
            extraction_prompt = f"""Questions to answer:
{json.dumps(questions, indent=2)}

Document content to analyze:
{truncated_content}"""
            
            extraction_response = await self.agent_manager.run_agent(
                self.agent_manager.information_extractor_agent,
                extraction_prompt
            )
            
            if "Rate limit exceeded" in extraction_response:
                return []  # Return empty to trigger fallback
            
            extraction_data = await self.agent_manager.parse_json_response(extraction_response)
            
            if extraction_data and extraction_data.get('extractions'):
                extraction_data['document_name'] = filename
                all_extractions.append(extraction_data)
            else:
                # Fallback extraction
                fallback_extraction = {
                    'document_name': filename,
                    'extractions': [{
                        'question': 'Document summary',
                        'answer': truncated_content[:500] + '...',
                        'source_text': 'Full document'
                    }]
                }
                all_extractions.append(fallback_extraction)
        
        return all_extractions
    
    def _create_comparison_result(self, prompt: str, extractions: List[Dict[str, Any]]) -> str:
        """Create the final comparison result."""
        result = f"""## Document Comparison

Based on your request: "{prompt}"

I've analyzed {len(extractions)} documents:

"""
        
        # Add document summaries
        for i, extraction in enumerate(extractions, 1):
            result += f"### Document {i}: {extraction['document_name']}\\n"
            extractions_list = extraction.get('extractions', [])
            for ext in extractions_list[:AppConfig.MAX_EXTRACTIONS]:
                question = ext.get('question', 'N/A')
                answer = ext.get('answer', 'N/A')
                result += f"- **{question}**: {answer}\\n"
            result += "\\n"
        
        # Add key differences
        differences = self.comparator.find_key_differences(extractions)
        if differences:
            result += "### Key Differences\\n\\n"
            for diff in differences[:10]:  # Limit differences shown
                result += f"- {diff}\\n"
        
        return result

class DocumentRouter:
    """Routes requests to appropriate processing pipeline."""
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.pdf_processor = PDFProcessor()
    
    async def route_request(self, prompt: str, pdf_contents: List[Tuple[str, str]] = None) -> str:
        """Route request to appropriate handler."""
        await self.agent_manager.initialize()
        
        # Determine task type
        task_type = await self._determine_task_type(prompt, pdf_contents)
        
        if task_type == 'pdf_comparison' and pdf_contents and len(pdf_contents) >= 2:
            return await self.pdf_processor.process_comparison(prompt, pdf_contents)
        else:
            return await self._handle_general_query(prompt, pdf_contents)
    
    async def _determine_task_type(self, prompt: str, pdf_contents: List[Tuple[str, str]]) -> str:
        """Determine if this is a PDF comparison or general query."""
        coordinator_prompt = f"""Analyze this user request: "{prompt}"
        
Additional context: User has uploaded {len(pdf_contents) if pdf_contents else 0} PDF files."""
        
        coordination_response = await self.agent_manager.run_agent(
            self.agent_manager.coordinator_agent,
            coordinator_prompt
        )
        
        coordination_data = await self.agent_manager.parse_json_response(coordination_response)
        return coordination_data.get('task_type', 'general')
    
    async def _handle_general_query(self, prompt: str, pdf_contents: List[Tuple[str, str]]) -> str:
        """Handle general queries."""
        full_prompt = prompt
        if pdf_contents:
            pdf_text = "\\n\\n".join([f"--- {name} ---\\n{content}" for name, content in pdf_contents])
            full_prompt = f"{prompt}\\n\\nDocument content:\\n{pdf_text}"
        
        return await self.agent_manager.run_agent(
            self.agent_manager.general_agent,
            full_prompt
        )