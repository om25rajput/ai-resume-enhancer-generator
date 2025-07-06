"""
AI Resume Enhancer & Cover Letter Generator
Free Version - No Paid APIs Required

Uses:
- Google Gemini API (Free tier)
- HuggingFace Transformers (Free)
- spaCy NLP (Free)
- Unicode symbols instead of images
"""

import streamlit as st
import sys
import os
from pathlib import Path
import traceback

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Import our modules
try:
    from components.sidebar import render_sidebar
    from components.file_upload import handle_file_upload
    from components.resume_display import display_resume
    from services.document_parser import DocumentParser
    from services.ai_enhancer import AIEnhancer
    from workflows.langgraph_workflow import ResumeWorkflow
    from utils.validators import validate_environment
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.error("Please ensure all dependencies are installed and the file structure is correct.")
    st.stop()

# Unicode symbols for UI
SYMBOLS = {
    'upload': '📄',
    'process': '⚙️',
    'enhance': '✨',
    'download': '⬇️',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'rocket': '🚀',
    'gear': '⚙️',
    'magic': '✨',
    'document': '📋',
    'email': '📧',
    'phone': '📞',
    'location': '📍',
    'skills': '🎯',
    'experience': '💼',
    'education': '🎓',
    'projects': '🔧',
    'star': '⭐',
    'check': '✓',
    'cross': '✗',
    'arrow_right': '→',
    'arrow_down': '↓',
    'bullet': '•',
    'diamond': '♦',
    'circle': '●'
}

def init_session_state():
    """Initialize session state variables"""
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'extracted_content' not in st.session_state:
        st.session_state.extracted_content = None
    if 'enhanced_resume' not in st.session_state:
        st.session_state.enhanced_resume = None
    if 'cover_letter' not in st.session_state:
        st.session_state.cover_letter = None
    if 'processing_stage' not in st.session_state:
        st.session_state.processing_stage = 'upload'

def main():
    """Main application function"""
    st.set_page_config(
        page_title="AI Resume Enhancer (Free)",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    .feature-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }

    .status-box {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-weight: bold;
    }

    .success-box {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }

    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }

    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }

    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>{SYMBOLS['rocket']} AI Resume Enhancer & Cover Letter Generator</h1>
        <p>Free Version - Powered by Google Gemini API & Open Source Tools</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    init_session_state()

    # Validate environment
    env_status = validate_environment()
    if not env_status['valid']:
        st.error(f"{SYMBOLS['error']} Environment validation failed:")
        for issue in env_status['issues']:
            st.error(f"  {SYMBOLS['bullet']} {issue}")
        st.info(f"{SYMBOLS['info']} Please check the deployment guide for setup instructions.")
        return

    # Sidebar
    render_sidebar()

    # Main content area
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"### {SYMBOLS['upload']} Upload Resume")

        # File upload section
        uploaded_file = handle_file_upload()

        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.processing_stage = 'uploaded'

            # Show file info
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.write(f"{SYMBOLS['success']} File uploaded successfully!")
            st.write(f"{SYMBOLS['document']} **File:** {uploaded_file.name}")
            st.write(f"{SYMBOLS['info']} **Size:** {uploaded_file.size:,} bytes")
            st.markdown('</div>', unsafe_allow_html=True)

            # Process button
            if st.button(f"{SYMBOLS['process']} Process Resume", type="primary"):
                process_resume()

        # User questionnaire
        if st.session_state.processing_stage in ['uploaded', 'processed']:
            st.markdown(f"### {SYMBOLS['gear']} Customization")
            render_questionnaire()

    with col2:
        if st.session_state.uploaded_file:
            st.markdown(f"### {SYMBOLS['magic']} Enhanced Resume")
            display_resume(st.session_state.uploaded_file)
        else:
            render_welcome_section()

