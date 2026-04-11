# virtaul activation code for VS code (.\venv\Scripts\activate)
# RGBOUC Framework: Role, Goal, Background, Output, Constraints
# Use case: General-Purpose LLM-based ATS (Applicant Tracking System)
# Interface: Simple Gradio UI for copy-paste testing
# Features: Saves evaluation results to Excel for record-keeping

from openai import OpenAI
import os
from dotenv import load_dotenv
import gradio as gr
import json
import pandas as pd
from datetime import datetime

load_dotenv()
client = OpenAI()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')

# Excel file path for storing evaluation records
EXCEL_FILE = "ats_evaluation_records.xlsx"

def get_completion(prompt, model="gpt-4o-mini"):
    """Get completion from OpenAI API"""
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0  # Max consistency for scoring
    )
    return response.choices[0].message.content

def save_to_excel(evaluation_data):
    """
    Save evaluation record to Excel file
    Creates new file if doesn't exist, appends if exists
    """
    try:
        # Check if file exists
        if os.path.exists(EXCEL_FILE):
            # Read existing data
            df_existing = pd.read_excel(EXCEL_FILE)
            # Append new record
            df_new = pd.DataFrame([evaluation_data])
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            # Create new DataFrame
            df_combined = pd.DataFrame([evaluation_data])
        
        # Save to Excel
        df_combined.to_excel(EXCEL_FILE, index=False)
        return True, f"✅ Saved to {EXCEL_FILE}"
    except Exception as e:
        return False, f"⚠️ Could not save to Excel: {str(e)}"

def extract_json_from_text(text):
    """
    Extract JSON data from text that may contain other content
    """
    try:
        # Try to find JSON block in the text
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_str = text[start_idx:end_idx+1]
            return json.loads(json_str)
        return None
    except:
        return None

def evaluate_resume(job_description, resume_text):
    """
    Evaluate a single resume against job description using RGBOUC framework
    Returns both human-readable report and saves structured data to Excel
    """
    
    if not job_description.strip():
        return "⚠️ Please paste a Job Description first.", ""
    
    if not resume_text.strip():
        return "⚠️ Please paste a Resume to evaluate.", ""
    
    # RGBOUC Prompt Structure - Modified to include JSON output
    prompt = f"""
**ROLE:**
You are an expert HR recruitment specialist with 10+ years of experience evaluating candidates 
across various industries (technology, finance, healthcare, operations, sales, etc.).

**GOAL:**
Evaluate how well the candidate's resume matches the job description. Provide an objective score, 
identify strengths and gaps, and give a clear hiring recommendation.

**BACKGROUND/CONTEXT:**
This is a general-purpose ATS system. You must:
- Extract key requirements from the job description
- Evaluate candidate's relevant skills, experience, and qualifications
- Be completely objective - ignore name, gender, age, university brand, or formatting
- Focus purely on job-relevant capabilities and achievements
- Understand industry context (tech values projects, finance values certifications, etc.)

**OUTPUT FORMAT:**
First, provide a human-readable report, then provide structured JSON data.

HUMAN-READABLE REPORT:
```
═══════════════════════════════════════════════════════════════
                    CANDIDATE EVALUATION REPORT
═══════════════════════════════════════════════════════════════

OVERALL MATCH SCORE: [X/100]

SCORE BREAKDOWN:
├─ Required Skills Match: [X/40]
├─ Experience Relevance: [X/30]
├─ Education & Certifications: [X/15]
└─ Achievements & Impact: [X/15]

───────────────────────────────────────────────────────────────
✅ KEY STRENGTHS:
1. [Specific strength with evidence from resume]
2. [Specific strength with evidence from resume]
3. [Specific strength with evidence from resume]

───────────────────────────────────────────────────────────────
⚠️ GAPS / MISSING REQUIREMENTS:
1. [Gap description - Severity: CRITICAL/MEDIUM/MINOR]
2. [Gap description]

(Write "No significant gaps identified" if none found)

───────────────────────────────────────────────────────────────
📋 RECOMMENDATION: [STRONG YES / YES / MAYBE / NO]

💭 RATIONALE:
[2-3 sentences explaining the recommendation based on match score and analysis]

───────────────────────────────────────────────────────────────
🎯 SUGGESTED INTERVIEW FOCUS AREAS:
1. [Topic to explore in interview]
2. [Topic to explore in interview]
3. [Topic to explore in interview]
```

STRUCTURED JSON DATA (for database):
{{
  "job_title": "extracted from JD",
  "candidate_name": "extracted from resume if present, else 'Not specified'",
  "overall_score": 85,
  "skills_score": 38,
  "experience_score": 28,
  "education_score": 14,
  "achievements_score": 13,
  "recommendation": "STRONG YES",
  "top_strength": "brief summary of #1 strength",
  "main_gap": "brief summary of main gap or 'None'",
  "years_experience": "X years or 'Not specified'"
}}

**CONSTRAINTS:**
1. Scoring Rules:
   - Required Skills (40 pts): Award points based on % of must-have skills present
   - Experience (30 pts): Years + relevance of past roles to job requirements
   - Education (15 pts): Degree + relevant certifications matching JD
   - Achievements (15 pts): Quantified results, impact metrics, leadership examples

2. Recommendation Thresholds:
   - STRONG YES (85-100): Exceptional fit, exceeds requirements
   - YES (70-84): Good fit, meets all key requirements
   - MAYBE (55-69): Partial fit, missing some requirements but shows potential
   - NO (<55): Poor fit, significant gaps in critical areas

3. Fairness Guidelines:
   - DO NOT consider: Name, gender, age, ethnicity, university prestige
   - DO consider: Skills, experience, achievements, role-specific qualifications
   - Treat career gaps neutrally unless clearly problematic for role

4. Automatic Disqualifiers (override score):
   - Completely lacks all must-have skills marked as "required"
   - Clear evidence of dishonesty or credential fabrication

═══════════════════════════════════════════════════════════════

JOB DESCRIPTION:
{job_description}

═══════════════════════════════════════════════════════════════

CANDIDATE RESUME:
{resume_text}

═══════════════════════════════════════════════════════════════

Evaluate this candidate now. Provide BOTH the human-readable report AND the JSON data.
"""
    
    try:
        result = get_completion(prompt)
        
        # Extract JSON from response
        json_data = extract_json_from_text(result)
        
        # Prepare Excel record
        if json_data:
            excel_record = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Job Title": json_data.get("job_title", "Not specified"),
                "Candidate Name": json_data.get("candidate_name", "Not specified"),
                "Overall Score": json_data.get("overall_score", 0),
                "Skills Score": json_data.get("skills_score", 0),
                "Experience Score": json_data.get("experience_score", 0),
                "Education Score": json_data.get("education_score", 0),
                "Achievements Score": json_data.get("achievements_score", 0),
                "Recommendation": json_data.get("recommendation", "N/A"),
                "Years Experience": json_data.get("years_experience", "Not specified"),
                "Top Strength": json_data.get("top_strength", "N/A"),
                "Main Gap": json_data.get("main_gap", "None")
            }
            
            # Save to Excel
            success, message = save_to_excel(excel_record)
            status_message = f"\n\n{'═'*65}\n{message}\n{'═'*65}"
        else:
            status_message = "\n\n⚠️ Could not extract structured data for Excel (evaluation still valid)"
        
        return result, status_message
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease check your OpenAI API key and connection.", ""


