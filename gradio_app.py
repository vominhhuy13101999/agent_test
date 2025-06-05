import asyncio
import warnings
from enum import Enum
from pathlib import Path
from typing import List, Tuple, Optional

import gradio as gr

# Suppress numpy warnings from docling
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="docling")

# --- try both import styles so it works regardless of docling version ---
from docling.document_converter import DocumentConverter

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from multi_tool_agent.agent import create_agent

# ============================================================
# 1. GLOBAL BOOTSTRAP ----------------------------------------
# ============================================================
class Role(str, Enum):
    USER = "user"

AGENT: Optional = None
RUNNER: Optional[Runner] = None

async def _bootstrap() -> None:
    """Create agent & runner once and cache them."""
    global AGENT, RUNNER
    if AGENT is not None:
        return

    AGENT, _ = await create_agent()
    session_service = InMemorySessionService()
    RUNNER = Runner(
        app_name="Math APP",
        agent=AGENT,
        session_service=session_service,
    )
    session_service.create_session(
        app_name="Math APP", user_id="anhld", session_id="anhld-session-01"
    )

async def _ensure_bootstrap():
    if AGENT is None:
        await _bootstrap()

# ============================================================
# 2. AGENT CALL ----------------------------------------------
# ============================================================
async def _mcp_reply(prompt: str) -> str:
    await _ensure_bootstrap()
    events = [
        e async for e in RUNNER.run_async(
            user_id="anhld",
            session_id="anhld-session-01",
            new_message=types.Content(role=Role.USER, parts=[types.Part(text=prompt)]),
        )
    ]
    return events[-1].content.parts[0].text if events else "(no response)"

# ============================================================
# 3. FILE TEXT EXTRACTION (via DOCLING) ----------------------
# ============================================================

def _extract_text(file_path: str) -> str:
    """Use **docling** to pull plaintext from a variety of formats."""
    if not file_path:
        return ""

    try:
        # Suppress warnings during conversion
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
    prompt = (user_prompt.strip() + "\n\n" + doc_text.strip()) if doc_text else user_prompt.strip()
    if not prompt:
        return history, gr.update(), doc_text, gr.update(visible=False)
    reply = await _mcp_reply(prompt)
    # Clear textbox, doc state, and hide file icon after sending
    return history + [{"role": "user", "content": prompt}, {"role": "assistant", "content": reply}], "", "", gr.update(visible=False)


def _handle_upload(file_list):
    """Store extracted text from multiple files into state and update file icon."""
    print(f"Debug: Received file_list: {file_list}")
    print(f"Debug: Type of file_list: {type(file_list)}")
    
    if not file_list:
        print("Debug: No files received")
        return "", gr.update(visible=False)
    
    # Handle both single file and multiple files cases
    files = file_list if isinstance(file_list, list) else [file_list]
    print(f"Debug: Processing {len(files)} files")
    
    all_text = []
    successful_files = 0
    
    for i, file_obj in enumerate(files):
        print(f"Debug: Processing file {i}: {file_obj}")
        
        if file_obj is None:
            continue
            
        try:
            # Get file path - handle different possible structures
            if hasattr(file_obj, 'name'):
                file_path = file_obj.name
            elif isinstance(file_obj, str):
                file_path = file_obj
            else:
                file_path = str(file_obj)
                
            print(f"Debug: File path: {file_path}")
            
            # Check if file exists
            if not Path(file_path).exists():
                print(f"Debug: File does not exist: {file_path}")
                continue
                
            print(f"Debug: File exists, starting text extraction...")
            extracted_text = _extract_text(file_path)
            print(f"Debug: Text extraction completed. Length: {len(extracted_text) if extracted_text else 0}")
            
            if extracted_text and not extracted_text.startswith("(error"):
                # Add filename header for each file
                filename = Path(file_path).name
                all_text.append(f"--- {filename} ---\n{extracted_text}")
                successful_files += 1
                print(f"Debug: Successfully processed file: {filename}")
            else:
                print(f"Debug: Error or empty text: {extracted_text[:100] if extracted_text else 'None'}")
                # Still count as a file even if extraction failed
                filename = Path(file_path).name
                all_text.append(f"--- {filename} ---\n(Could not extract text from this file)")
                successful_files += 1
                
        except Exception as e:
            print(f"Debug: Exception processing file {i}: {e}")
            continue
    
    combined_text = "\n\n".join(all_text) if all_text else ""
    file_count = successful_files
    
    print(f"Debug: Combined text length: {len(combined_text)}")
    print(f"Debug: Successful file count: {file_count}")
    
    # Update file icon with count
    if file_count == 0:
        return "", gr.update(visible=False)
    elif file_count == 1:
        icon_html = "<div class='file-indicator'>📄</div>"
    else:
        icon_html = f"<div class='file-indicator' title='{file_count} files'>📁<span style='font-size:10px;position:absolute;top:-2px;right:-2px;background:#FF5C8D;border-radius:50%;padding:1px 3px;min-width:12px;text-align:center;'>{file_count}</span></div>"
    
    print(f"Debug: Returning icon_html: {icon_html}")
    return combined_text, gr.update(value=icon_html, visible=True)

with gr.Blocks(css=CSS) as demo:
    gr.Markdown("## What's on your mind today?", elem_id="page")

    doc_state = gr.State("")

    with gr.Column(elem_classes="input-box", elem_id="page"):
        txt = gr.Textbox(placeholder="Ask anything", show_label=False, lines=1)
        with gr.Row(elem_classes="icon-row"):
            upload = gr.UploadButton("+", file_types=["file"], file_count="multiple", elem_classes="icon-btn")
            file_icon = gr.HTML("<div class='file-indicator'>📄</div>", visible=False)
            send = gr.Button("➤", elem_classes="icon-btn")

    chat = gr.Chatbot(type="messages")

    send.click(_send, [chat, txt, doc_state], [chat, txt, doc_state, file_icon])
    txt.submit(_send, [chat, txt, doc_state], [chat, txt, doc_state, file_icon])

    # Fix: Use .upload() event for UploadButton
    upload.upload(_handle_upload, upload, [doc_state, file_icon])


if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv("multi_tool_agent/.env")
    demo.launch(share=True)