def process_resume():
    """Process the uploaded resume"""
    try:
        with st.spinner(f"{SYMBOLS['gear']} Processing your resume..."):
            # Initialize components
            parser = DocumentParser()
            enhancer = AIEnhancer()

            # Extract content
            st.write(f"{SYMBOLS['arrow_right']} Extracting content...")
            content = parser.extract_content(st.session_state.uploaded_file)
            st.session_state.extracted_content = content

            # Parse entities
            st.write(f"{SYMBOLS['arrow_right']} Analyzing content...")
            entities = parser.extract_entities(content)

            # Enhance content
            st.write(f"{SYMBOLS['arrow_right']} Enhancing with AI...")
            enhanced = enhancer.enhance_resume(content, entities)
            st.session_state.enhanced_resume = enhanced

            st.session_state.processing_stage = 'processed'

            st.success(f"{SYMBOLS['success']} Resume processed successfully!")

    except Exception as e:
        st.error(f"{SYMBOLS['error']} Error processing resume: {str(e)}")
        st.error("Please check the logs for more details.")

def render_questionnaire():
    """Render the user questionnaire"""
    st.markdown(f"#### {SYMBOLS['info']} Tell us about your goals")

    with st.form("user_questionnaire"):
        desired_role = st.text_input(f"{SYMBOLS['star']} Desired Role/Position")
        experience_level = st.selectbox(
            f"{SYMBOLS['experience']} Experience Level",
            ["Entry Level", "Mid-Level", "Senior Level", "Executive"]
        )
        expected_salary = st.text_input(f"{SYMBOLS['diamond']} Expected Salary Range")
        location = st.text_input(f"{SYMBOLS['location']} Preferred Location")
        work_arrangement = st.selectbox(
            f"{SYMBOLS['gear']} Work Arrangement",
            ["Remote", "Hybrid", "On-site", "Any"]
        )
        start_date = st.date_input(f"{SYMBOLS['calendar']} Available Start Date")
        relocate = st.checkbox(f"{SYMBOLS['location']} Willing to relocate")

        submitted = st.form_submit_button(f"{SYMBOLS['magic']} Generate Cover Letter")

        if submitted and st.session_state.enhanced_resume:
            generate_cover_letter({
                'desired_role': desired_role,
                'experience_level': experience_level,
                'expected_salary': expected_salary,
                'location': location,
                'work_arrangement': work_arrangement,
                'start_date': start_date,
                'relocate': relocate
            })

def generate_cover_letter(user_data):
    """Generate cover letter based on resume and user data"""
    try:
        from services.cover_letter_generator import CoverLetterGenerator

        with st.spinner(f"{SYMBOLS['gear']} Generating cover letter..."):
            generator = CoverLetterGenerator()
            cover_letter = generator.generate(
                resume_content=st.session_state.enhanced_resume,
                user_preferences=user_data
            )
            st.session_state.cover_letter = cover_letter

            st.success(f"{SYMBOLS['success']} Cover letter generated!")

    except Exception as e:
        st.error(f"{SYMBOLS['error']} Error generating cover letter: {str(e)}")

def render_welcome_section():
    """Render welcome section when no file is uploaded"""
    st.markdown(f"""
    ### {SYMBOLS['rocket']} Welcome to AI Resume Enhancer

    <div class="feature-box">
    <h4>{SYMBOLS['magic']} Free AI-Powered Features</h4>
    <ul>
        <li>{SYMBOLS['check']} Resume content enhancement using Google Gemini</li>
        <li>{SYMBOLS['check']} Skills analysis and suggestions</li>
        <li>{SYMBOLS['check']} Professional summary optimization</li>
        <li>{SYMBOLS['check']} Cover letter generation</li>
        <li>{SYMBOLS['check']} ATS-friendly formatting</li>
    </ul>
    </div>

    <div class="info-box">
    <p>{SYMBOLS['info']} <strong>Supported formats:</strong> PDF, DOCX, TXT</p>
    <p>{SYMBOLS['info']} <strong>No account required</strong> - Start enhancing immediately!</p>
    <p>{SYMBOLS['info']} <strong>100% Free</strong> - Powered by open-source technologies</p>
    </div>

    ### {SYMBOLS['gear']} How it works:

    1. {SYMBOLS['upload']} **Upload** your resume in any supported format
    2. {SYMBOLS['process']} **Process** with our AI-powered analysis
    3. {SYMBOLS['magic']} **Enhance** content, skills, and formatting
    4. {SYMBOLS['download']} **Download** your improved resume and cover letter
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
