# virtaul activation code for VS code (.\venv\Scripts\activate)
# RGBOUC Framework: Role, Goal, Background, Output, Constraints
# Use case: General-Purpose LLM-based ATS (Applicant Tracking System)
# Interface: Simple Gradio UI for copy-paste testing

from openai import OpenAI
import os
from dotenv import load_dotenv
import gradio as gr

load_dotenv()
client = OpenAI()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')

def get_completion(prompt, model="gpt-4o-mini"):
    """Get completion from OpenAI API"""
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0  # Max consistency for scoring
    )
    return response.choices[0].message.content

def evaluate_resume(job_description, resume_text):
    """
    Evaluate a single resume against job description using RGBOUC framework
    """
    
    if not job_description.strip():
        return "⚠️ Please paste a Job Description first."
    
    if not resume_text.strip():
        return "⚠️ Please paste a Resume to evaluate."
    
    # RGBOUC Prompt Structure
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

Evaluate this candidate now.
"""
    
    try:
        result = get_completion(prompt)
        return result
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease check your OpenAI API key and connection."


# ============================================================================
# GRADIO INTERFACE - Simple Copy/Paste Design
# ============================================================================

with gr.Blocks(title="ATS - Resume Evaluator") as demo:
    
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
                label=""
            )
        
        # Right Column: Resume Input
        with gr.Column(scale=1):
            gr.Markdown("### 📄 Candidate Resume")
            resume_input = gr.Textbox(
                placeholder="Paste the candidate's resume here...\n\nInclude:\n- Work experience\n- Skills\n- Education\n- Projects/Achievements\n...",
                lines=18,
                max_lines=25,
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
        label="",
        interactive=False
    )
    
    # Connect button to function
    evaluate_btn.click(
        fn=evaluate_resume,
        inputs=[job_desc_input, resume_input],
        outputs=output
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
        
        ### 🧠 Powered by RGBOUC Framework:
        **R**ole • **G**oal • **B**ackground • **O**utput • **C**onstraints  
        This prompt structure ensures consistent, intelligent evaluations across all job types.
        """
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(
        share=False,  # Set True for public link
        server_name="127.0.0.1",
        server_port=7860
    )
