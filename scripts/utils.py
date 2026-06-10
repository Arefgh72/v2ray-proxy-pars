"""
Utility functions for the v2ray proxy parser.
"""

def log_error(module_name: str, message: str, error_details: str = ""):
    """
    Log error messages to console.
    
    Args:
        module_name: Name of the module where the error occurred
        message: Description of the error
        error_details: Additional error details (usually exception message)
    """
    error_msg = f"[ERROR] {module_name}: {message}"
    if error_details:
        error_msg += f" | Details: {error_details}"
    print(error_msg)

def log_info(message: str):
    """
    Log info messages to console.
    
    Args:
        message: Information message to log
    """
    print(f"[INFO] {message}")

def log_warning(message: str):
    """
    Log warning messages to console.
    
    Args:
        message: Warning message to log
    """
    print(f"[WARNING] {message}")
