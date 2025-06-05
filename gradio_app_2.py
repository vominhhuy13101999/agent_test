import asyncio
import warnings
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

import gradio as gr

# Suppress numpy warnings from docling
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="docling")

from docling.document_converter import DocumentConverter

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent, BaseAgent

# ============================================================
# 1. AGENT DEFINITIONS ---------------------------------------
# ============================================================

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

# Global variables
COORDINATOR_AGENT: Optional[LlmAgent] = None
GENERAL_AGENT: Optional[LlmAgent] = None
QUESTION_GENERATOR_AGENT: Optional[LlmAgent] = None
INFORMATION_EXTRACTOR_AGENT: Optional[LlmAgent] = None
COMPARISON_AGENT: Optional[LlmAgent] = None
RUNNER: Optional[Runner] = None

async def create_coordinator_agent() -> LlmAgent:
    """Create the coordinator agent that routes requests."""
    
    # Create specialized agents first
    general_agent = LlmAgent(
        name="general_assistant",
        model="gemini-2.5-flash-preview-05-20",
        description="Helpful AI assistant for general questions and tasks"
    )
    
    pdf_comparison_agent = LlmAgent(
        name="pdf_comparison_specialist", 
        model="gemini-2.5-flash-preview-05-20",
        description="Specialist for comparing PDF documents"
    )
    
    return LlmAgent(
        name="coordinator",
        model="gemini-2.5-flash-preview-05-20",
        description="""You are a coordinator agent that determines if a user request is for PDF comparison or general questions.

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

If unsure, default to "general".""",
        sub_agents=[general_agent, pdf_comparison_agent]
    )

async def create_general_agent() -> LlmAgent:
    """Create the general knowledge agent."""
    return LlmAgent(
        name="general_assistant",
        model="gemini-2.5-flash-preview-05-20",
        description="You are a helpful AI assistant that can answer general questions and help with various tasks. Provide clear, accurate, and helpful responses to user queries."
    )

async def create_question_generator_agent() -> LlmAgent:
    """Create the agent that generates important questions for PDF analysis."""
    return LlmAgent(
        name="question_generator",
        model="gemini-2.5-flash-preview-05-20",
        description="""You are an expert document analyst who generates comprehensive, relevant questions for any type of document comparison.

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
    )

async def create_information_extractor_agent() -> LlmAgent:
    """Create the agent that extracts information based on questions."""
    return LlmAgent(
        name="information_extractor",
        model="gemini-2.5-flash-preview-05-20",
        description="""You are an expert at extracting specific information from documents based on provided questions.

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
    )

async def create_comparison_agent() -> LlmAgent:
    """Create the agent that performs final comparison."""
    return LlmAgent(
        name="comparison_analyst",
        model="gemini-2.5-flash-preview-05-20",
        description="""You are an expert analyst who compares extracted information from multiple documents.

You will receive extracted information from multiple documents and need to provide a comprehensive comparison.

Create a clear, structured comparison that includes:
1. Side-by-side comparison of key points
2. Similarities between documents
3. Key differences highlighted
4. Recommendations or insights where appropriate

Format your response as a well-structured analysis with clear headings and bullet points.
Highlight the most important differences that would impact decision-making."""
    )

async def _bootstrap_agents() -> None:
    """Create all agents and runner once and cache them."""
    global COORDINATOR_AGENT, GENERAL_AGENT, QUESTION_GENERATOR_AGENT
    global INFORMATION_EXTRACTOR_AGENT, COMPARISON_AGENT, RUNNER
    
    if COORDINATOR_AGENT is not None:
        return

    # Create all agents
    COORDINATOR_AGENT = await create_coordinator_agent()
    GENERAL_AGENT = await create_general_agent()
    QUESTION_GENERATOR_AGENT = await create_question_generator_agent()
    INFORMATION_EXTRACTOR_AGENT = await create_information_extractor_agent()
    COMPARISON_AGENT = await create_comparison_agent()
    
    # Create runner with coordinator as default
    session_service = InMemorySessionService()
    RUNNER = Runner(
        app_name="Multi-Agent PDF Analyzer",
        agent=COORDINATOR_AGENT,
        session_service=session_service,
    )
    session_service.create_session(
        app_name="Multi-Agent PDF Analyzer", 
        user_id="user", 
        session_id="main-session"
    )

async def _ensure_bootstrap():
    if COORDINATOR_AGENT is None:
        await _bootstrap_agents()

# ============================================================
# 2. MULTI-AGENT ORCHESTRATION ------------------------------
# ============================================================