# ============================================================================
# GRADIO INTERFACE - Simple Copy/Paste Design
# ============================================================================

with gr.Blocks(title="ATS - Resume Evaluator", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown(
        """
        # 🎯 AI-Powered Resume Evaluator
        ### Copy-paste any Job Description and Resume to get instant AI evaluation
        
        **How to use:**
        1. Copy a job description from anywhere → Paste in left box
        2. Copy a resume/CV → Paste in right box
        3. Click "Evaluate" to get AI analysis with scoring
        """
    )
    
    with gr.Row():
        # Left Column: Job Description Input
        with gr.Column(scale=1):
            gr.Markdown("### 📋 Job Description")
            job_desc_input = gr.Textbox(
                placeholder="Paste the job description here...\n\nExample:\nJob Title: Software Engineer\nRequirements:\n- 5+ years Python\n- Django/Flask\n- AWS experience\n...",
                lines=18,
                max_lines=25,
                show_copy_button=True,
                label=""
            )
        
        # Right Column: Resume Input
        with gr.Column(scale=1):
            gr.Markdown("### 📄 Candidate Resume")
            resume_input = gr.Textbox(
                placeholder="Paste the candidate's resume here...\n\nInclude:\n- Work experience\n- Skills\n- Education\n- Projects/Achievements\n...",
                lines=18,
                max_lines=25,
                show_copy_button=True,
                label=""
            )
    
    # Evaluate Button (centered, prominent)
    with gr.Row():
        evaluate_btn = gr.Button(
            "🚀 Evaluate Resume", 
            variant="primary", 
            size="lg",
            scale=1
        )
    
    # Output Section
    gr.Markdown("---")
    gr.Markdown("## 📊 Evaluation Results")
    
    output = gr.Textbox(
        placeholder="AI evaluation will appear here after you click 'Evaluate Resume'...",
        lines=20,
        max_lines=40,
        show_copy_button=True,
        label="",
        interactive=False
    )
    
    # Excel save status
    excel_status = gr.Textbox(
        placeholder="Excel save status will appear here...",
        lines=2,
        label="",
        interactive=False
    )
    
    # Connect button to function
    evaluate_btn.click(
        fn=evaluate_resume,
        inputs=[job_desc_input, resume_input],
        outputs=[output, excel_status]
    )
    
    # Footer with tips
    gr.Markdown(
        """
        ---
        ### 💡 Tips:
        - Works for **any industry**: Tech, Finance, Healthcare, Sales, Operations, etc.
        - The AI adapts automatically to different job types
        - Paste real job posts and resumes for testing
        - Results are objective and unbiased (no name/gender/age consideration)
        - **All evaluations are automatically saved to Excel** (`ats_evaluation_records.xlsx`)
        
        ### 📊 Excel Record Tracking:
        Each evaluation creates a record with:
        - Timestamp, Job Title, Candidate Name
        - All scores (Overall, Skills, Experience, Education, Achievements)
        - Recommendation (Strong Yes/Yes/Maybe/No)
        - Top strength and main gap
        - Years of experience
        
        ### 🧠 Powered by RGBOUC Framework:
        **R**ole • **G**oal • **B**ackground • **O**utput • **C**onstraints  
        This prompt structure ensures consistent, intelligent evaluations across all job types.
        
        ### 📁 View Your Records:
        Open `ats_evaluation_records.xlsx` in the same folder to see evaluation history.
        """
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(
        share=False,  # Set True for public link
        server_name="127.0.0.1",
        server_port=7860
    )
