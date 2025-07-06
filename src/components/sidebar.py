"""
Sidebar Component
Provides navigation, information, and settings
"""

import streamlit as st

# Unicode symbols for UI
SYMBOLS = {
    'rocket': '🚀',
    'gear': '⚙️',
    'info': 'ℹ️',
    'star': '⭐',
    'check': '✅',
    'document': '📋',
    'magic': '✨',
    'github': '🔗',
    'api': '🔑',
    'free': '🆓',
    'warning': '⚠️',
    'trophy': '🏆',
    'heart': '❤️',
    'world': '🌍'
}

def render_sidebar():
    """Render the application sidebar"""

    with st.sidebar:
        # App info header
        st.markdown(f"""
        ### {SYMBOLS['rocket']} AI Resume Enhancer
        **Free Version - No Paid APIs!**
        """)

        st.markdown("---")

        # Current status
        render_status_section()

        st.markdown("---")

        # Features section
        render_features_section()

        st.markdown("---")

        # API Configuration
        render_api_section()

        st.markdown("---")

        # Tips and help
        render_tips_section()

        st.markdown("---")

        # About section
        render_about_section()

def render_status_section():
    """Render current processing status"""
    st.markdown(f"#### {SYMBOLS['info']} Current Status")

    if 'processing_stage' in st.session_state:
        stage = st.session_state.processing_stage

        if stage == 'upload':
            st.info(f"{SYMBOLS['document']} Ready to upload resume")
        elif stage == 'uploaded':
            st.success(f"{SYMBOLS['check']} File uploaded successfully")
        elif stage == 'processed':
            st.success(f"{SYMBOLS['magic']} Resume enhanced successfully")
        else:
            st.info(f"{SYMBOLS['gear']} Processing...")
    else:
        st.info(f"{SYMBOLS['document']} Ready to get started")

    # Show file info if available
    if 'uploaded_file' in st.session_state and st.session_state.uploaded_file:
        file = st.session_state.uploaded_file
        st.write(f"**File:** {file.name}")
        st.write(f"**Size:** {format_file_size(file.size)}")

def render_features_section():
    """Render features and capabilities"""
    st.markdown(f"#### {SYMBOLS['star']} Features")

    features = [
        f"{SYMBOLS['check']} Resume content analysis",
        f"{SYMBOLS['check']} AI-powered enhancement",
        f"{SYMBOLS['check']} Skills optimization",
        f"{SYMBOLS['check']} ATS compatibility check",
        f"{SYMBOLS['check']} Cover letter generation",
        f"{SYMBOLS['check']} Multiple export formats"
    ]

    for feature in features:
        st.markdown(f"• {feature}")

def render_api_section():
    """Render API configuration section"""
    st.markdown(f"#### {SYMBOLS['api']} API Configuration")

    # Check if Gemini API key is configured
    api_key_status = check_api_key_status()

    if api_key_status['configured']:
        st.success(f"{SYMBOLS['check']} Gemini API configured")
    else:
        st.error(f"{SYMBOLS['warning']} Gemini API not configured")

        with st.expander("How to setup Gemini API"):
            st.markdown("""
            1. Go to [Google AI Studio](https://aistudio.google.com/)
            2. Click "Get API Key"
            3. Create a new API key
            4. Add it to your environment:
               - For local: Set `GEMINI_API_KEY` environment variable
               - For Streamlit Cloud: Add to secrets.toml
            """)

    # Show current models being used
    st.markdown("**Free Models Used:**")
    st.markdown(f"• {SYMBOLS['free']} Google Gemini 1.5 Flash")
    st.markdown(f"• {SYMBOLS['free']} HuggingFace Transformers")
    st.markdown(f"• {SYMBOLS['free']} spaCy NLP")

def render_tips_section():
    """Render tips and best practices"""
    st.markdown(f"#### {SYMBOLS['star']} Tips for Best Results")

    with st.expander("📄 Resume Tips"):
        st.markdown("""
        • Use a clear, standard format
        • Include contact information at the top
        • List skills and experience clearly
        • Use bullet points for achievements
        • Quantify results where possible
        • Keep formatting simple and clean
        """)

    with st.expander("🎯 Enhancement Tips"):
        st.markdown("""
        • Provide detailed work experience
        • Include specific technologies used
        • Mention measurable achievements
        • Add relevant keywords for your field
        • Ensure consistent formatting
        • Review AI suggestions carefully
        """)

def render_about_section():
    """Render about and links section"""
    st.markdown(f"#### {SYMBOLS['heart']} About")

    st.markdown(f"""
    This AI Resume Enhancer is built with:

    • {SYMBOLS['free']} **100% Free APIs**
    • {SYMBOLS['world']} **Open Source Technologies**
    • {SYMBOLS['gear']} **No Account Required**
    • {SYMBOLS['trophy']} **Professional Results**

    **Powered by:**
    • Google Gemini API (Free)
    • HuggingFace Transformers
    • spaCy NLP Library
    • Streamlit Framework
    """)

    # Links section
    st.markdown("**Resources:**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"{SYMBOLS['github']} GitHub"):
            st.write("https://github.com/your-repo")

    with col2:
        if st.button(f"{SYMBOLS['info']} Documentation"):
            st.write("Check the docs/ folder")

    # Clear data button
    st.markdown("---")
    if st.button(f"{SYMBOLS['warning']} Clear All Data", type="secondary"):
        clear_all_session_data()

def check_api_key_status():
    """Check if API keys are properly configured"""
    import os

    # Check for Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')

    if not gemini_key:
        try:
            gemini_key = st.secrets.get('GEMINI_API_KEY')
        except:
            pass

    return {
        'configured': bool(gemini_key),
        'gemini_api': bool(gemini_key)
    }

def clear_all_session_data():
    """Clear all session data"""
    keys_to_keep = ['uploaded_file_key']  # Keep file uploader key

    keys_to_clear = [key for key in st.session_state.keys() if key not in keys_to_keep]

    for key in keys_to_clear:
        del st.session_state[key]

    st.success(f"{SYMBOLS['check']} All data cleared!")
    st.experimental_rerun()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"
