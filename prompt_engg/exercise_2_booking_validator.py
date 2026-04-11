"""
===============================================================================
PROMPT ENGINEERING EXERCISE 2: CONTAINER BOOKING VALIDATOR
===============================================================================

LEARNING OBJECTIVES:
1. Practice Chain-of-Thought (CoT) prompting for complex validation
2. Implement conditional logic checks using "if-then" instructions
3. Use step-by-step reasoning to catch errors in business data
4. Generate actionable recommendations based on validation results

BUSINESS USE CASE:
Validate container booking requests before processing to catch errors early.
This prevents costly mistakes like:
- Wrong container type for cargo (dry container for refrigerated goods)
- Insufficient container size (40ft cargo in 20ft container)
- Invalid route combinations (landlocked destination for ocean freight)
- Missing required documentation

YOUR TASK:
Build a booking validator that checks for common errors and provides 
specific correction guidance.

REQUIREMENTS:
1. Accept booking details as input
2. Validate container type matches cargo requirements
3. Check container size is sufficient for cargo volume
4. Verify route is valid (origin/destination combination)
5. Identify missing documents
6. Provide step-by-step validation reasoning
7. Generate actionable error corrections

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
# VALIDATION RULES DATABASE
# ============================================================================

CONTAINER_RULES = """
CONTAINER TYPE REQUIREMENTS:
- Dry Container: General cargo, non-perishable goods, machinery, textiles
- Reefer Container: Pharmaceuticals, frozen foods, fresh produce, temperature-sensitive cargo
- Open Top: Oversized cargo, machinery exceeding standard height
- Flat Rack: Heavy machinery, vehicles, construction equipment
- Tank Container: Liquid chemicals, oils, hazardous liquids

CONTAINER SIZE CAPACITY:
- 20ft Standard: Max 28 cubic meters, Max 28 tons gross weight
- 40ft Standard: Max 67 cubic meters, Max 30 tons gross weight
- 40ft High Cube: Max 76 cubic meters, Max 30 tons gross weight

REQUIRED DOCUMENTS:
- Dry Cargo: Commercial Invoice, Packing List, Bill of Lading
- Reefer Cargo: Above + Temperature Control Certificate, Quality Certificate
- Hazardous Cargo: Above + MSDS (Material Safety Data Sheet), UN Classification
- Pharma Cargo: Above + GDP Certificate, Cold Chain Compliance Certificate

