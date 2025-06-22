from enum import Enum
from typing import Dict, Any

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class AppConfig:
    APP_NAME = "Multi-Agent PDF Analyzer"
    USER_ID = "user"
    SESSION_ID = "main-session"
    MODEL_NAME = "gemini-2.5-flash-preview-05-20"
    MAX_CONTENT_LENGTH = 80000
    MAX_QUESTIONS = 20
    MAX_EXTRACTIONS = 5

class MCPConfig:
    SERVER_URL = "http://127.0.0.1:17234/sse"

class UIConfig:
    MAX_WIDTH = "960px"
    ICON_SIZE = "38px"
    BORDER_RADIUS = "2.5rem"
    PRIMARY_COLOR = "#000"
    ACCENT_COLOR = "#FF5C8D"
    
    CSS = f"""
    #page{{max-width:{MAX_WIDTH};margin:0 auto;}}
    h1{{font-size:2rem;font-weight:600;margin-top:3rem;text-align:center;}}
    .input-box{{display:flex;flex-direction:column;gap:.75rem;border:2px solid #E5E7EB;border-radius:{BORDER_RADIUS};padding:1.25rem 1.5rem;}}
    .input-box:hover{{box-shadow:0 0 0 2px #D1D5DB;}}
    .gr-textbox{{border:none !important;background:transparent;}}
    .icon-row{{display:flex;justify-content:space-between;align-items:center;}}
    .icon-btn{{width:{ICON_SIZE};height:{ICON_SIZE};min-width:{ICON_SIZE} !important;min-height:{ICON_SIZE} !important;flex:0 0 auto !important;padding:0;border-radius:50%;border:none;background:{PRIMARY_COLOR};color:#fff;font-size:1rem;display:flex;align-items:center;justify-content:center;cursor:pointer;}}
    .file-indicator{{width:{ICON_SIZE};height:{ICON_SIZE};border-radius:12px;background:{ACCENT_COLOR};display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;position:relative;}}
    """

class AgentPrompts:
    COORDINATOR = """You are a coordinator agent that determines if a user request is for PDF comparison or general questions.

Your task is to analyze the user's prompt and determine:
1. Is this a request to compare PDFs or documents?
2. Or is this a general question/request?

Look for keywords like:
- "compare", "comparison", "difference", "contrast"
- "between documents", "between PDFs", "two files"
- "which is better", "analyze differences"

Respond with JSON only:
{
    "task_type": "pdf_comparison" or "general",
    "reasoning": "brief explanation of your decision"
}

If unsure, default to "general"."""

    GENERAL = "You are a helpful AI assistant that can answer general questions and help with various tasks. Provide clear, accurate, and helpful responses to user queries."

    QUESTION_GENERATOR = """You are an expert document analyst who generates comprehensive, relevant questions for any type of document comparison.

Your task:
1. FIRST, analyze the provided document content to understand what type of documents they are
2. THEN, generate specific, relevant questions based on the actual document type and content

For different document types, focus on different aspects:
- **Contracts/Agreements**: Terms, conditions, obligations, penalties, dates, parties involved
- **Financial Documents**: Rates, fees, costs, payment terms, penalties, benefits
- **Policy Documents**: Rules, procedures, requirements, exceptions, coverage
- **Legal Documents**: Definitions, clauses, rights, responsibilities, jurisdiction
- **Technical Documents**: Specifications, requirements, procedures, standards
- **Business Documents**: Processes, responsibilities, timelines, deliverables
- **Academic/Research**: Methodology, findings, conclusions, data, references

Generate 15-50 targeted questions that would be most important for comparing these specific types of documents.

Respond with JSON:
{
    "document_type_detected": "Brief description of what type of documents these appear to be",
    "questions": [
        "Specific question relevant to this document type",
        "Another targeted question",
        ...
    ]
}

Make questions specific to the actual content and purpose of the documents, not generic."""

    INFORMATION_EXTRACTOR = """You are an expert at extracting specific information from documents based on provided questions.

You will be given:
1. A list of questions to answer
2. Document content to analyze

For each question, extract the relevant information from the document. If information is not found, clearly state "Not mentioned" or "Not found".

Respond with JSON:
{
    "document_name": "filename",
    "extractions": [
        {
            "question": "What is the monthly rent rate?",
            "answer": "extracted information or 'Not found'",
            "source_text": "relevant quote from document if found"
        },
        ...
    ]
}

Be thorough and accurate in your extractions."""

    COMPARISON = """You are an expert analyst who compares extracted information from multiple documents.

You will receive extracted information from multiple documents and need to provide a comprehensive comparison.

Create a clear, structured comparison that includes:
1. Side-by-side comparison of key points
2. Similarities between documents
3. Key differences highlighted
4. Recommendations or insights where appropriate

Format your response as a well-structured analysis with clear headings and bullet points.
Highlight the most important differences that would impact decision-making."""

class DocumentType:
    FALLBACK_QUESTIONS = {
        'lease': [
            "What is the rental amount or monthly rent?",
            "What are the lease terms and duration?",
            "What are the pet policies and associated fees?",
            "What security deposit is required?",
            "What are the tenant responsibilities?",
            "What are the landlord responsibilities?",
            "What are the termination conditions?",
            "What penalties or fees are mentioned?"
        ],
        'contract': [
            "What are the main terms and conditions?",
            "Who are the parties involved?",
            "What are the obligations of each party?",
            "What are the payment terms?",
            "What are the termination clauses?",
            "What penalties or consequences are specified?",
            "What are the key dates and deadlines?",
            "What dispute resolution mechanisms exist?"
        ],
        'policy': [
            "What is the main purpose or scope?",
            "What are the key policies or rules?",
            "Who does this apply to?",
            "What are the requirements or qualifications?",
            "What are the procedures to follow?",
            "What are the exceptions or special cases?",
            "What are the consequences of non-compliance?",
            "How often is this reviewed or updated?"
        ],
        'generic': [
            "What is the main subject or purpose?",
            "What are the key terms and conditions?",
            "What costs, fees, or financial aspects are mentioned?",
            "What requirements or qualifications exist?",
            "What are the important dates and deadlines?",
            "What parties or entities are involved?",
            "What processes or procedures are described?",
            "What risks, penalties, or consequences are mentioned?"
        ]
    }