import streamlit as st
import json
from datetime import datetime
from google import genai
from google.genai.types import GenerateContentConfig, Part

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

def analyze_proposal_metrics(client, pdf_file, problem_statement):
    default_metrics = {
        "technical_depth": 20,
        "project_understanding": 20,
        "timeline_clarity": 20,
        "innovation_score": 20,
        "implementation_feasibility": 20,
        "strengths": ["No clear strength identified", "No clear strength identified", "No clear strength identified"],
        "weaknesses": ["Proposal lacks essential details", "Insufficient addressing of problem statement", "Missing clear implementation plan"]
    }
    
    system_prompt = """You are a fair but demanding GSoC proposal analyzer with high standards. Your task is to evaluate if a proposal addresses the given problem statement.
    
    Follow these balanced evaluation principles:
    - Be extremely critical when essential components are missing (scoring below 20)
    - Be moderate when content is present but underdeveloped (scoring 30-60)
    - Be generous when you find well-developed, specific content (scoring 70-100)
    - Never invent strengths that aren't in the text, but genuinely recognize good points when present
    - If the proposal doesn't address the problem statement, be harshly critical on project understanding
    - If proposal directly and excellently addresses the problem statement, acknowledge this with appropriate scores
    
    Your evaluation must be data-driven, based only on what's explicitly in the document."""
    
    user_prompt = f"""
    Problem Statement: {problem_statement}
    
    Extract the following metrics as a valid JSON object:

    1. "technical_depth" (1-100): Score based on technical implementation details
       - Below 30 if technical details are vague/missing
       - 30-60 if some technical approach is outlined but lacks depth
       - 60-80 if technical implementation is clear but could be more detailed
       - 80-100 if technical implementation is comprehensive and well-reasoned
    
    2. "project_understanding" (1-100): Score based on alignment with problem statement
       - Below 20 if proposal doesn't address the specific problem statement
       - 20-50 if proposal partially addresses the problem statement
       - 50-80 if proposal shows good understanding of problem statement
       - 80-100 if proposal demonstrates exceptional understanding
    
    3. "timeline_clarity" (1-100): Score based on project schedule
       - Below 30 if no clear timeline is provided
       - 30-60 if timeline exists but lacks specific milestones
       - 60-80 if timeline has clear milestones but could be more detailed
       - 80-100 if timeline is comprehensive with clear deliverables
    
    4. "innovation_score" (1-100): Score based on originality of approach
       - Below 40 if approach is standard with no novel elements
       - 40-70 if approach has some innovative elements
       - 70-100 if approach is highly innovative and creative
    
    5. "implementation_feasibility" (1-100): Score based on realistic implementation
       - Below 40 if implementation seems unrealistic or vague
       - 40-70 if implementation seems feasible but with some concerns
       - 70-100 if implementation plan is realistic and well-considered
    
    6. "strengths" (list of 3 strings): Identify genuine strengths in the proposal
       - If you cannot find 3 genuine strengths, use "No clear strength identified"
       - Be generous in recognizing actual strengths when they exist
    
    7. "weaknesses" (list of 3 strings): Identify specific areas for improvement
       - Be specific about what's missing or problematic
       - Include actionable suggestions when possible
    
    CRITICAL INSTRUCTIONS:
    - Your most important task is to check if the proposal DIRECTLY addresses the specific problem statement provided
    - If proposal doesn't match the problem statement, project_understanding MUST be below 20
    - For all categories, be precise about your reasoning but never explain in the JSON
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
        pdf_part = Part.from_bytes(data=pdf_file.getvalue(), mime_type="application/pdf")
        
        chat = client.chats.create(
            model="gemini-2.0-flash",
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2
            )
        )
        response = chat.send_message([pdf_part, user_prompt])
        
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

def get_ai_review(client, pdf_file, problem_statement, reviewer_mode=False):
    system_prompt = """You are a balanced GSoC proposal evaluator with high standards. Your task is to provide constructive feedback that is:
    
    - Extremely critical and direct when fundamental elements are missing
    - Fair and measured when elements are present but need improvement
    - Generous and encouraging when you find genuinely good content
    
    Never invent strengths that aren't in the proposal. Be honest but also solution-oriented, offering specific suggestions for improvement.
    For excellent proposals, recognize and validate the quality. For weak proposals, be direct about their shortcomings but provide clear paths to improvement."""
    
    if reviewer_mode:
        user_prompt = f"""
        Problem Statement: {problem_statement}
        
        As a GSoC project mentor/reviewer, provide a balanced evaluation of this proposal:
        1. Overall assessment - begin by stating whether the proposal directly addresses the problem statement
        2. Technical feasibility analysis - evaluate technical claims with appropriate skepticism
        3. Timeline and deliverables evaluation - assess if it's realistic and sufficiently detailed
        4. Specific improvement suggestions with actionable steps
        5. An estimated score out of 100
        
        EVALUATION GUIDELINES:
        - Be extremely critical if the proposal doesn't address the specific problem statement (score below 40)
        - Be direct but fair if technical details are insufficient (score 40-60 depending on severity)
        - Be encouraging if the proposal shows promise but needs refinement (score 60-80)
        - Be generous with praise if the proposal is excellent (score 80-100)
        - Always include specific, actionable recommendations for improvement
        - Never assume information that isn't in the proposal
        
        Format your response with clear headings and concise bullet points.
        Always start with the most important feedback about problem statement alignment first.
        """
    else:
        user_prompt = f"""
        Problem Statement: {problem_statement}
        
        Provide constructive feedback on this GSoC proposal:
        1. First, evaluate if your proposal directly addresses the problem statement
        2. Identify both strengths and areas needing improvement
        3. Provide specific, actionable suggestions to strengthen the proposal
        4. Comment on technical feasibility and timeline with specific recommendations
        5. An estimated score out of 100
        
        FEEDBACK GUIDELINES:
        - Be extremely direct if the proposal doesn't address the problem statement (this is the most critical issue)
        - Be specific about areas that need improvement, but also acknowledge what works well
        - Provide clear, actionable suggestions that would significantly improve the proposal
        - Don't assume information that isn't in the proposal
        - Score below 40 if the proposal doesn't match the problem statement
        - Score 40-60 if the proposal has significant issues but some promise
        - Score 60-80 if the proposal is good but needs refinement
        - Score 80-100 if the proposal is excellent with minor improvements needed
        
        Be honest but constructive. Your goal is to help create a stronger proposal.
        """
    
    try:
        pdf_part = Part.from_bytes(data=pdf_file.getvalue(), mime_type="application/pdf")
        
        chat = client.chats.create(
            model="gemini-2.0-flash",
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2
            )
        )
        response = chat.send_message([pdf_part, user_prompt])
        return response.text
    except Exception as e:
        st.error(f"Error generating AI review: {str(e)}")
        return "Failed to generate review. Please check your API key and try again."

def extract_project_timeline(client, pdf_file):
    system_prompt = """You are a GSoC timeline analyzer who looks for explicitly mentioned project schedules or timelines.
    
    Your evaluation approach:
    - Be strict about verifying that actual timelines exist in the document
    - Don't invent timelines that aren't present
    - Be flexible in recognizing different timeline formats (tables, lists, paragraphs)
    - Extract what's actually in the proposal, not what should be there
    
    A valid timeline must have specific time periods (dates, weeks, months) with corresponding activities or deliverables."""
    
    user_prompt = """
    From the following GSoC proposal, extract the project timeline or schedule.
    Format as JSON with keys as milestone dates/weeks and values as the task descriptions.
    
    INSTRUCTIONS:
    - Look for any explicitly defined timeline, schedule, or work plan
    - If a clear timeline exists, extract it accurately with time periods as keys
    - Consider various formats (tables, lists, phases, etc.)
    - If no explicit timeline exists, return this exact JSON:
      {
        "No Timeline": "The proposal does not contain a clear timeline or schedule."
      }
    - If timeline is vaguely mentioned without specific periods and tasks, also return "No Timeline"
    
    A valid timeline must have specific time periods with corresponding tasks or deliverables.
    """
    
    try:
        pdf_part = Part.from_bytes(data=pdf_file.getvalue(), mime_type="application/pdf")
        
        chat = client.chats.create(
            model="gemini-2.0-flash", 
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1
            )
        )
        response = chat.send_message([pdf_part, user_prompt])
        
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
            
            if uploaded_file:
                progress_bar = st.progress(0)
                
                progress_bar.progress(20)
                metrics = analyze_proposal_metrics(client, uploaded_file, problem_statement)
                
                progress_bar.progress(40)
                timeline = extract_project_timeline(client, uploaded_file)
                
                progress_bar.progress(70)
                feedback = get_ai_review(client, uploaded_file, problem_statement, reviewer_mode)
                
                progress_bar.progress(100)
                progress_bar.empty()
                
                st.session_state.metrics = metrics
                st.session_state.timeline = timeline
                st.session_state.feedback = feedback
                st.session_state.has_feedback = True
            else:
                st.error("Could not process the PDF. Please try again with a different file.")

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
