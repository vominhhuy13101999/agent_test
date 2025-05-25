import streamlit as st
from document_extractor import extract_text
from document_comparator import compare_texts

st.title("Document Comparison Tool")
file1 = st.file_uploader("Choose the first document", type=["pdf", "docx"])
file2 = st.file_uploader("Choose the second document", type=["pdf", "docx"])

if file1 and file2:
    text1 = extract_text(file1.name)
    text2 = extract_text(file2.name)
    st.write("Differences Found:")
    st.text(compare_texts(text1, text2))
