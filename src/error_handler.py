import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps

class ErrorHandler:
    """Centralized error handling for the application."""
    
    def __init__(self, logger_name: str = "agent_app"):
        self.logger = logging.getLogger(logger_name)
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging configuration."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def handle_agent_error(self, error: Exception) -> str:
        """Handle agent-related errors and return user-friendly message."""
        error_str = str(error)
        
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            self.logger.warning(f"Rate limit exceeded: {error}")
            return "Rate limit exceeded. Please try again in a moment."
        
        if "INVALID_ARGUMENT" in error_str:
            self.logger.error(f"Invalid argument error: {error}")
            return "Invalid request format. Please check your input."
        
        if "PERMISSION_DENIED" in error_str:
            self.logger.error(f"Permission denied: {error}")
            return "Access denied. Please check your credentials."
        
        if "UNAVAILABLE" in error_str:
            self.logger.error(f"Service unavailable: {error}")
            return "Service temporarily unavailable. Please try again later."
        
        # Generic error
        self.logger.error(f"Unexpected error: {error}", exc_info=True)
        return f"An unexpected error occurred: {error}"
    
    def handle_file_error(self, error: Exception, file_path: str) -> str:
        """Handle file processing errors."""
        self.logger.error(f"File processing error for {file_path}: {error}")
        
        if "No such file" in str(error) or "FileNotFoundError" in str(type(error).__name__):
            return f"File not found: {file_path}"
        
        if "PermissionError" in str(type(error).__name__):
            return f"Permission denied accessing file: {file_path}"
        
        if "UnicodeDecodeError" in str(type(error).__name__):
            return f"Could not read file (encoding issue): {file_path}"
        
        return f"Error processing file {file_path}: {error}"
    
    def handle_json_error(self, error: Exception, response: str) -> dict:
        """Handle JSON parsing errors."""
        self.logger.warning(f"JSON parsing failed: {error}. Response: {response[:200]}...")
        return {}
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def log_info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def log_error(self, message: str, exc_info: bool = False):
        """Log an error message."""
        self.logger.error(message, exc_info=exc_info)

def safe_async_call(error_handler: ErrorHandler, fallback_message: str = "Operation failed"):
    """Decorator for safe async function calls."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler.log_error(f"Error in {func.__name__}: {e}", exc_info=True)
                if "agent" in func.__name__.lower():
                    return error_handler.handle_agent_error(e)
                return fallback_message
        return wrapper
    return decorator

def safe_call(error_handler: ErrorHandler, fallback_value: Any = None):
    """Decorator for safe synchronous function calls."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.log_error(f"Error in {func.__name__}: {e}", exc_info=True)
                return fallback_value
        return wrapper
    return decorator

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class ProcessingError(Exception):
    """Custom exception for processing errors."""
    pass

def validate_input(prompt: str, pdf_contents: list = None) -> None:
    """Validate user input."""
    if not prompt or not prompt.strip():
        raise ValidationError("Prompt cannot be empty")
    
    if len(prompt) > 10000:  # Reasonable limit
        raise ValidationError("Prompt is too long (max 10,000 characters)")
    
    if pdf_contents is not None:
        if len(pdf_contents) > 10:  # Reasonable limit
            raise ValidationError("Too many files uploaded (max 10)")
        
        for filename, content in pdf_contents:
            if not filename or not content:
                raise ValidationError(f"Invalid file content: {filename}")

def validate_file_upload(file_list) -> None:
    """Validate file upload."""
    if not file_list:
        return
    
    files = file_list if isinstance(file_list, list) else [file_list]
    
    if len(files) > 10:
        raise ValidationError("Too many files (max 10)")
    
    for file_obj in files:
        if file_obj is None:
            continue
        
        # Basic file validation
        file_path = getattr(file_obj, 'name', str(file_obj))
        if not file_path:
            raise ValidationError("Invalid file path")
        
        # Check file size (if available)
        if hasattr(file_obj, 'size') and file_obj.size > 50 * 1024 * 1024:  # 50MB
            raise ValidationError(f"File too large: {file_path} (max 50MB)")