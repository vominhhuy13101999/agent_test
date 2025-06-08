"""
Agent Test Source Package

This package contains the refactored modular components for the agent test application.
"""

__version__ = "1.0.0"

# Import main classes for easy access
from .config import AppConfig, UIConfig, MCPConfig, Role
from .error_handler import ErrorHandler
from .document_extractor import DocumentExtractor
from .document_comparator import DocumentComparator
from .agent_manager import AgentManager, MCPAgentManager
from .pdf_processor import PDFProcessor, DocumentRouter

__all__ = [
    "AppConfig",
    "UIConfig", 
    "MCPConfig",
    "Role",
    "ErrorHandler",
    "DocumentExtractor",
    "DocumentComparator", 
    "AgentManager",
    "MCPAgentManager",
    "PDFProcessor",
    "DocumentRouter"
]