async def _run_agent(agent: LlmAgent, prompt: str) -> str:
    """Run a specific agent with a prompt."""
    await _ensure_bootstrap()
    
    # Temporarily switch the runner's agent
    original_agent = RUNNER.agent
    RUNNER.agent = agent
    
    try:
        print(f"Debug: Running agent {agent.name}")
        events = [
            e async for e in RUNNER.run_async(
                user_id="user",
                session_id="main-session",
                new_message=types.Content(
                    role=Role.USER, 
                    parts=[types.Part(text=prompt)]
                ),
            )
        ]
        response = events[-1].content.parts[0].text if events else "(no response)"
        print(f"Debug: Agent {agent.name} response length: {len(response)}")
        return response
    except Exception as e:
        print(f"Debug: Error running agent {agent.name}: {e}")
        # If rate limited, wait and try with a simpler model or return error
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return "Rate limit exceeded. Please try again in a moment."
        return f"Error: {e}"
    finally:
        # Restore original agent
        RUNNER.agent = original_agent

async def _parse_json_response(response: str) -> Dict:
    """Safely parse JSON response from agent."""
    try:
        print(f"Debug: Parsing JSON from response: {response[:200]}...")
        
        # Try to find JSON in the response - look for ```json blocks first
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end != -1:
                json_str = response[start:end].strip()
                print(f"Debug: Found JSON block: {json_str[:100]}...")
                return json.loads(json_str)
        
        # Try to find plain JSON
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = response[start:end]
            print(f"Debug: Found JSON: {json_str[:100]}...")
            return json.loads(json_str)
            
    except Exception as e:
        print(f"Debug: JSON parsing error: {e}")
        print(response)
    
    print("Debug: No valid JSON found")
    return {}

async def _process_pdf_comparison(prompt: str, pdf_contents: List[Tuple[str, str]]) -> str:
    """Process PDF comparison using sequential agents."""
    if len(pdf_contents) < 2:
        return "I need at least 2 PDF files to perform a comparison."
    
    print("Debug: Starting PDF comparison process...")
    
    # Step 1: Generate questions based on user prompt
    question_prompt = f"""Based on this user request: "{prompt}" """
    
    questions_response = await _run_agent(QUESTION_GENERATOR_AGENT, question_prompt)
    print(f"Debug: Questions response: {questions_response[:200]}...")
    
    questions_data = await _parse_json_response(questions_response)
    questions = questions_data.get('questions', [])
    doc_type = questions_data.get('document_type_detected', 'Unknown document type')
    
    print(f"Debug: Detected document type: {doc_type}")
    
    if not questions:

        print("______________________________________________________________________")
        # Fallback questions that adapt based on common document patterns
        if any(word in prompt.lower() or any(word in content.lower() for _, content in pdf_contents) 
               for word in ['lease', 'rent', 'tenant', 'landlord']):
            questions = [
                "What is the rental amount or monthly rent?",
                "What are the lease terms and duration?",
                "What are the pet policies and associated fees?",
                "What security deposit is required?",
                "What are the tenant responsibilities?",
                "What are the landlord responsibilities?",
                "What are the termination conditions?",
                "What penalties or fees are mentioned?"
            ]
        elif any(word in prompt.lower() or any(word in content.lower() for _, content in pdf_contents)
                 for word in ['contract', 'agreement', 'terms', 'conditions']):
            questions = [
                "What are the main terms and conditions?",
                "Who are the parties involved?",
                "What are the obligations of each party?",
                "What are the payment terms?",
                "What are the termination clauses?",
                "What penalties or consequences are specified?",
                "What are the key dates and deadlines?",
                "What dispute resolution mechanisms exist?"
            ]
        elif any(word in prompt.lower() or any(word in content.lower() for _, content in pdf_contents)
                 for word in ['policy', 'procedure', 'guidelines', 'rules']):
            questions = [
                "What is the main purpose or scope?",
                "What are the key policies or rules?",
                "Who does this apply to?",
                "What are the requirements or qualifications?",
                "What are the procedures to follow?",
                "What are the exceptions or special cases?",
                "What are the consequences of non-compliance?",
                "How often is this reviewed or updated?"
            ]
        else:
            # Generic fallback
            questions = [
                "What is the main subject or purpose?",
                "What are the key terms and conditions?",
                "What costs, fees, or financial aspects are mentioned?",
                "What requirements or qualifications exist?",
                "What are the important dates and deadlines?",
                "What parties or entities are involved?",
                "What processes or procedures are described?",
                "What risks, penalties, or consequences are mentioned?"
            ]
    
    print(f"Debug: Using {len(questions)} questions for extraction")
    
    # Step 2: Extract information from each PDF
    all_extractions = []
    for filename, content in pdf_contents:
        print(f"Debug: Extracting from {filename}")
        
        # Truncate content if too long to avoid rate limits
        max_content_length = 80000  # Reduced to avoid rate limits
        truncated_content = content[:max_content_length]
        if len(content) > max_content_length:
            truncated_content += "\n\n[Content truncated due to length...]"
        
        extraction_prompt = f"""Questions to answer:
{json.dumps(questions[:20], indent=2)}

Document content to analyze:
{truncated_content}"""
        
        extraction_response = await _run_agent(INFORMATION_EXTRACTOR_AGENT, extraction_prompt)
        print(f"Debug: Extraction response for {filename}: {extraction_response[:200]}...")
        
        if "Rate limit exceeded" in extraction_response:
            return "Rate limit exceeded. Please try again in a moment."
        
        extraction_data = await _parse_json_response(extraction_response)
        if extraction_data and extraction_data.get('extractions'):
            extraction_data['document_name'] = filename
            all_extractions.append(extraction_data)
            print(f"Debug: Successfully extracted data for {filename}")
        else:
            # Fallback: create basic extraction
            fallback_extraction = {
                'document_name': filename,
                'extractions': [{'question': 'Document summary', 'answer': truncated_content[:500] + '...', 'source_text': 'Full document'}]
            }
            all_extractions.append(fallback_extraction)
            print(f"Debug: Used fallback extraction for {filename}")
    
    print(f"Debug: Completed extraction for {len(all_extractions)} documents")
    
    if not all_extractions:
        return "Could not extract information from the documents due to rate limits. Please try again later."
    
    # Step 3: Compare the extracted information (simplified to avoid rate limits)
    # Create a simple comparison without using another agent call
    comparison_result = f"""## Document Comparison

Based on your request: "{prompt}"

I've analyzed {len(all_extractions)} documents:

"""
    
    for i, extraction in enumerate(all_extractions, 1):
        comparison_result += f"### Document {i}: {extraction['document_name']}\n"
        extractions = extraction.get('extractions', [])
        for ext in extractions[:5]:  # Limit to first 5 extractions
            comparison_result += f"- **{ext.get('question', 'N/A')}**: {ext.get('answer', 'N/A')}\n"
        comparison_result += "\n"
    
    comparison_result += """### """
    
    return comparison_result

