"""
Validation Utilities
Validates files, inputs, and API responses
"""
import os
from typing import Optional, Tuple
from pathlib import Path


def validate_file_upload(file, max_size_mb: int = 10) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded contract file

    Args:
        file: Uploaded file object
        max_size_mb: Maximum file size in MB

    Returns:
        Tuple of (is_valid, error_message)
    """
    if file is None:
        return False, "No file provided"

    # Check file size
    file_size = file.size if hasattr(file, 'size') else len(file.read())
    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        return False, f"File size ({file_size // (1024*1024)}MB) exceeds maximum allowed size ({max_size_mb}MB)"

    if file_size == 0:
        return False, "File is empty"

    # Check file extension
    filename = file.name if hasattr(file, 'name') else 'unknown'
    ext = Path(filename).suffix.lower()

    allowed_extensions = ['.pdf', '.docx', '.doc']
    if ext not in allowed_extensions:
        return False, f"File type '{ext}' not supported. Please upload PDF or DOCX files."

    # Check MIME type
    if hasattr(file, 'type'):
        allowed_mimes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword'
        ]
        if file.type not in allowed_mimes:
            return False, f"Invalid file type: {file.type}"

    return True, None


def validate_api_response(response: dict, required_fields: list) -> Tuple[bool, Optional[str]]:
    """
    Validate API response structure

    Args:
        response: API response dictionary
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(response, dict):
        return False, "Response is not a valid dictionary"

    missing_fields = [field for field in required_fields if field not in response]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    # Check for error field
    if 'error' in response:
        return False, f"API Error: {response['error']}"

    return True, None


def validate_risk_score(score: int) -> Tuple[bool, Optional[str]]:
    """
    Validate risk score is in valid range

    Args:
        score: Risk score value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(score, int):
        return False, "Risk score must be an integer"

    if score < 1 or score > 10:
        return False, f"Risk score {score} is out of valid range (1-10)"

    return True, None


def validate_analysis_results(results: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate complete analysis results structure

    Args:
        results: Analysis results dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = [
        'job_id',
        'risk_score',
        'risk_level',
        'recommendation'
    ]

    is_valid, error = validate_api_response(results, required_fields)
    if not is_valid:
        return False, error

    # Validate risk score
    risk_score = results.get('risk_score')
    is_valid, error = validate_risk_score(risk_score)
    if not is_valid:
        return False, error

    # Check optional but expected fields
    if 'entities' in results and not isinstance(results['entities'], dict):
        return False, "Invalid entities structure"

    if 'high_risk_clauses' in results and not isinstance(results['high_risk_clauses'], list):
        return False, "Invalid high_risk_clauses structure"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    sanitized = filename

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')

    # Limit length
    max_length = 255
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:max_length - len(ext)] + ext

    return sanitized
