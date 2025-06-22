#!/usr/bin/env python3
"""
Test the improved display formatting for Gradio.
"""

import gradio as gr
from src.pdf_processor import PDFProcessor

def create_test_interface():
    """Create a test interface to demonstrate improved formatting."""
    
    processor = PDFProcessor()
    
    # Create sample data that shows the formatting improvements
    sample_extractions = [
        {
            'document_name': 'Lease_Document_1.pdf',
            'extractions': [
                {'question': 'What is the effective Date of Lease Contract?', 'answer': 'June 25, 2022'},
                {'question': 'Who are the named Residents on the Lease?', 'answer': 'Huy Vo, Enkh-Amgalan Batburen'},
                {'question': 'What is the Owners Name?', 'answer': 'RXR EMF Atlantic Station REIT LLC'},
                {'question': 'What is the Dwelling Unit address?', 'answer': 'Unit No. 11B at 355 Atlantic Street, Stamford, Connecticut, 06901'}
            ]
        },
        {
            'document_name': 'julius_leasing_documents.pdf',
            'extractions': [
                {'question': 'What is the effective Date of Lease Contract?', 'answer': 'September 3, 2024'},
                {'question': 'Who are the named Residents on the Lease?', 'answer': 'Huy Vo'},
                {'question': 'What is the Owners Name?', 'answer': 'QOZB V,LLC'},
                {'question': 'What is the Dwelling Unit address?', 'answer': 'Dwelling Unit No. 442 at 777 Summer St #442, Stamford, Connecticut, 06901'}
            ]
        }
    ]
    
    def show_comparison():
        """Show the improved comparison formatting."""
        result = processor._create_comparison_result("Compare these lease documents", sample_extractions)
        return result
    
    def show_old_format():
        """Show what the old format looked like."""
        return """### Document 1: Lease_Document 1.pdf\\n- **What is the effective 'Date of Lease Contract'?**: June 25, 2022\\n- **Who are the named 'Resident(s)'?**: Huy Vo, Enkh-Amgalan Batburen\\n\\n### Document 2: julius leasing documents.pdf\\n- **What is the effective 'Date of Lease Contract'?**: September 3, 2024\\n- **Who are the named 'Resident(s)'?**: Huy Vo"""
    
    with gr.Blocks(title="Display Formatting Test") as demo:
        gr.Markdown("# 🎨 Display Formatting Comparison")
        gr.Markdown("Compare the old vs new formatting for document analysis results.")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## ❌ Old Format (Bad)")
                old_output = gr.Markdown()
                gr.Button("Show Old Format").click(
                    show_old_format,
                    outputs=old_output
                )
            
            with gr.Column():
                gr.Markdown("## ✅ New Format (Good)")
                new_output = gr.Markdown()
                gr.Button("Show New Format").click(
                    show_comparison,
                    outputs=new_output
                )
        
        gr.Markdown("### Key Improvements:")
        gr.Markdown("""
        - ✅ Proper markdown rendering (no escaped \\n)
        - ✅ Better visual hierarchy with emojis
        - ✅ Clear document separation with horizontal rules
        - ✅ Cleaner question/answer formatting
        - ✅ Highlighted key differences
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_test_interface()
    demo.launch(share=False, server_port=7862)