async def _mcp_reply(prompt: str, pdf_contents: List[Tuple[str, str]] = None) -> str:
    """Main orchestration function."""
    await _ensure_bootstrap()
    
    # Step 1: Coordinate - determine task type
    coordinator_prompt = f"""Analyze this user request: "{prompt}"
    
Additional context: User has uploaded {len(pdf_contents) if pdf_contents else 0} PDF files."""
    
    coordination_response = await _run_agent(COORDINATOR_AGENT, coordinator_prompt)
    print(f"Debug: Coordination response: {coordination_response}")
    
    coordination_data = await _parse_json_response(coordination_response)
    task_type = coordination_data.get('task_type', 'general')
    
    print(f"Debug: Task type determined: {task_type}")
    
    # Step 2: Route to appropriate processing
    if task_type == 'pdf_comparison' and pdf_contents and len(pdf_contents) >= 2:
        return await _process_pdf_comparison(prompt, pdf_contents)
    else:
        # Step 3: Handle as general query
        full_prompt = prompt
        if pdf_contents:
            # Include PDF content for general questions
            pdf_text = "\n\n".join([f"--- {name} ---\n{content}" for name, content in pdf_contents])
            full_prompt = f"{prompt}\n\nDocument content:\n{pdf_text}"
        
        return await _run_agent(GENERAL_AGENT, full_prompt)

# ============================================================
# 3. FILE TEXT EXTRACTION (via DOCLING) --------------------
# ============================================================

def _extract_text(file_path: str) -> str:
    """Use **docling** to pull plaintext from a variety of formats."""
    if not file_path:
        return ""

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            print(f"Debug: Starting docling conversion for {file_path}")
            converter = DocumentConverter()
            result = converter.convert(file_path)
            text = result.document.export_to_markdown().strip()
            print(f"Debug: Docling conversion completed, text length: {len(text)}")
            return text
    except Exception as exc:
        print(f"Debug: Exception in _extract_text: {exc}")
        return f"(error extracting text: {exc})"

# ============================================================
# 4. GRADIO UI -----------------------------------------------
# ============================================================

