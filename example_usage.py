#!/usr/bin/env python3
"""
Example usage of the refactored agent_test components.
"""

import asyncio
from src import AppConfig, Role, ErrorHandler, DocumentComparator

def example_config_usage():
    """Demonstrate configuration usage."""
    print("📋 Configuration Example:")
    print(f"  App Name: {AppConfig.APP_NAME}")
    print(f"  Model: {AppConfig.MODEL_NAME}")
    print(f"  Max Content: {AppConfig.MAX_CONTENT_LENGTH}")
    print(f"  User Role: {Role.USER}")
    print()

def example_error_handling():
    """Demonstrate error handling."""
    print("🛡️ Error Handling Example:")
    
    handler = ErrorHandler("example")
    
    # Simulate different error types
    class MockRateError(Exception):
        def __str__(self):
            return "429 Too Many Requests"
    
    result = handler.handle_agent_error(MockRateError())
    print(f"  Rate limit error: {result}")
    
    result = handler.handle_file_error(FileNotFoundError(), "missing.pdf")
    print(f"  File error: {result}")
    print()

def example_document_comparison():
    """Demonstrate document comparison."""
    print("📄 Document Comparison Example:")
    
    comparator = DocumentComparator()
    
    # Basic text comparison
    text1 = "The quick brown fox jumps over the lazy dog"
    text2 = "The quick brown fox leaps over the lazy cat"
    
    diff = comparator.compare_texts(text1, text2)
    print(f"  Text differences found: {len(diff.splitlines())} lines")
    
    # Structured comparison
    extractions = [
        {
            "document_name": "contract1.pdf",
            "extractions": [
                {"question": "What is the price?", "answer": "$100"},
                {"question": "What is the duration?", "answer": "1 year"}
            ]
        },
        {
            "document_name": "contract2.pdf", 
            "extractions": [
                {"question": "What is the price?", "answer": "$150"},
                {"question": "What is the duration?", "answer": "2 years"}
            ]
        }
    ]
    
    result = comparator.create_structured_comparison(extractions)
    print(f"  Structured comparison: {len(result)} characters")
    print()

async def example_agent_manager():
    """Demonstrate agent manager (without API calls)."""
    print("🤖 Agent Manager Example:")
    
    try:
        from src.agent_manager import AgentManager
        
        manager = AgentManager()
        
        # Test fallback questions generation
        questions = manager.get_fallback_questions(
            "lease agreement", 
            [("lease.pdf", "monthly rent $1000 landlord tenant")]
        )
        
        print(f"  Generated {len(questions)} questions for lease documents")
        print(f"  Sample question: {questions[0]}")
        print()
        
    except Exception as e:
        print(f"  Note: Agent manager requires API setup: {e}")
        print()

def main():
    """Run all examples."""
    print("🚀 Refactored Agent Test - Usage Examples\n")
    
    example_config_usage()
    example_error_handling()
    example_document_comparison()
    asyncio.run(example_agent_manager())
    
    print("✅ All examples completed successfully!")
    print("\n📚 To use the applications:")
    print("  python gradio_app.py      # Simple interface")
    print("  python gradio_app_2.py    # Advanced multi-agent interface")
    print("  python main.py            # Command-line interface")

if __name__ == "__main__":
    main()