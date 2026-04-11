
# virtaul activation code for VS code (.\venv\Scripts\activate)
# Principle 2: Give model time to think
# Chain of thought prompting and self-evaluation

# Real-world use case: Automated Customer Call Quality Analysis for Maersk
# 
# Business Value:
# - Analyze 1000+ daily customer service calls automatically
# - Identify high-priority escalations requiring immediate action
# - Track sentiment trends across regions/agents/time periods
# - Reduce manual QA workload by 80%
# - Catch toxic interactions early for coaching opportunities
#
# Without CoT: Model might rush to judgment and misclassify urgency or miss escalation needs
# With CoT: Model reasons through each aspect systematically, producing better analysis

from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()

OpenAI.api_key  = os.getenv('OPENAI_API_KEY')

def get_completion(prompt, model="gpt-4o-mini"):
    messages = [{"role": "user", "content": prompt}]
    response = client.responses.create(
        model=model,
        input=messages,
        temperature=0
    )
    return response.output_text

# ============================================================================
# PART 1: Simple Chain-of-Thought Introduction
# ============================================================================
print("="*70)
print("PART 1: SIMPLE CHAIN-OF-THOUGHT DEMONSTRATION")
print("="*70)

simple_call = """
Agent: Maersk customer service, how can I help?
Customer: My container MAEU123456 is delayed by 5 days!
Agent: Let me check... it's held at customs for documentation review.
Customer: This is completely unacceptable! I need it today!
"""

simple_cot_prompt = f"""
Analyze this customer service call and classify it.

Follow these steps:
1. Identify the customer's main issue
2. Assess the customer's emotional state
3. Determine urgency level (low/medium/high)
4. Decide if escalation is needed

Show your reasoning for each step, then provide final classification.

Call transcript:
{simple_call}

Provide output as:
REASONING:
Step 1 - Issue: [your analysis]
Step 2 - Emotion: [your analysis]
Step 3 - Urgency: [your analysis]
Step 4 - Escalation: [your analysis]

FINAL CLASSIFICATION:
- Issue Type: [complaint/inquiry/request]
- Urgency: [low/medium/high]
- Escalation Needed: [yes/no]
"""

response = get_completion(simple_cot_prompt)
print("\n📋 SIMPLE CALL ANALYSIS (With Chain-of-Thought):")
print(response)
print("\n" + "="*70 + "\n")

# ============================================================================
# PART 2: Enterprise Chain-of-Thought Application
# ============================================================================
print("="*70)
print("PART 2: ENTERPRISE-GRADE CALL ANALYSIS")
print("="*70)

detailed_call_transcript = """\
Agent: Thank you for calling Maersk Logistics, this is Priya. How may I help you today?
Customer: I'm honestly very frustrated! My container was supposed to arrive three days ago, and I still don't have any updates!
Agent: I'm sorry to hear that, sir. Could you provide me the container number so I can check the status?
Customer: It's MAEU7894561. I've been calling every day, and no one gives me a clear answer!
Agent: I understand how frustrating that must be. Let me check your shipment details… yes, I can see the container is currently held at Nhava Sheva port awaiting customs clearance.
Customer: Customs clearance? Why wasn't I informed about this? My production line is stopped because of this delay!
Agent: I apologize for the lack of communication. It appears there was a documentation issue that's causing the delay.
Customer: Documentation issue? We submitted everything correctly! Are you people even checking properly or just making excuses?
Agent: I assure you, sir, we take every case seriously. I can see that our customs team is working to resolve this, but it may take 2-3 more business days.
Customer: 2-3 more days?! That's unacceptable! I'm losing thousands of rupees every day. I need this resolved immediately!
Agent: I completely understand your concern. Unfortunately, customs procedures are beyond our direct control, but I can escalate this to our port operations manager.
Customer: Escalate it then! This is ridiculous. I pay premium rates for your services and this is what I get?
Agent: I will escalate your case right away, sir. Would you like me to transfer you to my supervisor immediately?
Customer: Yes, do it now. I want to speak to someone who can actually help me, not just give me excuses.
Agent: Understood, sir. I'll transfer your call to my supervisor immediately. Please hold.
"""