CSS = r"""
#page{max-width:960px;margin:0 auto;}
h1{font-size:2rem;font-weight:600;margin-top:3rem;text-align:center;}
.input-box{display:flex;flex-direction:column;gap:.75rem;border:2px solid #E5E7EB;border-radius:2.5rem;padding:1.25rem 1.5rem;}
.input-box:hover{box-shadow:0 0 0 2px #D1D5DB;}
.gr-textbox{border:none !important;background:transparent;}
.icon-row{display:flex;justify-content:space-between;align-items:center;}
.icon-btn{width:38px;height:38px;min-width:38px !important;min-height:38px !important;flex:0 0 auto !important;padding:0;border-radius:50%;border:none;background:#000;color:#fff;font-size:1rem;display:flex;align-items:center;justify-content:center;cursor:pointer;}
.file-indicator{width:38px;height:38px;border-radius:12px;background:#FF5C8D;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;position:relative;}
"""

async def _send(history: List[dict], user_prompt: str, doc_text: str):
    prompt = user_prompt.strip()
    if not prompt:
        return history, gr.update(), doc_text, gr.update(visible=False)
    
    # Parse PDF contents if any
    pdf_contents = []
    if doc_text:
        # Split by document separators
        sections = doc_text.split('\n\n--- ')
        for section in sections:
            if section.startswith('--- '):
                section = section[4:]  # Remove leading '--- '
            
            if ' ---\n' in section:
                filename, content = section.split(' ---\n', 1)
                pdf_contents.append((filename, content.strip()))
    
    print(f"Debug: Processing {len(pdf_contents)} PDF files")
    
    reply = await _mcp_reply(prompt, pdf_contents)
    
    # Clear everything after sending
    return (
        history + [{"role": "user", "content": prompt}, {"role": "assistant", "content": reply}], 
        "", 
        "", 
        gr.update(visible=False)
    )

def _handle_upload(file_list):
    """Store extracted text from multiple files into state and update file icon."""
    print(f"Debug: Received file_list: {file_list}")
    
    if not file_list:
        return "", gr.update(visible=False)
    
    files = file_list if isinstance(file_list, list) else [file_list]
    print(f"Debug: Processing {len(files)} files")
    
    all_text = []
    successful_files = 0
    
    for i, file_obj in enumerate(files):
        if file_obj is None:
            continue
            
        try:
            file_path = file_obj if isinstance(file_obj, str) else str(file_obj)
            print(f"Debug: File path: {file_path}")
            
            if not Path(file_path).exists():
                print(f"Debug: File does not exist: {file_path}")
                continue
                
            extracted_text = _extract_text(file_path)
            
            if extracted_text and not extracted_text.startswith("(error"):
                filename = Path(file_path).name
                all_text.append(f"--- {filename} ---\n{extracted_text}")
                successful_files += 1
                print(f"Debug: Successfully processed file: {filename}")
            else:
                filename = Path(file_path).name
                all_text.append(f"--- {filename} ---\n(Could not extract text from this file)")
                successful_files += 1
                
        except Exception as e:
            print(f"Debug: Exception processing file {i}: {e}")
            continue
    
    combined_text = "\n\n".join(all_text) if all_text else ""
    
    # Update file icon with count
    if successful_files == 0:
        return "", gr.update(visible=False)
    elif successful_files == 1:
        icon_html = "<div class='file-indicator'>📄</div>"
    else:
        icon_html = f"<div class='file-indicator' title='{successful_files} files'>📁<span style='font-size:10px;position:absolute;top:-2px;right:-2px;background:#FF5C8D;border-radius:50%;padding:1px 3px;min-width:12px;text-align:center;'>{successful_files}</span></div>"
    
    return combined_text, gr.update(value=icon_html, visible=True)

with gr.Blocks(css=CSS) as demo:
    gr.Markdown("## Multi-Agent PDF Analyzer", elem_id="page")
    gr.Markdown("Upload PDFs to compare them, or ask general questions. The system will automatically determine the best approach.")

    doc_state = gr.State("")

    with gr.Column(elem_classes="input-box", elem_id="page"):
        txt = gr.Textbox(placeholder="Ask anything or request PDF comparison", show_label=False, lines=1)
        with gr.Row(elem_classes="icon-row"):
            upload = gr.UploadButton("+", file_types=["file"], file_count="multiple", elem_classes="icon-btn")
            file_icon = gr.HTML("<div class='file-indicator'>📄</div>", visible=False)
            send = gr.Button("➤", elem_classes="icon-btn")

    chat = gr.Chatbot(type="messages")

    send.click(_send, [chat, txt, doc_state], [chat, txt, doc_state, file_icon])
    txt.submit(_send, [chat, txt, doc_state], [chat, txt, doc_state, file_icon])
    upload.upload(_handle_upload, upload, [doc_state, file_icon])


if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv("multi_tool_agent/.env")
    demo.launch(share=True)