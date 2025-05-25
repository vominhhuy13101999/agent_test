import asyncio, io
from enum import Enum
from pathlib import Path
from typing import List, Tuple, Optional

import gradio as gr
import pdfplumber
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
    # idempotent create
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
# 3. FILE TEXT EXTRACTION ------------------------------------
# ============================================================

def _extract_text(file_path: str) -> str:
    """Return plain text from .txt or .pdf path provided by Gradio."""
    if not file_path:
        return ""

    p = Path(str(file_path))
    data = p.read_bytes()
    ext  = p.suffix.lower()

    if ext == ".txt":
        return data.decode("utf-8", errors="ignore").strip()

    if ext == ".pdf":
        text = ""
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text.strip()

    return f"(unsupported file type: {ext})"

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
.file-indicator{width:38px;height:38px;border-radius:12px;background:#FF5C8D;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;}
"""

async def _send(history: List[Tuple[str, str]], user_prompt: str, doc_text: str):
    prompt = (user_prompt.strip() + "\n\n" + doc_text.strip()) if doc_text else user_prompt.strip()
    if not prompt:
        return history, gr.update(), doc_text

    reply = await _mcp_reply(prompt)
    return history + [[prompt, reply]], "", ""  # clear textbox + doc state


def _handle_upload(file_path: str):
    """Store extracted text into state and reveal file icon."""
    return _extract_text(file_path), gr.update(visible=True)

with gr.Blocks(css=CSS) as demo:
    gr.Markdown("## What's on your mind today?", elem_id="page")

    doc_state = gr.State("")  # holds extracted text until send

    with gr.Column(elem_classes="input-box", elem_id="page"):
        txt = gr.Textbox(placeholder="Ask anything", show_label=False, lines=1)
        with gr.Row(elem_classes="icon-row"):
            upload = gr.UploadButton("+", file_types=["file"], file_count="single", elem_classes="icon-btn")
            file_icon = gr.HTML("<div class='file-indicator'>📄</div>", visible=False)
            send = gr.Button("➤", elem_classes="icon-btn")

    chat = gr.Chatbot()

    send.click(_send, [chat, txt, doc_state], [chat, txt, doc_state])
    txt.submit(_send, [chat, txt, doc_state], [chat, txt, doc_state])

    # when a file is uploaded, extract text into doc_state and show indicator
    upload.upload(_handle_upload, upload, [doc_state, file_icon])

if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv("multi_tool_agent/.env")
    demo.launch(share=True)

