"""
===============================================================================
PROMPT ENGINEERING EXERCISE 1: CUSTOMER SENTIMENT ANALYZER
===============================================================================

LEARNING OBJECTIVES:
1. Practice using delimiters to separate content from instructions
2. Implement structured JSON output for business applications
3. Apply few-shot prompting for domain-specific classification
4. Combine multiple prompt engineering tactics in one solution

BUSINESS USE CASE:
Analyze customer emails/messages to prioritize support responses and route to 
appropriate departments. This is critical for:
- High-volume customer support teams
- Automated ticket routing systems
- Customer satisfaction tracking
- Escalation management

YOUR TASK:
Build a customer sentiment analyzer that classifies messages and extracts 
key information for the support team.

REQUIREMENTS:
1. Accept customer message as input
2. Classify sentiment (Positive/Negative/Neutral)
3. Identify urgency level (High/Medium/Low)
4. Extract key topics mentioned
5. Recommend department routing
6. Output structured JSON format

===============================================================================
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

def get_completion(prompt, model="gpt-4o-mini"):
    """Helper function to call OpenAI API"""
    messages = [{"role": "user", "content": prompt}]
    response = client.responses.create(
        model=model,
        input=messages,
        temperature=0
    )
    return response.output_text

# ============================================================================
# SAMPLE CUSTOMER MESSAGES FOR TESTING
# ============================================================================

sample_messages = [
    """
    Subject: URGENT - Container stuck at customs for 5 days!
    
    I am extremely frustrated! Our container MAEU9876543 has been sitting at 
    Mumbai customs for 5 DAYS now. We submitted all required documents on time 
    but your team hasn't followed up. This delay is costing us $2000 per day 
    in penalties to our buyer. I need immediate escalation to your customs team 
    and a manager to call me TODAY. This is completely unacceptable service!
    
    - Vikram Patel, Operations Director
    """,
    
    """
    Hi team,
    
    Quick question - I noticed my booking confirmation shows a 40ft container 
    but I actually need a 20ft container for this shipment. Can someone help 
    me modify the booking? No rush, loading date is still 10 days away. Let me 
    know what documents you need from my side.
    
    Thanks,
    Anjali
    """,
    
    """
    Hello Maersk,
    
    I wanted to share positive feedback about your Mumbai port team. Our shipment 
    arrived 2 days earlier than expected, and your agent Rajesh proactively 
    informed us about early arrival so we could arrange pickup. This kind of 
    communication really helps our planning. Great service, keep it up!
    
    Best regards,
    Suresh Kumar, Supply Chain Manager
    """
]

# ============================================================================
# YOUR CODE STARTS HERE
# ============================================================================
# TODO: Write a prompt that analyzes customer messages and returns structured data
# 
# HINTS:
# 1. Use triple backticks ``` to delimit the customer message
# 2. Provide few-shot examples to teach sentiment classification rules:
#    - "Delay" = always negative
#    - "Early arrival" = always positive
#    - "Question/clarification" = neutral
#    - "Urgent/Immediate" = high urgency
# 3. Define clear JSON structure with these fields:
#    {
#      "sentiment": "Positive|Negative|Neutral",
#      "urgency": "High|Medium|Low",
#      "topics": ["list", "of", "topics"],
#      "recommended_department": "Customs|Operations|Customer Service|Sales",
#      "requires_escalation": true|false,
#      "summary": "one-sentence summary of the issue"
#    }
# 4. Ask the model to think step-by-step before classifying
# ============================================================================

def analyze_customer_message(customer_message):
    """
    Analyze customer message and return structured sentiment analysis.
    
    Args:
        customer_message (str): The customer's email or message text
    
    Returns:
        dict: Parsed JSON with sentiment, urgency, topics, and routing info
    """
    
    # YOUR PROMPT HERE - Replace this with your implementation
    prompt = f"""
    # Write your prompt engineering solution here
    # Remember to use:
    # - Delimiters (```) to separate the customer message
    # - Few-shot examples for sentiment classification
    # - Clear JSON structure definition
    # - Step-by-step reasoning instructions
    
    Customer Message:
    ```
    {customer_message}
    ```
    """
    
    # Get response from LLM
    response = get_completion(prompt)
    
    # Parse JSON response
    try:
        result = json.loads(response)
        return result
    except json.JSONDecodeError:
        print("⚠️  Warning: Response was not valid JSON")
        return {"raw_response": response}

# ============================================================================
# TEST YOUR SOLUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING CUSTOMER SENTIMENT ANALYZER")
    print("="*80)
    
    for i, message in enumerate(sample_messages, 1):
        print(f"\n📧 TEST MESSAGE {i}:")
        print("-" * 80)
        print(message.strip())
        print("-" * 80)
        
        # Analyze the message
        result = analyze_customer_message(message)
        
        print("\n📊 ANALYSIS RESULT:")
        print(json.dumps(result, indent=2))
        print("\n" + "="*80)

# ============================================================================
# EXPECTED OUTPUT EXAMPLE
# ============================================================================
# For Message 1 (Urgent complaint), you should get something like:
# {
#   "sentiment": "Negative",
#   "urgency": "High",
#   "topics": ["customs delay", "financial loss", "escalation request"],
#   "recommended_department": "Customs",
#   "requires_escalation": true,
#   "summary": "Container stuck at customs for 5 days causing daily $2000 penalty"
# }
#
# For Message 2 (Simple question), you should get:
# {
#   "sentiment": "Neutral",
#   "urgency": "Low",
#   "topics": ["booking modification", "container type change"],
#   "recommended_department": "Customer Service",
#   "requires_escalation": false,
#   "summary": "Customer needs to change container size from 40ft to 20ft"
# }
#
# For Message 3 (Positive feedback), you should get:
# {
#   "sentiment": "Positive",
#   "urgency": "Low",
#   "topics": ["early delivery", "proactive communication", "positive feedback"],
#   "recommended_department": "Customer Service",
#   "requires_escalation": false,
#   "summary": "Customer praising early arrival and proactive communication"
# }
# ============================================================================

# ============================================================================
# REFLECTION QUESTIONS (Answer after completing the exercise)
# ============================================================================
# 1. Why is it important to use delimiters when passing customer messages?
#    Answer: 
#
# 2. How do few-shot examples improve sentiment classification accuracy?
#    Answer: 
#
# 3. What are the benefits of structured JSON output vs. plain text response?
#    Answer: 
#
# 4. How would you handle edge cases (e.g., mixed sentiment in one message)?
#    Answer: 
# ============================================================================
