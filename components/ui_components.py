import streamlit as st
import json
from datetime import datetime

def render_header():
    st.markdown("""
    <div class="header-container">
        <div>
            <span class="logo-text">📝 GSoC Proposal Reviewer</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_tips_section():
    st.info("### Tips for Good Proposals\n"
            "- Clearly define the problem\n"
            "- Provide a detailed implementation plan\n"
            "- Include a realistic timeline\n"
            "- Demonstrate your technical capabilities\n"
            "- Explain your motivation for the project")

def render_file_info(uploaded_file):
    if uploaded_file:
        st.success("✅ PDF uploaded successfully")
        file_size = uploaded_file.size / 1024
        st.caption(f"File size: {file_size:.1f} KB")

def render_metrics_display(metrics):
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Technical Depth</div>
            <div class="metric-value">{metrics.get('technical_depth', 20)}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Project Understanding</div>
            <div class="metric-value">{metrics.get('project_understanding', 20)}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Timeline Clarity</div>
            <div class="metric-value">{metrics.get('timeline_clarity', 20)}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Implementation Feasibility</div>
            <div class="metric-value">{metrics.get('implementation_feasibility', 20)}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    overall_score = int((
        metrics.get('technical_depth', 20) + 
        metrics.get('project_understanding', 20) + 
        metrics.get('timeline_clarity', 20) + 
        metrics.get('innovation_score', 20) + 
        metrics.get('implementation_feasibility', 20)
    ) / 5)
    
    score_class = "high-score" if overall_score >= 70 else "medium-score" if overall_score >= 50 else "low-score"
    st.markdown(f"""
    <div class="score-display {score_class}">
        Overall Score: {overall_score}/100
    </div>
    """, unsafe_allow_html=True)
    
    return overall_score

def render_strengths_weaknesses(metrics):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Strengths")
        strengths = metrics.get('strengths', ["No clear strength identified", "No clear strength identified", "No clear strength identified"])
        for strength in strengths:
            st.markdown(f"""
            <div class="key-point">
                <strong>➕</strong> {strength}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Areas for Improvement")
        weaknesses = metrics.get('weaknesses', ["Proposal lacks essential details", "Insufficient addressing of problem statement", "Missing clear implementation plan"])
        for weakness in weaknesses:
            st.markdown(f"""
            <div class="key-point">
                <strong>➖</strong> {weakness}
            </div>
            """, unsafe_allow_html=True)

def render_timeline(timeline):
    st.markdown("### Project Timeline")
    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    for period, task in timeline.items():
        st.markdown(f"""
        <div class="timeline-item">
            <strong>{period}</strong>: {task}
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_detailed_feedback(feedback):
    st.markdown("## Detailed Feedback")
    st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
    st.write(feedback)  
    st.markdown('</div>', unsafe_allow_html=True)

def render_export_options(metrics, timeline, feedback, overall_score):
    st.markdown("## Export Results")
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("Export as Text"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_text = f"""
            GSoC PROPOSAL REVIEW - {timestamp}
            
            OVERALL SCORE: {overall_score}/100
            
            KEY METRICS:
            Technical Depth: {metrics.get('technical_depth', 20)}/100
            Project Understanding: {metrics.get('project_understanding', 20)}/100
            Timeline Clarity: {metrics.get('timeline_clarity', 20)}/100
            Innovation Score: {metrics.get('innovation_score', 20)}/100
            Implementation Feasibility: {metrics.get('implementation_feasibility', 20)}/100
            
            STRENGTHS:
            {chr(10).join(['- ' + s for s in metrics.get('strengths', ["No clear strength identified"])])}
            
            AREAS FOR IMPROVEMENT:
            {chr(10).join(['- ' + w for w in metrics.get('weaknesses', ["Proposal lacks essential details"])])}
            
            PROJECT TIMELINE:
            {chr(10).join([f'- {k}: {v}' for k, v in timeline.items()])}
            
            DETAILED FEEDBACK:
            {feedback}
            """
            
            st.download_button(
                label="Download Text Report", 
                data=export_text,
                file_name=f"proposal_review_{timestamp}.txt",
                mime="text/plain"
            )
    
    with export_col2:
        if st.button("Export as JSON"):
            export_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "overall_score": overall_score,
                "metrics": metrics,
                "timeline": timeline,
                "feedback": feedback
            }
            
            st.download_button(
                label="Download JSON Data",
                data=json.dumps(export_data, indent=2),
                file_name=f"proposal_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def render_about_section():
    st.header("Writing Effective GSoC Proposals")
    st.markdown("""
    ### Key Components of a Strong GSoC Proposal
    
    1. **Project Understanding**: Demonstrate that you understand the project and its goals.
    
    2. **Implementation Plan**: Provide a detailed plan for how you will implement the project.
    
    3. **Timeline**: Include a realistic timeline with milestones and deliverables.
    
    4. **Technical Skills**: Highlight your relevant technical skills and experience.
    
    5. **Motivation**: Explain why you're interested in this project and organization.
    
    6. **Communication**: Show that you can communicate clearly and effectively.
    
    ### Common Pitfalls to Avoid
    
    - Vague or generic proposals
    - Unrealistic timelines
    - Lack of technical details
    - Poor organization or formatting
    - Not addressing project requirements
    """)

def render_footer():
    st.markdown("---")
    st.caption("GSoC Proposal Reviewer • Made with <3 @ MostlyK")
