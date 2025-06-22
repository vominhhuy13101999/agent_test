import streamlit as st
from document_extractor import DocumentExtractor
from document_comparator import DocumentComparator
from error_handler import ErrorHandler, safe_call

# Initialize components
extractor = DocumentExtractor()
comparator = DocumentComparator()
error_handler = ErrorHandler("streamlit_app")

@safe_call(error_handler, "Error extracting text")
def safe_extract_text(file_path: str) -> str:
    return extractor.extract_text(file_path)

@safe_call(error_handler, "Error comparing documents")
def safe_compare_texts(text1: str, text2: str) -> str:
    return comparator.compare_texts(text1, text2)

def main():
    st.title("Document Comparison Tool")
    
    st.markdown("""
    Upload two documents to compare their content and find differences.
    Supported formats: PDF, DOCX, and other document types.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("First Document")
        file1 = st.file_uploader(
            "Choose the first document", 
            type=["pdf", "docx", "txt"],
            key="file1"
        )
    
    with col2:
        st.subheader("Second Document")
        file2 = st.file_uploader(
            "Choose the second document", 
            type=["pdf", "docx", "txt"],
            key="file2"
        )
    
    if file1 and file2:
        with st.spinner("Processing documents..."):
            # Save uploaded files temporarily
            with open(f"temp_{file1.name}", "wb") as f:
                f.write(file1.getbuffer())
            with open(f"temp_{file2.name}", "wb") as f:
                f.write(file2.getbuffer())
            
            # Extract text
            text1 = safe_extract_text(f"temp_{file1.name}")
            text2 = safe_extract_text(f"temp_{file2.name}")
            
            if "Error" not in text1 and "Error" not in text2:
                # Show document info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Document 1 Length", f"{len(text1)} chars")
                with col2:
                    st.metric("Document 2 Length", f"{len(text2)} chars")
                
                # Compare documents
                st.subheader("Comparison Results")
                
                # Basic diff
                differences = safe_compare_texts(text1, text2)
                if differences and "Error" not in differences:
                    st.text_area("Differences Found:", differences, height=300)
                    
                    # Show unified diff as well
                    st.subheader("Unified Diff")
                    unified = comparator.unified_diff(text1, text2, file1.name, file2.name)
                    st.code(unified, language="diff")
                else:
                    st.warning("No significant differences found or error in comparison.")
                
                # Show document previews
                with st.expander("Document Previews"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader(f"Preview: {file1.name}")
                        st.text_area("Content", text1[:1000] + "..." if len(text1) > 1000 else text1, height=200)
                    with col2:
                        st.subheader(f"Preview: {file2.name}")
                        st.text_area("Content", text2[:1000] + "..." if len(text2) > 1000 else text2, height=200)
            else:
                st.error("Failed to extract text from one or both documents.")
                if "Error" in text1:
                    st.error(f"Document 1: {text1}")
                if "Error" in text2:
                    st.error(f"Document 2: {text2}")
            
            # Cleanup temp files
            import os
            try:
                os.remove(f"temp_{file1.name}")
                os.remove(f"temp_{file2.name}")
            except:
                pass
    else:
        st.info("Please upload two documents to start comparison.")

if __name__ == "__main__":
    main()
