import streamlit as st
import os
import tempfile
import PyPDF2
from google import genai
from google.genai.types import GenerateContentConfig
import json
from datetime import datetime

st.set_page_config(
    page_title="GSoC Proposal Reviewer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #121212;
        color: #e0e0e0;
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .feedback-box {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-top: 20px;
        color: #e0e0e0;
    }
    .score-display {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .high-score {
        background-color: #1e4620;
        color: #4caf50;
    }
    .medium-score {
        background-color: #332d15;
        color: #ffeb3b;
    }
    .low-score {
        background-color: #391c1c;
        color: #f44336;
    }
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .logo-text {
        font-size: 2.5rem;
        font-weight: bold;
        margin-right: 10px;
        color: #e0e0e0;
    }
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin: 20px 0;
    }
    .metric-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        text-align: center;
    }
    .metric-title {
        font-size: 16px;
        color: #bdbdbd;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #e0e0e0;
    }
    .timeline {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .timeline-item {
        padding: 10px;
        border-left: 2px solid #4caf50;
        margin-left: 20px;
        margin-bottom: 10px;
        position: relative;
        color: #e0e0e0;
    }
    .timeline-item::before {
        content: "";
        position: absolute;
        width: 12px;
        height: 12px;
        background-color: #4caf50;
        border-radius: 50%;
        left: -7px;
        top: 15px;
    }
    .key-points {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin-top: 20px;
    }
    .key-point {
        background-color: #1e2f1e;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #4caf50;
        color: #e0e0e0;
        margin-bottom: 10px;
    }
    .feedback-section {
        margin: 15px 0;
    }
    .feedback-header {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #e0e0e0;
    }
    .tag {
        display: inline-block;
        background-color: #333333;
        color: #e0e0e0;
        padding: 5px 10px;
        border-radius: 15px;
        margin-right: 5px;
        margin-bottom: 5px;
        font-size: 14px;
    }
    .positive-tag {
        background-color: #1e4620;
        color: #4caf50;
    }
    .negative-tag {
        background-color: #391c1c;
        color: #f44336;
    }
    .neutral-tag {
        background-color: #332d15;
        color: #ffeb3b;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e1e1e;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #333333;
    }
    .stTextInput > div > div > input {
        background-color: #333333;
        color: #e0e0e0;
    }
    .stTextArea > div > div > textarea {
        background-color: #333333;
        color: #e0e0e0;
    }
    .css-1n543e5 {
        background-color: #1e293b;
        color: #e0e0e0;
    }
    .uploadedFile {
        background-color: #333333 !important;
    }
    .css-16huue1 {
        color: #e0e0e0 !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_genai():
    return genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

def extract_text_from_pdf(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp:
        temp.write(pdf_file.getvalue())
        temp_path = temp.name
    
    try:
        reader = PyPDF2.PdfReader(temp_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""
    finally:
        os.unlink(temp_path)

def analyze_proposal_metrics(client, text, problem_statement):
    default_metrics = {
        "technical_depth": 20,
        "project_understanding": 20,
        "timeline_clarity": 20,
        "innovation_score": 20,
        "implementation_feasibility": 20,
        "strengths": ["No clear strength identified", "No clear strength identified", "No clear strength identified"],
        "weaknesses": ["Proposal lacks essential details", "Insufficient addressing of problem statement", "Missing clear implementation plan"]
    }
    
    system_prompt = """You are an extremely critical GSoC proposal analyzer with very high standards. Your task is to strictly evaluate if a proposal addresses the given problem statement.
    Do not be generous. Only extract information that is EXPLICITLY present in the proposal text. 
    If information is missing or vague, assign very low scores (below 20). 
    If the proposal doesn't clearly address the specific problem statement, assign a project understanding score below 20.
    Be ruthlessly factual. If you can't find genuine strengths, don't invent them - state "No clear strength identified" instead.
    You must be difficult to impress and skeptical by default."""
    
    user_prompt = f"""
    Problem Statement: {problem_statement}
    
    Proposal: {text[:4000]}
    
    Extract the following metrics as a valid JSON object:

    1. "technical_depth" (1-100): Must be below 40 if technical implementation details are vague or missing
    2. "project_understanding" (1-100): Must be below 20 if the proposal doesn't directly address the provided problem statement
    3. "timeline_clarity" (1-100): Must be below 30 if no explicit timeline with milestones is provided
    4. "innovation_score" (1-100): Must be below 40 if approach is standard with no novel elements
    5. "implementation_feasibility" (1-100): Must be below 40 if implementation approach is vague or unrealistic
    6. "strengths" (list of 3 strings): If you cannot find 3 genuine strengths, use "No clear strength identified" 
    7. "weaknesses" (list of 3 strings): Be specific about what's missing or problematic
    
    CRITICAL INSTRUCTIONS:
    - Your most important task is to check if the proposal DIRECTLY addresses the specific problem statement provided
    - If the proposal is generic or doesn't match the problem statement, project_understanding MUST be below 20
    - If ANY critical information is missing, assign scores below 20 for relevant categories
    - Do NOT invent information or strengths that aren't explicitly stated in the proposal
    - Use EXACTLY the key names shown above in your JSON response
    - Return ONLY valid JSON, no explanation text
    
    Format:
    {{
      "technical_depth": number,
      "project_understanding": number,
      "timeline_clarity": number,
      "innovation_score": number,
      "implementation_feasibility": number,
      "strengths": [string, string, string],
      "weaknesses": [string, string, string]
    }}
    """
    
    try:
        chat = client.chats.create(
            model="gemini-2.0-flash",
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.01
            )
        )
        response = chat.send_message(user_prompt)
        
        try:
            json_str = response.text
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            metrics = json.loads(json_str)
            
            expected_keys = ["technical_depth", "project_understanding", "timeline_clarity", 
                            "innovation_score", "implementation_feasibility", "strengths", "weaknesses"]
            
            for key in expected_keys:
                if key not in metrics:
                    metrics[key] = default_metrics[key]
                    
            return metrics
            
        except json.JSONDecodeError as e:
            st.error(f"Error parsing metrics JSON: {str(e)}")
            return default_metrics
    except Exception as e:
        st.error(f"Error analyzing proposal: {str(e)}")
        return default_metrics

def get_ai_review(client, proposal_text, problem_statement, reviewer_mode=False):
    system_prompt = """You are an exceptionally critical GSoC proposal evaluator with extremely high standards. You are skeptical by default and difficult to impress.
    Your task is to evaluate how well proposals address the specific problem statement. Be direct and honest - never invent strengths that aren't explicitly present.
    If information is missing or vague, call it out harshly. Give brutally honest criticism. Set an extremely high bar for what makes a good proposal."""
    
    if reviewer_mode:
        user_prompt = f"""
        Problem Statement: {problem_statement}
        
        Proposal: {proposal_text}
        
        As a GSoC project mentor/reviewer, provide a critical evaluation of this proposal:
        1. Overall assessment - begin by stating whether the proposal directly addresses the problem statement
        2. Technical feasibility analysis - be skeptical of vague technical claims
        3. Timeline and deliverables evaluation - identify if it's realistic and detailed
        4. Specific improvement suggestions
        5. An estimated score out of 100
        
        CRITICAL EVALUATION GUIDELINES:
        - Check if the proposal SPECIFICALLY addresses the exact problem statement provided - this is the most critical factor
        - If the proposal doesn't directly match the problem statement, this must be your primary criticism
        - If the proposal lacks specific information (timeline, technical details, etc.), harshly criticize this
        - Do not assume or invent information that isn't explicitly in the proposal
        - Score below 40 if the proposal doesn't clearly match the problem statement
        - Score below 30 if important technical details are missing
        - Be specific about what's missing and what needs improvement
        - Be extremely strict about evaluating project understanding - it must specifically address the provided problem statement
        
        Format your response with clear headings and concise bullet points.
        """
    else:
        user_prompt = f"""
        Problem Statement: {problem_statement}
        
        Proposal: {proposal_text}
        
        Provide critical feedback for the student on this GSoC proposal:
        1. Honestly evaluate if your proposal directly addresses the problem statement
        2. Identify areas that need significant improvement
        3. Provide specific suggestions to make the proposal competitive
        4. Comment on technical feasibility and timeline
        5. An estimated score out of 100
        
        CRITICAL GUIDELINES:
        - Be direct about whether the proposal specifically addresses the provided problem statement
        - If the proposal doesn't match the problem statement, emphasize this as the critical issue to fix
        - If the proposal lacks specific information (timeline, technical details, etc.), be direct about this
        - Do not assume or invent information that isn't explicitly in the proposal
        - Score below 40 if the proposal doesn't clearly match the problem statement
        - Be specific about what's missing and what needs improvement
        - Be extremely strict about evaluating project understanding - it must specifically address the provided problem statement
        
        Be constructive but brutally honest about the proposal's weaknesses.
        """
    
    try:
        chat = client.chats.create(
            model="gemini-2.0-flash",
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.01
            )
        )
        response = chat.send_message(user_prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating AI review: {str(e)}")
        return "Failed to generate review. Please check your API key and try again."

def extract_project_timeline(client, proposal_text):
    system_prompt = """You are a GSoC timeline analyzer with strict criteria. Extract ONLY timelines that are explicitly and clearly mentioned.
    Do not be generous or create timelines from vague mentions. If no clear timeline with specific milestones exists, state this fact.
    Never invent or assume timelines that aren't explicitly presented in the document."""
    
    user_prompt = f"""
    From the following GSoC proposal, extract ONLY a clearly defined project timeline or schedule.
    Format as JSON with keys as milestone dates/weeks and values as the task descriptions.
    
    Proposal: {proposal_text[:5000]}
    
    CRITICAL INSTRUCTION: If no explicit, structured timeline is present in the proposal, return this exact JSON:
    {{
      "No Timeline": "The proposal does not contain a clear timeline or schedule."
    }}
    
    Do not extract a timeline if it's only vaguely mentioned. There must be specific time periods and corresponding activities.
    """
    
    try:
        chat = client.chats.create(
            model="gemini-2.0-flash", 
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.01
            )
        )
        response = chat.send_message(user_prompt)
        
        try:
            json_str = response.text
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            timeline = json.loads(json_str)
            return timeline
        except json.JSONDecodeError:
            return {"No Timeline": "The proposal does not contain a clear timeline or schedule."}
    except Exception as e:
        st.error(f"Error extracting timeline: {str(e)}")
        return {"Error": "Failed to extract timeline"}

st.markdown("""
<div class="header-container">
    <div>
        <span class="logo-text">📝 GSoC Proposal Reviewer</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Submit Proposal", "About GSoC Proposals"])

with tab1:
    col1, col2 = st.columns([3, 2])
    
    with col1:
        uploaded_file = st.file_uploader("Upload your GSoC proposal (PDF)", type="pdf")
        problem_statement = st.text_area("Enter the project/problem statement", height=150)
        reviewer_mode = st.checkbox("I am a project mentor/reviewer")
        
        submit_button = st.button("Generate Feedback", type="primary", disabled=not uploaded_file)
    
    with col2:
        st.info("### Tips for Good Proposals\n"
                "- Clearly define the problem\n"
                "- Provide a detailed implementation plan\n"
                "- Include a realistic timeline\n"
                "- Demonstrate your technical capabilities\n"
                "- Explain your motivation for the project")
        
        if uploaded_file:
            st.success("✅ PDF uploaded successfully")
            file_size = uploaded_file.size / 1024
            st.caption(f"File size: {file_size:.1f} KB")

    if submit_button and uploaded_file:
        with st.spinner("Analyzing your proposal..."):
            client = initialize_genai()
            
            proposal_text = extract_text_from_pdf(uploaded_file)
            
            if proposal_text:
                progress_bar = st.progress(0)
                
                progress_bar.progress(20)
                metrics = analyze_proposal_metrics(client, proposal_text, problem_statement)
                
                progress_bar.progress(40)
                timeline = extract_project_timeline(client, proposal_text)
                
                progress_bar.progress(70)
                feedback = get_ai_review(client, proposal_text, problem_statement, reviewer_mode)
                
                progress_bar.progress(100)
                progress_bar.empty()
                
                st.session_state.metrics = metrics
                st.session_state.timeline = timeline
                st.session_state.feedback = feedback
                st.session_state.has_feedback = True
            else:
                st.error("Could not extract text from the PDF. Please try again with a different file.")

    if 'has_feedback' in st.session_state and st.session_state.has_feedback:
        st.markdown("## Proposal Analysis")
        
        st.markdown("### Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Technical Depth</div>
                <div class="metric-value">{st.session_state.metrics.get('technical_depth', 20)}/100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Project Understanding</div>
                <div class="metric-value">{st.session_state.metrics.get('project_understanding', 20)}/100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Timeline Clarity</div>
                <div class="metric-value">{st.session_state.metrics.get('timeline_clarity', 20)}/100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Implementation Feasibility</div>
                <div class="metric-value">{st.session_state.metrics.get('implementation_feasibility', 20)}/100</div>
            </div>
            """, unsafe_allow_html=True)
        
        overall_score = int((
            st.session_state.metrics.get('technical_depth', 20) + 
            st.session_state.metrics.get('project_understanding', 20) + 
            st.session_state.metrics.get('timeline_clarity', 20) + 
            st.session_state.metrics.get('innovation_score', 20) + 
            st.session_state.metrics.get('implementation_feasibility', 20)
        ) / 5)
        
        score_class = "high-score" if overall_score >= 70 else "medium-score" if overall_score >= 50 else "low-score"
        st.markdown(f"""
        <div class="score-display {score_class}">
            Overall Score: {overall_score}/100
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Strengths")
            strengths = st.session_state.metrics.get('strengths', ["No clear strength identified", "No clear strength identified", "No clear strength identified"])
            for strength in strengths:
                st.markdown(f"""
                <div class="key-point">
                    <strong>➕</strong> {strength}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Areas for Improvement")
            weaknesses = st.session_state.metrics.get('weaknesses', ["Proposal lacks essential details", "Insufficient addressing of problem statement", "Missing clear implementation plan"])
            for weakness in weaknesses:
                st.markdown(f"""
                <div class="key-point">
                    <strong>➖</strong> {weakness}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("### Project Timeline")
        st.markdown('<div class="timeline">', unsafe_allow_html=True)
        for period, task in st.session_state.timeline.items():
            st.markdown(f"""
            <div class="timeline-item">
                <strong>{period}</strong>: {task}
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("## Detailed Feedback")
        st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
        st.write(st.session_state.feedback)  
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("## Export Results")
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.button("Export as Text"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_text = f"""
                GSoC PROPOSAL REVIEW - {timestamp}
                
                OVERALL SCORE: {overall_score}/100
                
                KEY METRICS:
                Technical Depth: {st.session_state.metrics.get('technical_depth', 20)}/100
                Project Understanding: {st.session_state.metrics.get('project_understanding', 20)}/100
                Timeline Clarity: {st.session_state.metrics.get('timeline_clarity', 20)}/100
                Innovation Score: {st.session_state.metrics.get('innovation_score', 20)}/100
                Implementation Feasibility: {st.session_state.metrics.get('implementation_feasibility', 20)}/100
                
                STRENGTHS:
                {chr(10).join(['- ' + s for s in st.session_state.metrics.get('strengths', ["No clear strength identified"])])}
                
                AREAS FOR IMPROVEMENT:
                {chr(10).join(['- ' + w for w in st.session_state.metrics.get('weaknesses', ["Proposal lacks essential details"])])}
                
                PROJECT TIMELINE:
                {chr(10).join([f'- {k}: {v}' for k, v in st.session_state.timeline.items()])}
                
                DETAILED FEEDBACK:
                {st.session_state.feedback}
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
                    "metrics": st.session_state.metrics,
                    "timeline": st.session_state.timeline,
                    "feedback": st.session_state.feedback
                }
                
                st.download_button(
                    label="Download JSON Data",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"proposal_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

with tab2:
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

st.markdown("---")
st.caption("GSoC Proposal Reviewer • Made with <3 @ MostlyK")
