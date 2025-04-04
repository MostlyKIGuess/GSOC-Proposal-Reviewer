import streamlit as st
import json
from google import genai
from google.genai.types import GenerateContentConfig, Part

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
            
        except json.JSONDecodeError as e:
            st.error(f"Error parsing timeline JSON: {str(e)}")
            return {"No Timeline": "Failed to parse timeline data from the proposal."}
    except Exception as e:
        st.error(f"Error extracting timeline: {str(e)}")
        return {"No Timeline": "Failed to extract timeline from the proposal."}
