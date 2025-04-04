import streamlit as st

def setup_page_config():
    st.set_page_config(
        page_title="GSoC Proposal Reviewer",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def process_proposal(client, uploaded_file, problem_statement, reviewer_mode):
    from services.ai_service import analyze_proposal_metrics, extract_project_timeline, get_ai_review
    
    progress_bar = st.progress(0)
    results = {}
    
    try:
        progress_bar.progress(20)
        metrics = analyze_proposal_metrics(client, uploaded_file, problem_statement)
        results['metrics'] = metrics
        
        progress_bar.progress(40)
        timeline = extract_project_timeline(client, uploaded_file)
        results['timeline'] = timeline
        
        progress_bar.progress(70)
        feedback = get_ai_review(client, uploaded_file, problem_statement, reviewer_mode)
        results['feedback'] = feedback
        
        progress_bar.progress(100)
        results['success'] = True
    except Exception as e:
        st.error(f"Error processing proposal: {str(e)}")
        results['success'] = False
    finally:
        progress_bar.empty()
        
    return results
