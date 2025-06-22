#!/usr/bin/env python3
"""
Test script to validate the refactored agent_test codebase.
"""

import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing imports...")
    
    try:
        from src.config import AppConfig, UIConfig, MCPConfig
        print("✅ Config module")
        
        from src.error_handler import ErrorHandler
        print("✅ Error handler module")
        
        from src.document_extractor import DocumentExtractor, process_file_upload
        print("✅ Document extractor module")
        
        from src.document_comparator import DocumentComparator, parse_document_sections
        print("✅ Document comparator module")
        
        from src.agent_manager import AgentManager, MCPAgentManager
        print("✅ Agent manager module")
        
        from src.pdf_processor import PDFProcessor, DocumentRouter
        print("✅ PDF processor module")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration values."""
    print("\n🧪 Testing configuration...")
    
    try:
        from src.config import AppConfig, UIConfig
        
        assert AppConfig.APP_NAME == "Multi-Agent PDF Analyzer"
        assert AppConfig.MAX_CONTENT_LENGTH == 80000
        assert UIConfig.MAX_WIDTH == "960px"
        
        print("✅ Configuration values are correct")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_error_handler():
    """Test error handling functionality."""
    print("\n🧪 Testing error handler...")
    
    try:
        from src.error_handler import ErrorHandler, ValidationError
        
        handler = ErrorHandler("test")
        
        # Test rate limit error
        class MockRateError(Exception):
            def __str__(self):
                return "429 Rate limit exceeded"
        
        result = handler.handle_agent_error(MockRateError())
        assert "Rate limit exceeded" in result
        
        # Test file error
        result = handler.handle_file_error(FileNotFoundError(), "test.pdf")
        assert "File not found" in result
        
        print("✅ Error handler working correctly")
        return True
    except Exception as e:
        print(f"❌ Error handler test failed: {e}")
        return False

def test_document_comparator():
    """Test document comparison functionality."""
    print("\n🧪 Testing document comparator...")
    
    try:
        from src.document_comparator import DocumentComparator, parse_document_sections
        
        comparator = DocumentComparator()
        
        # Test basic comparison
        diff = comparator.compare_texts("hello world", "hello universe")
        assert "world" in diff or "universe" in diff
        
        # Test document parsing
        doc_text = "--- file1.pdf ---\nContent 1\n\n--- file2.pdf ---\nContent 2"
        sections = parse_document_sections(doc_text)
        assert len(sections) == 2
        assert sections[0][0] == "file1.pdf"
        assert sections[1][0] == "file2.pdf"
        
        print("✅ Document comparator working correctly")
        return True
    except Exception as e:
        print(f"❌ Document comparator test failed: {e}")
        return False

async def test_agent_manager():
    """Test agent manager (without actual API calls)."""
    print("\n🧪 Testing agent manager...")
    
    try:
        from src.agent_manager import AgentManager
        
        manager = AgentManager()
        
        # Test fallback questions
        questions = manager.get_fallback_questions("lease agreement", [("test.pdf", "rent landlord")])
        assert len(questions) > 0
        assert any("rent" in q.lower() for q in questions)
        
        print("✅ Agent manager basic functionality working")
        return True
    except Exception as e:
        print(f"❌ Agent manager test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting refactored codebase tests...\n")
    
    tests = [
        test_imports,
        test_config,
        test_error_handler,
        test_document_comparator,
    ]
    
    # Run async test
    async_tests = [test_agent_manager]
    
    results = []
    
    # Run synchronous tests
    for test in tests:
        results.append(test())
    
    # Run async tests
    for test in async_tests:
        results.append(asyncio.run(test()))
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactoring successful.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())