enterprise_prompt = """
You are analyzing a customer service call transcript. Follow these steps in order to produce a structured JSON report.

IMPORTANT: Include a "reasoning" section showing your step-by-step thought process.

<transcript>
{call_transcript}
</transcript>

## Analysis Steps

**Step 1: Validate Data Sufficiency**
First, determine if the transcript contains enough information for analysis.
Return INSUFFICIENT_DATA if ANY of these conditions are true:
- Fewer than 3 meaningful exchanges between agent and customer
- Customer's issue or intent is completely unclear
- Transcript is severely garbled, incomplete, or has major language barriers

If insufficient, output ONLY:
{{
  "status": "INSUFFICIENT_DATA",
  "reason": "brief explanation of why data is insufficient"
}}

**Step 2: Analyze Sentiment & Tone**
Evaluate the emotional aspects of the interaction:
- Overall sentiment trajectory (positive/neutral/negative/mixed)
- Customer's emotional state throughout the call
- Agent's tone and approach

**Step 3: Classify the Interaction**
Identify:
- Type of interaction (complaint/inquiry/request/feedback/technical_support/other)
- Customer's primary intent
- Key topics or themes discussed
- Urgency and severity levels
- Whether escalation would be beneficial
- Presence of inappropriate language

**Step 4: Summarize Key Information**
Capture:
- The core customer issue
- What resolution or guidance was provided
- Whether follow-up action is needed

## Output Requirements

- **Confidentiality**: Exclude all PII (names, phone numbers, emails, account numbers, addresses)
- **Brevity**: Keep each text field under 100 characters
- **Format**: Return ONLY valid JSON, no markdown code blocks or extra text
- **Tone**: Professional and objective

## JSON Structure (when data is sufficient)

{{
  "reasoning": {{
    "step1_validation": "your validation reasoning here",
    "step2_sentiment_analysis": "your sentiment analysis reasoning here",
    "step3_classification_logic": "your classification reasoning here",
    "step4_summary_basis": "your summary reasoning here"
  }},
  "sentiment": {{
    "overall": "positive|neutral|negative|mixed",
    "customerEmotion": "concise description of customer's emotional state",
    "agentTone": "concise description of agent's approach"
  }},
  "classification": {{
    "interactionType": "complaint|inquiry|request|feedback|technical_support|other",
    "customerIntent": "brief phrase describing what customer wants to achieve",
    "topics": ["topic1", "topic2", "topic3"],
    "urgency": "low|medium|high",
    "severity": "low|medium|high",
    "escalationSuggested": true|false,
    "escalationReason": "why escalation would help, or null if not suggested",
    "toxicLanguage": true|false
  }},
  "summary": {{
    "customerIssue": "concise problem statement",
    "resolution": "what was done to address the issue, or null if unresolved",
    "followUpRequired": true|false,
    "followUpDetails": "specific next steps needed, or null"
  }},
  "status": "COMPLETE",
  "ambiguities": ["list any unclear points or information gaps, empty array if none"]
}}

## Reference Examples

**Example 1 - Resolved Logistics Issue:**
{{
  "reasoning": {{
    "step1_validation": "Transcript has 6+ exchanges, customer issue is clear (tracking inquiry)",
    "step2_sentiment_analysis": "Customer tone starts concerned but becomes satisfied after resolution",
    "step3_classification_logic": "Classified as inquiry because customer seeks information, not complaining about service failure",
    "step4_summary_basis": "Issue: delay notification needed. Resolution: tracking provided with new ETA"
  }},
  "sentiment": {{
    "overall": "neutral",
    "customerEmotion": "initially concerned, then satisfied",
    "agentTone": "helpful and methodical"
  }},
  "classification": {{
    "interactionType": "inquiry",
    "customerIntent": "track delayed shipment",
    "topics": ["tracking", "delay", "port operations"],
    "urgency": "medium",
    "severity": "low",
    "escalationSuggested": false,
    "escalationReason": null,
    "toxicLanguage": false
  }},
  "summary": {{
    "customerIssue": "Container delayed at port, customer needs ETA update",
    "resolution": "Agent provided tracking details and confirmed new ETA",
    "followUpRequired": true,
    "followUpDetails": "Customer to receive proactive updates if further delays occur"
  }},
  "status": "COMPLETE",
  "ambiguities": ["exact cause of delay not specified in call"]
}}

**Example 2 - Escalated Issue:**
{{
  "reasoning": {{
    "step1_validation": "Transcript has 10+ exchanges with clear complaint about customs delay",
    "step2_sentiment_analysis": "Strong negative sentiment - words like 'frustrated', 'unacceptable', 'ridiculous' indicate anger",
    "step3_classification_logic": "Complaint type due to service failure (lack of communication), high urgency due to production impact and financial loss mentioned",
    "step4_summary_basis": "Core issue: 3-day customs hold with no proactive communication. Financial impact stated. Agent limited by process constraints."
  }},
  "sentiment": {{
    "overall": "negative",
    "customerEmotion": "frustrated and impatient",
    "agentTone": "empathetic but limited by process"
  }},
  "classification": {{
    "interactionType": "complaint",
    "customerIntent": "resolve customs clearance delay immediately",
    "topics": ["customs", "documentation", "delay", "financial impact"],
    "urgency": "high",
    "severity": "high",
    "escalationSuggested": true,
    "escalationReason": "requires port operations manager intervention for customs expediting",
    "toxicLanguage": false
  }},
  "summary": {{
    "customerIssue": "Container held at customs for 3 days, production stopped",
    "resolution": "Basic information provided; escalated to supervisor",
    "followUpRequired": true,
    "followUpDetails": "Port operations manager to expedite customs clearance"
  }},
  "status": "COMPLETE",
  "ambiguities": ["specific documentation issue not detailed"]
}}

Now analyze the transcript provided above.
"""


