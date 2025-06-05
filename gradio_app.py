import warnings
from typing import List, Optional

import gradio as gr

# Suppress warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="docling")

from src.agent_manager import MCPAgentManager
from src.document_extractor import process_file_upload
from src.config import UIConfig
from src.error_handler import ErrorHandler, safe_async_call, validate_input, validate_file_upload

# Global components
agent_manager: Optional[MCPAgentManager] = None
error_handler = ErrorHandler("gradio_app")

@safe_async_call(error_handler, "Failed to get response")
async def _mcp_reply(prompt: str) -> str:
    """Get response from MCP agent."""
    global agent_manager
    if agent_manager is None:
        agent_manager = MCPAgentManager()
    
    return await agent_manager.run(prompt)



async def _send(history: List[dict], user_prompt: str, doc_text: str):
    """Send message and get response."""
    try:
        prompt = user_prompt.strip()
        validate_input(prompt)
        
        if not prompt:
            return history, gr.update(), doc_text, gr.update(visible=False)
        
        # Combine prompt with document text if available
        full_prompt = (prompt + "\n\n" + doc_text.strip()) if doc_text else prompt
        
        reply = await _mcp_reply(full_prompt)
        
        # Clear textbox, doc state, and hide file icon after sending
        return (
            history + [{"role": "user", "content": prompt}, {"role": "assistant", "content": reply}], 
            "", 
            "", 
            gr.update(visible=False)
        )
    except Exception as e:
        error_msg = error_handler.handle_agent_error(e)
        return history + [{"role": "user", "content": user_prompt}, {"role": "assistant", "content": error_msg}], "", doc_text, gr.update(visible=False)


def _handle_upload(file_list):
    """Handle file upload and text extraction."""
    try:
        validate_file_upload(file_list)
        
        combined_text, has_files = process_file_upload(file_list)
        
        if not has_files:
            return "", gr.update(visible=False)
        
        # Count successful files for icon
        file_count = len([f for f in (file_list if isinstance(file_list, list) else [file_list]) if f is not None])
        
        # Update file icon
        if file_count == 1:
            icon_html = "<div class='file-indicator'>📄</div>"
        else:
            icon_html = f"<div class='file-indicator' title='{file_count} files'>📁<span style='font-size:10px;position:absolute;top:-2px;right:-2px;background:#FF5C8D;border-radius:50%;padding:1px 3px;min-width:12px;text-align:center;'>{file_count}</span></div>"
        
        return combined_text, gr.update(value=icon_html, visible=True)
        
    except Exception as e:
        error_msg = error_handler.handle_file_error(e, "uploaded files")
        error_handler.log_error(f"File upload error: {e}")
        return "", gr.update(visible=False)

def create_interface():
    """Create the Gradio interface."""
    with gr.Blocks(css=UIConfig.CSS) as demo:
        gr.Markdown("## What's on your mind today?", elem_id="page")
        gr.Markdown("Upload documents and ask questions or request analysis.")

        doc_state = gr.State("")

        with gr.Column(elem_classes="input-box", elem_id="page"):
            txt = gr.Textbox(
                placeholder="Ask anything", 
                show_label=False, 
                lines=1,
                max_lines=3
            )
            with gr.Row(elem_classes="icon-row"):
                upload = gr.UploadButton(
                    "+", 
                    file_types=["file"], 
                    file_count="multiple", 
                    elem_classes="icon-btn"
                )
                file_icon = gr.HTML(
                    "<div class='file-indicator'>📄</div>", 
                    visible=False
                )
                send = gr.Button("➤", elem_classes="icon-btn")

        chat = gr.Chatbot(type="messages", height=400)

        # Event handlers
        send.click(
            _send, 
            [chat, txt, doc_state], 
            [chat, txt, doc_state, file_icon]
        )
        txt.submit(
            _send, 
            [chat, txt, doc_state], 
            [chat, txt, doc_state, file_icon]
        )
        upload.upload(
            _handle_upload, 
            upload, 
            [doc_state, file_icon]
        )
        
    return demo


def main():
    """Main function to run the application."""
    try:
        from dotenv import load_dotenv
        load_dotenv("multi_tool_agent/.env")
        
        demo = create_interface()
        demo.launch(
            share=True,
            server_name="0.0.0.0",
            server_port=7860
        )
    except Exception as e:
        error_handler.log_error(f"Failed to start application: {e}", exc_info=True)
        print(f"Application failed to start: {e}")

if __name__ == "__main__":
    main()

