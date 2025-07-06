"""
Validators Utility
Validates environment, inputs, and system requirements
"""

import os
import logging
from typing import Dict, List, Any

def validate_environment() -> Dict[str, Any]:
    """Validate that all required dependencies and configurations are available"""

    validation_result = {
        'valid': True,
        'issues': [],
        'warnings': []
    }

    # Check Python libraries
    library_checks = check_required_libraries()
    if not library_checks['all_available']:
        validation_result['valid'] = False
        validation_result['issues'].extend(library_checks['missing'])

    # Check API configuration
    api_checks = check_api_configuration()
    if not api_checks['gemini_configured']:
        validation_result['warnings'].append("Gemini API not configured - AI features will use fallback mode")

    # Check spaCy models
    spacy_checks = check_spacy_models()
    if not spacy_checks['model_available']:
        validation_result['warnings'].append("spaCy English model not found - will attempt to download")

    return validation_result

def check_required_libraries() -> Dict[str, Any]:
    """Check if all required Python libraries are available"""

    required_libraries = [
        'streamlit',
        'google.generativeai', 
        'transformers',
        'spacy',
        'docx',
        'PyPDF2',
        'pandas'
    ]

    missing_libraries = []
    available_libraries = []

    for lib in required_libraries:
        try:
            __import__(lib.replace('google.generativeai', 'google.generativeai'))
            available_libraries.append(lib)
        except ImportError:
            missing_libraries.append(lib)

    return {
        'all_available': len(missing_libraries) == 0,
        'available': available_libraries,
        'missing': missing_libraries
    }

def check_api_configuration() -> Dict[str, Any]:
    """Check API key configuration"""

    # Check Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')

    if not gemini_key:
        try:
            import streamlit as st
            gemini_key = st.secrets.get('GEMINI_API_KEY')
        except:
            pass

    return {
        'gemini_configured': bool(gemini_key)
    }

def check_spacy_models() -> Dict[str, Any]:
    """Check if required spaCy models are available"""

    try:
        import spacy

        # Try to load English model
        try:
            nlp = spacy.load("en_core_web_sm")
            model_available = True
        except OSError:
            model_available = False

        return {
            'spacy_available': True,
            'model_available': model_available
        }

    except ImportError:
        return {
            'spacy_available': False,
            'model_available': False
        }

def validate_file_upload(file_data: bytes, file_type: str, file_name: str) -> Dict[str, Any]:
    """Validate uploaded file data"""

    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    # File size check (10MB limit)
    max_size = 10 * 1024 * 1024
    if len(file_data) > max_size:
        validation_result['valid'] = False
        validation_result['errors'].append(f"File size exceeds 10MB limit")

    # File type check
    allowed_types = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
        'text/plain'
    ]

    if file_type not in allowed_types:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Unsupported file type: {file_type}")

    # File name validation
    if not file_name or len(file_name.strip()) == 0:
        validation_result['valid'] = False
        validation_result['errors'].append("Invalid file name")

    # Content validation
    if len(file_data) == 0:
        validation_result['valid'] = False
        validation_result['errors'].append("File appears to be empty")

    return validation_result

def validate_user_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user questionnaire input"""

    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    # Check required fields
    required_fields = ['desired_role']

    for field in required_fields:
        if field not in input_data or not input_data[field].strip():
            validation_result['warnings'].append(f"Consider filling out the {field.replace('_', ' ')} field")

    # Validate specific fields
    if 'expected_salary' in input_data and input_data['expected_salary']:
        salary = input_data['expected_salary'].strip()
        if salary and not any(char.isdigit() for char in salary):
            validation_result['warnings'].append("Salary field should contain numeric values")

    return validation_result

def validate_content_extraction(content: str) -> Dict[str, Any]:
    """Validate extracted content quality"""

    validation_result = {
        'valid': True,
        'quality_score': 0,
        'issues': [],
        'suggestions': []
    }

    if not content or len(content.strip()) == 0:
        validation_result['valid'] = False
        validation_result['issues'].append("No content extracted from file")
        return validation_result

    # Calculate quality score
    quality_score = 0

    # Length check
    if len(content) > 100:
        quality_score += 20

    # Check for common resume sections
    sections = ['experience', 'education', 'skills', 'summary', 'objective']
    found_sections = sum(1 for section in sections if section.lower() in content.lower())
    quality_score += found_sections * 15

    # Check for contact information
    import re
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
        quality_score += 15

    if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content):
        quality_score += 10

    # Check for bullet points or structured content
    if '•' in content or '*' in content or content.count('\n') > 5:
        quality_score += 10

    validation_result['quality_score'] = min(quality_score, 100)

    # Add suggestions based on quality
    if validation_result['quality_score'] < 50:
        validation_result['suggestions'].append("Content quality seems low - ensure the file is not corrupted")

    if found_sections < 2:
        validation_result['suggestions'].append("Consider using a more structured resume format")

    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
        validation_result['suggestions'].append("Make sure your contact email is clearly visible")

    return validation_result

def setup_logging():
    """Setup application logging"""

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Suppress some verbose logs
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging"""

    import platform
    import sys

    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'python_version': sys.version,
        'architecture': platform.machine()
    }