final_prompt = enterprise_prompt.replace("{call_transcript}", detailed_call_transcript)

response = get_completion(final_prompt)
print("\n📋 ENTERPRISE CALL ANALYSIS (With Reasoning Visible):")
print(response)
print("\n" + "="*70 + "\n")

# # ============================================================================
# # PART 3: Math Self-Evaluation with Chain-of-Thought
# # ============================================================================
# print("="*70)
# print("PART 3: SELF-EVALUATION - WHY CHAIN-OF-THOUGHT MATTERS")
# print("="*70)

# math_problem = """
# Question:
# A Maersk vessel is loading containers at Mumbai port. The vessel can carry 150 containers total.
# Currently loaded: 60% are 40ft containers (each weighs 28 tons), and 40% are 20ft containers (each weighs 15 tons).
# The vessel's maximum weight capacity is 3500 tons.
# Is the vessel overloaded?

# Student's Solution:
# 150 containers × 28 tons = 4200 tons
# 4200 tons > 3500 tons maximum capacity
# Therefore: YES, the vessel is OVERLOADED.
# """

# # WITHOUT Chain-of-Thought (Model rushes to judgment)
# print("\n❌ WITHOUT CHAIN-OF-THOUGHT:")
# print("-" * 70)

# prompt_without_cot = f"""
# Determine if the student's solution is correct or not.

# {math_problem}
# """

# response_no_cot = get_completion(prompt_without_cot)
# print(response_no_cot)

# # WITH Chain-of-Thought (Model thinks step-by-step)
# print("\n✅ WITH CHAIN-OF-THOUGHT:")
# print("-" * 70)

# prompt_with_cot = f"""
# First, work out your own solution to the problem step by step.
# Then compare your solution to the student's solution and evaluate if the student is correct.

# Don't decide if the student's solution is correct until you have done the problem yourself.

# {math_problem}

# Your response should follow this structure:
# 1. MY SOLUTION:
#    - Calculate the correct answer step-by-step
#    - Show all calculations clearly

# 2. STUDENT'S SOLUTION REVIEW:
#    - Identify any errors in student's approach
#    - Compare final answers

# 3. VERDICT:
#    - State clearly if student is CORRECT or INCORRECT
#    - Explain why
# """

# response_with_cot = get_completion(prompt_with_cot)
# print(response_with_cot)

# print("\n" + "="*70)
# print("KEY TAKEAWAY:")
# print("="*70)
# print("""
# Without CoT: Model may agree with student's incorrect logic (multiplied ALL containers by 40ft weight)
# With CoT: Model calculates correctly (60% × 150 = 90 @ 28t, plus 40% × 150 = 60 @ 15t)
#          Correct total: 90×28 + 60×15 = 2520 + 900 = 3420 tons < 3500 → NOT overloaded

# Chain-of-Thought prevents the model from rushing to judgment and forces systematic reasoning.
# """)
