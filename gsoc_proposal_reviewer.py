import streamlit as st

from utils.helpers import setup_page_config, process_proposal
from styles.app_styles import get_app_styles
from components.ui_components import (
    render_header, render_tips_section, render_file_info,
    render_metrics_display, render_strengths_weaknesses, render_timeline,
    render_detailed_feedback, render_export_options, render_about_section,
    render_footer
)
from services.ai_service import initialize_genai

# page setup
setup_page_config()
st.markdown(get_app_styles(), unsafe_allow_html=True)

render_header()

tab1, tab2 = st.tabs(["Submit Proposal", "About GSoC Proposals"])

with tab1:
    col1, col2 = st.columns([3, 2])
    
    with col1:
        uploaded_file = st.file_uploader("Upload your GSoC proposal (PDF)", type="pdf")
        problem_statement = st.text_area("Enter the project/problem statement", height=150)
        reviewer_mode = st.checkbox("I am a project mentor/reviewer")
        
        submit_button = st.button("Generate Feedback", type="primary", disabled=not uploaded_file)
    
    with col2:
        render_tips_section()
        render_file_info(uploaded_file)

    if submit_button and uploaded_file:
        with st.spinner("Analyzing your proposal..."):
            client = initialize_genai()
            
            if uploaded_file:
                results = process_proposal(client, uploaded_file, problem_statement, reviewer_mode)
                
                if results['success']:
                    st.session_state.metrics = results['metrics']
                    st.session_state.timeline = results['timeline']
                    st.session_state.feedback = results['feedback']
                    st.session_state.has_feedback = True
            else:
                st.error("Could not process the PDF. Please try again with a different file.")

    if 'has_feedback' in st.session_state and st.session_state.has_feedback:
        st.markdown("## Proposal Analysis")
        
        overall_score = render_metrics_display(st.session_state.metrics)
        render_strengths_weaknesses(st.session_state.metrics)
        render_timeline(st.session_state.timeline)
        render_detailed_feedback(st.session_state.feedback)
        render_export_options(
            st.session_state.metrics,
            st.session_state.timeline,
            st.session_state.feedback,
            overall_score
        )

with tab2:
    render_about_section()

render_footer()