VALID ROUTES (Origin → Destination):
- JNPT Mumbai → Rotterdam (Netherlands)
- JNPT Mumbai → Hamburg (Germany)
- Chennai → Singapore
- Mundra → Dubai (UAE)
- JNPT Mumbai → New York (USA)
"""

# ============================================================================
# SAMPLE BOOKING REQUESTS FOR TESTING
# ============================================================================

sample_bookings = [
    {
        "booking_id": "BK-2024-001",
        "cargo_type": "Frozen Seafood Products",
        "cargo_volume": "45 cubic meters",
        "cargo_weight": "18 tons",
        "container_type": "40ft Dry Container",
        "origin": "JNPT Mumbai",
        "destination": "Rotterdam",
        "documents_submitted": ["Commercial Invoice", "Packing List"]
    },
    
    {
        "booking_id": "BK-2024-002",
        "cargo_type": "Textile Fabrics",
        "cargo_volume": "72 cubic meters",
        "cargo_weight": "12 tons",
        "container_type": "40ft Standard Container",
        "origin": "Chennai",
        "destination": "Singapore",
        "documents_submitted": ["Commercial Invoice", "Packing List", "Bill of Lading"]
    },
    
    {
        "booking_id": "BK-2024-003",
        "cargo_type": "Temperature-Controlled Vaccines",
        "cargo_volume": "15 cubic meters",
        "cargo_weight": "5 tons",
        "container_type": "20ft Reefer Container",
        "origin": "JNPT Mumbai",
        "destination": "Hamburg",
        "documents_submitted": [
            "Commercial Invoice", 
            "Packing List", 
            "Temperature Control Certificate",
            "GDP Certificate"
        ]
    }
]

# ============================================================================
# YOUR CODE STARTS HERE
# ============================================================================
# TODO: Write a Chain-of-Thought prompt that validates bookings step-by-step
# 
# HINTS:
# 1. Use delimiters to separate booking data from rules database
# 2. Instruct the model to follow these validation steps IN ORDER:
#    Step 1: Check if container type matches cargo requirements
#    Step 2: Check if container size is sufficient for cargo volume
#    Step 3: Verify the route is valid (origin → destination exists in rules)
#    Step 4: Identify any missing required documents
# 3. For EACH step, ask the model to:
#    - State what it's checking
#    - Show its reasoning
#    - Mark as PASS or FAIL
# 4. After all checks, provide final verdict and actionable corrections
# 5. Output should be structured with clear sections:
#    - VALIDATION STEPS (step-by-step reasoning)
#    - FINAL VERDICT (APPROVED / REJECTED)
#    - ERRORS FOUND (if any)
#    - RECOMMENDED ACTIONS (specific fixes)
# ============================================================================

def validate_booking(booking_data):
    """
    Validate container booking using Chain-of-Thought reasoning.
    
    Args:
        booking_data (dict): Booking details including cargo, container, route, docs
    
    Returns:
        str: Validation report with step-by-step reasoning and recommendations
    """
    
    # Convert booking dict to readable format
    booking_text = json.dumps(booking_data, indent=2)
    
    # YOUR PROMPT HERE - Replace this with your implementation
    prompt = f"""
    # Write your Chain-of-Thought prompt here
    # Remember to:
    # 1. Provide the validation rules database using delimiters
    # 2. Give step-by-step validation instructions
    # 3. Ask model to show reasoning for each step
    # 4. Request structured output format
    
    Validation Rules:
    ```
    {CONTAINER_RULES}
    ```
    
    Booking to Validate:
    ```
    {booking_text}
    ```
    
    Validation Process:
    [Your instructions for step-by-step validation]
    """
    
    # Get validation response
    response = get_completion(prompt)
    return response

# ============================================================================
# TEST YOUR SOLUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING CONTAINER BOOKING VALIDATOR")
    print("="*80)
    
    for i, booking in enumerate(sample_bookings, 1):
        print(f"\n📦 BOOKING {i}: {booking['booking_id']}")
        print("-" * 80)
        print(f"Cargo: {booking['cargo_type']}")
        print(f"Container: {booking['container_type']}")
        print(f"Route: {booking['origin']} → {booking['destination']}")
        print(f"Volume: {booking['cargo_volume']}, Weight: {booking['cargo_weight']}")
        print("-" * 80)
        
        # Validate the booking
        validation_report = validate_booking(booking)
        
        print("\n🔍 VALIDATION REPORT:")
        print(validation_report)
        print("\n" + "="*80)

# ============================================================================
# EXPECTED OUTPUT EXAMPLE
# ============================================================================
# For Booking 1 (Frozen Seafood in Dry Container - ERROR):
#
# VALIDATION STEPS:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 1: Container Type vs Cargo Requirements
# Checking: Does "40ft Dry Container" match "Frozen Seafood Products"?
# Reasoning: Frozen seafood requires temperature control. Per rules, frozen 
#            foods must use Reefer Container, not Dry Container.
# Result: ❌ FAIL - Container type mismatch
#
# Step 2: Container Size Sufficiency
# Checking: Is 40ft container sufficient for 45 cubic meters cargo?
# Reasoning: 40ft Standard capacity = 67 cubic meters. 45 < 67.
# Result: ✅ PASS - Size is sufficient
#
# Step 3: Route Validation
# Checking: Is "JNPT Mumbai → Rotterdam" a valid route?
# Reasoning: Per rules, this route is explicitly listed as valid.
# Result: ✅ PASS - Route is valid
#
# Step 4: Required Documents
# Checking: Are all required documents submitted for Reefer cargo?
# Reasoning: Reefer cargo requires: Commercial Invoice, Packing List, 
#            Bill of Lading, Temperature Control Certificate, Quality Certificate
#            Submitted: Commercial Invoice, Packing List
#            Missing: Bill of Lading, Temperature Control Certificate, Quality Certificate
# Result: ❌ FAIL - 3 documents missing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# FINAL VERDICT: ❌ REJECTED
#
# ERRORS FOUND:
# 1. Wrong container type (using Dry instead of Reefer)
# 2. Missing required documents (3 documents)
#
# RECOMMENDED ACTIONS:
# 1. CRITICAL: Change container type from "40ft Dry Container" to "40ft Reefer Container"
#    Reason: Frozen seafood requires temperature-controlled environment
#
# 2. Submit missing documents:
#    - Bill of Lading
#    - Temperature Control Certificate
#    - Quality Certificate
#
# 3. Once corrected, resubmit booking for approval
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# For Booking 3 (Vaccines in Reefer - APPROVED):
#
# VALIDATION STEPS:
# Step 1: ✅ PASS - Reefer container matches temperature-controlled vaccines
# Step 2: ✅ PASS - 20ft capacity (28 m³) > cargo volume (15 m³)
# Step 3: ✅ PASS - JNPT Mumbai → Hamburg is valid route
# Step 4: ✅ PASS - All required pharma documents submitted
#
# FINAL VERDICT: ✅ APPROVED
# No errors found. Booking can proceed.
# ============================================================================

# ============================================================================
# REFLECTION QUESTIONS (Answer after completing the exercise)
# ============================================================================
# 1. Why is step-by-step reasoning important for complex validation tasks?
#    Answer: 
#
# 2. How does Chain-of-Thought help the model avoid rushing to conclusions?
#    Answer: 
#
# 3. What happens if you skip providing the rules database to the model?
#    Answer: 
#
# 4. How would you extend this to validate pricing or customs regulations?
#    Answer: 
# ============================================================================

# ============================================================================
# BONUS CHALLENGE
# ============================================================================
# Try adding these advanced validations:
# 1. Check weight distribution (weight should not exceed container limits)
# 2. Validate temperature range for reefer cargo (e.g., vaccines need -20°C)
# 3. Check hazardous cargo UN classification codes
# 4. Verify customs documentation for specific destination countries
# 5. Calculate estimated transit time and validate against customer deadline
# ============================================================================
