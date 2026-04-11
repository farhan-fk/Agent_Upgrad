# virtaul activation code for VS code (.\venv\Scripts\activate)
#Principle1: Strucyuring the prompt and Tactics to get the best out of LLMs

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

# def get_completion(prompt, model="gpt-4o-mini"):
#     messages = [{"role": "user", "content": prompt}]
#     response = openai.responses.create(
#         model=model,
#         input=messages,
#         temperature=0, # this is the degree of randomness of the model's output
#     )
#     return response.output_text

# Prompting Principle (More to follow)
# Principal1 : Write clear and specific Instructions (Not necssarily short,sometimes longer prompts give more context to LLMs to give better responses)

# Tactic 1: Use delimiters
# - Triple quotes: """
# - Triple backticks: ```
# - Triple dashes: ---
# - Angle brackets: < >
# - XML tags: <tag> </tag>

# principal 2 : Give the model time to think


# in python \ is uded to break a line into multiple lines
# Tactic 1: Use delimiters to clearly separate instructions from content
# Real-world use case: Incident Report Summarizer for Maersk Operations

# text = f"""
# INCIDENT REPORT - IR-2024-1156

# Date/Time: November 15, 2024, 14:30 IST
# Reported By: Rajesh Kumar, Operations Manager, Mumbai Port
# Vessel: MV Maersk Dhaka (Voyage: 424N)
# Container(s): MAEU4567891, MAEU4567892, MAEU4567893

# INCIDENT DESCRIPTION:
# On November 15, 2024, at approximately 14:30 hours, three refrigerated containers 
# experienced power failure during loading operations at Jawaharlal Nehru Port, Mumbai. 
# The containers were being loaded onto MV Maersk Dhaka for shipment to Rotterdam.

# The power failure occurred due to a faulty reefer plug connection at Bay 14, Row 3. 
# The electrical team identified that the plug socket had corroded contacts, causing 
# intermittent power supply. Temperature monitoring showed that container MAEU4567891 
# (containing pharmaceutical products) experienced a temperature rise from -20°C to -12°C 
# over a 45-minute period before the issue was detected.

# CARGO DETAILS:
# - MAEU4567891: Pharmaceutical products (temperature-sensitive vaccines) - Customer: PharmaCorp Ltd
# - MAEU4567892: Frozen seafood products - Customer: Ocean Harvest Exports
# - MAEU4567893: Fresh fruits (mangoes) - Customer: Global Foods Trading

# IMMEDIATE ACTIONS TAKEN:
# 1. All three containers were immediately disconnected and moved to standby reefer area
# 2. Alternative power connections were arranged within 20 minutes
# 3. Temperature monitoring confirmed MAEU4567892 and MAEU4567893 maintained required temperatures
# 4. Container MAEU4567891 temperature stabilized at -18°C after 1 hour
# 5. Electrical maintenance team replaced the faulty socket at Bay 14, Row 3
# 6. Customer PharmaCorp Ltd was notified of the temperature excursion

# IMPACT ASSESSMENT:
# - Vessel departure delayed by 3 hours (original ETD: 18:00, revised ETD: 21:00)
# - 45 minutes of temperature excursion for pharmaceutical cargo
# - Customer PharmaCorp requesting cargo inspection before acceptance
# - Potential insurance claim for compromised pharmaceutical products
# - Estimated financial exposure: USD 75,000 (cargo value) + USD 12,000 (delay costs)

# CURRENT STATUS:
# - Containers MAEU4567892 and MAEU4567893 loaded successfully with normal parameters
# - Container MAEU4567891 on hold pending customer decision and quality inspection
# - Third-party surveyor scheduled for November 16, 2024, 09:00 hours
# - Port authority notified, incident logged in port safety system
# - Equipment maintenance team conducting full audit of all reefer connections in Bay 14

# NEXT STEPS REQUIRED:
# 1. Await surveyor report on pharmaceutical cargo condition (Due: Nov 16, 17:00)
# 2. Coordinate with customer for final decision on cargo acceptance/rejection
# 3. If rejected: arrange alternative transportation or return to shipper
# 4. Complete root cause analysis on electrical infrastructure
# 5. Update vessel schedule and notify all downstream ports of revised ETA
# 6. Process insurance documentation if cargo claim is filed

# ROOT CAUSE ANALYSIS:
# Preliminary investigation indicates inadequate preventive maintenance schedule for reefer 
# plug sockets in high-humidity areas. Last maintenance of Bay 14 sockets was conducted 
# 8 months ago, exceeding the recommended 6-month interval for coastal port facilities.

# RESPONSIBLE PARTIES:
# - Port Operations: Rajesh Kumar (Incident Commander)
# - Electrical Maintenance: Suresh Patil (Technical Lead)
# - Customer Service: Priya Sharma (Account Manager - PharmaCorp)
# - Claims & Insurance: Amit Desai (Claims Coordinator)
# """

# prompt = f"""
# Summarize the incident report delimited by triple backticks into a concise \
# executive summary suitable for management review. 

# The summary should include:
# - What happened (one sentence)
# - Key impact (financial, operational)
# - Current status
# - Critical action required

# Keep the summary under 100 words.

# ```{text}```
# """

# response = get_completion(prompt)
# print(response)

# # #Tactic 2: Ask for a structured output
# # # Use case: Extract key info from customer call to create support ticket
# # # JSON output can be directly saved to ticketing system or database

# call_transcript = f"""
# Agent: Good morning, thank you for calling Maersk customer service. This is Priya speaking. 
# May I have your company name and booking reference number please?

# Customer: Yes, hello. This is Ramesh Kumar from TechWorld Exports Private Limited, Mumbai.

# Agent: Thank you Mr. Ramesh. How can I help you today?

# Customer: We have booking with you, the reference number is... let me check... yes, 
# MAEU20241115. Actually we are having some problems with this booking.

# Agent: Okay, let me pull up that booking. MAEU20241115... yes I can see it. This is for 
# one 40-foot dry container from Mumbai to Hamburg, loading date November 18th on vessel 
# MV Maersk Edinburgh. Is that correct?

# Customer: Yes yes, that's the one. But see, we have two problems now. First thing is, 
# our cargo specification has changed. Originally we were shipping electronic components in 
# dry container, but now supplier changed and we received pharmaceutical raw materials which 
# needs temperature control. So we need reefer container now, not dry container.

# Agent: I understand. So you need equipment type change from dry to refrigerated container.

# Customer: Yes, exactly. And second problem is customs. Yesterday we got notice from customs 
# department that our export documents having some errors in HS code classification. We need 
# to resubmit corrected documents. This will take minimum 2 to 3 days. So we cannot load on 
# 18th November. We need to push loading date to 21st November.

# Agent: Alright, so two changes needed - equipment change from dry to reefer, and reschedule 
# loading from 18th to 21st November. Let me check vessel schedule... MV Maersk Edinburgh 
# departs 19th November, so you'll miss that sailing anyway.

# Customer: Oh no, what is next available vessel?

# Agent: Next vessel on same route is MV Maersk Copenhagen departing 23rd November. Would that work?

# Customer: Hmm, let me think... yes okay, that should be fine. Our customer in Hamburg is 
# already informed there will be some delay. But this is very urgent for us because we have 
# penalty clause in contract. Every day delay is costing us money.

# Agent: I completely understand Mr. Ramesh. I will mark this as high priority ticket. Can I 
# confirm your registered email address - is it contact@techworld.in?

# Customer: No no, that's old email. Please use ramesh.kumar@techworld-exports.com. That's my 
# direct email. I need confirmation quickly.

# Agent: Noted, ramesh.kumar@techworld-exports.com. I'm creating high priority ticket right now 
# for equipment change and schedule modification. You will receive confirmation email within 
# one hour with new booking details.

# Customer: Okay good. And what about additional charges for reefer container? Will it be more expensive?

# Agent: Yes, there will be price difference because reefer containers have higher rates. The 
# commercial team will send you revised quotation along with confirmation. They will contact you 
# within 2 hours.

# Customer: Alright, please make sure they contact fast. We need to finalize everything today only.

# Agent: Absolutely. Is there anything else I can help you with?

# Customer: No, that's all. Just please process this urgently.

# Agent: Definitely Mr. Ramesh. Your ticket reference number is TKT-2024-8821. You'll receive 
# all details on your email shortly. Thank you for calling Maersk.

# Customer: Thank you, bye.
# """

# prompt = f"""
# Extract key information from the customer call transcript and provide it in JSON format \
# with the following fields:
# - booking_number: string
# - customer_name: string (person's name)
# - customer_company: string
# - customer_email: string
# - issue_type: string (choose: "Equipment Change" or "Schedule Change" or "Documentation Issue" or "Multiple Issues")
# - requested_equipment_change: string (e.g., "Dry to Reefer" or "None")
# - requested_new_date: string (format: "DD Month" or "None")
# - urgency_level: string (choose: "High" or "Medium" or "Low")
# - ticket_number: string (if mentioned, else "Not assigned")

# Return only valid JSON format, no additional text.

# ```{call_transcript}```
# """

# response = get_completion(prompt)
# print(response)

# # Why JSON output?
# # The JSON format allows the extracted data to be directly saved into:
# # - Customer support ticketing systems (like ServiceNow, Jira Service Management)
# # - Database records for tracking and analytics
# # - CRM platforms (like Salesforce)
# # This eliminates manual data entry, reduces errors, and speeds up ticket creation.

# # Tactic 3: Ask the model to check whether conditions are met
# # Use case: Container Equipment Availability System
# # Check if requested container type is available at customer's preferred location

container_inventory = """
{
  "containers": [
    {"type": "40ft Reefer", "available_count": {"JNPT_Mumbai": 12, "Mundra_Port": 0, "Chennai_Port": 8}},
    {"type": "40ft Dry", "available_count": {"JNPT_Mumbai": 45, "Mundra_Port": 23, "Chennai_Port": 31}},
    {"type": "20ft Reefer", "available_count": {"JNPT_Mumbai": 0, "Mundra_Port": 5, "Chennai_Port": 0}},
    {"type": "40ft Open Top", "available_count": {"JNPT_Mumbai": 3, "Mundra_Port": 0, "Chennai_Port": 2}},
    {"type": "40ft Flat Rack", "available_count": {"JNPT_Mumbai": 0, "Mundra_Port": 0, "Chennai_Port": 0}}
  ]
}
"""

booking_request = """
Customer: TechWorld Exports
Requested Container: 40ft Reefer
Pickup Location: JNPT_Mumbai
Loading Date: November 20, 2024
Booking Number: MAEU20241115
"""

prompt = f"""
You are a container availability checking system for Maersk.

You will be provided with:
1) Container inventory across multiple Indian ports
2) A customer booking request

Your task:
- Check if the requested container type is available at the preferred pickup location
- If available (count > 0): Confirm availability and provide pickup instructions
- If NOT available at preferred location but available elsewhere: Suggest transfer from nearest location
- If NOT available anywhere: Inform customer to contact operations team

Provide response in this format:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTAINER AVAILABILITY STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Requested: <container type>
Status: <Available/Transfer Required/Not Available>
Location: <pickup location or transfer details>
Next Steps: <clear action items>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

--- INVENTORY DATABASE ---
{container_inventory}

--- BOOKING REQUEST ---
{booking_request}
"""

response = get_completion(prompt)
print(response)

# # # # Why this tactic is important?
# # # # This demonstrates conditional logic in prompts. The LLM evaluates multiple conditions:
# # # # 1. Is container available at preferred location? → Confirm
# # # # 2. Available elsewhere? → Suggest transfer
# # # # 3. Not available anywhere? → Escalate to operations
# # # # This is useful for decision-making workflows, approval systems, and intelligent routing.

# # # # Tactic 4: Few-shot prompting
# # # # Use case: Classify customer feedback sentiment in shipping/logistics context
# # # # Few-shot examples teach the LLM industry-specific sentiment rules that differ from general sentiment

# # prompt = f"""
# # You are analyzing customer feedback for Maersk's shipping operations. 

# # In the shipping industry, sentiment classification has SPECIAL RULES:
# # - "Delay" is ALWAYS negative, even if customer says "only" or "just"
# # - "Early arrival" is ALWAYS positive
# # - "Vessel change" can be neutral if no delay mentioned
# # - "Additional charges" is ALWAYS negative
# # - "Proactive communication" is ALWAYS positive

# # Classify sentiment as: POSITIVE, NEGATIVE, or NEUTRAL

# # <example_1>
# # Feedback: "Container arrived 2 days early, very happy with service"
# # Sentiment: POSITIVE
# # Reason: Early arrival
# # </example_1>

# # <example_2>
# # Feedback: "There was only a small delay of 6 hours, but team kept us informed throughout"
# # Sentiment: NEGATIVE
# # Reason: Any delay is negative in shipping, despite positive communication
# # </example_2>

# # <example_3>
# # Feedback: "Vessel changed from MV Maersk Delhi to MV Maersk Mumbai, same ETA maintained"
# # Sentiment: NEUTRAL
# # Reason: Vessel change with no schedule impact
# # </example_3>

# # <example_4>
# # Feedback: "Received additional detention charges bill today"
# # Sentiment: NEGATIVE
# # Reason: Unexpected charges are always frustrating
# # </example_4>

# # <example_5>
# # Feedback: "Your team proactively called us before the issue escalated, great service"
# # Sentiment: POSITIVE
# # Reason: Proactive communication is valued highly
# # </example_5>

# # Now classify this feedback:

# # Feedback: "Shipment had just 4-hour delay at port, but honestly your customer service kept updating us every hour, so we weren't stressed"
# # """

# # response = get_completion(prompt)
# # print("\n" + "="*60)
# # print("WITH FEW-SHOT EXAMPLES (Industry-aware)")
# # print("="*60)
# # print(response)

# # # Now let's see what happens WITHOUT few-shot examples
# # prompt_without_examples = f"""
# # You are analyzing customer feedback for Maersk's shipping operations.
# # Classify the sentiment as: POSITIVE, NEGATIVE, or NEUTRAL

# # Feedback: "Shipment had just 4-hour delay at port, but honestly your customer service kept updating us every hour, so we weren't stressed"

# # Sentiment:
# # """

# # response_no_examples = get_completion(prompt_without_examples)
# # print("\n" + "="*60)
# # print("WITHOUT FEW-SHOT EXAMPLES (Generic sentiment)")
# # print("="*60)
# # print(response_no_examples)

# # Why Few-shot Prompting is critical here?
# # 
# # WITHOUT few-shot: LLM sees "but honestly", "great customer service", "weren't stressed"
# # → Classifies as POSITIVE (generic sentiment analysis)
# #
# # WITH few-shot: LLM learns "ANY delay = NEGATIVE in shipping industry"
# # → Classifies as NEGATIVE (industry-specific rules)
# #
# # Few-shot examples teach domain-specific logic that contradicts general language patterns.
# # This is essential for:
# # - Industry-specific classification systems
# # - Custom business rules that differ from common sense
# # - Context-dependent interpretation
# # - Training without fine-tuning the model


# #  Recap in This Lesson we learned Very Important Prompting Techniques like\
# #  how we need to be specific in our instructions (Use Tactics 1), \
# #  Define the structure of output (Use Tactics 2), \
# #  Ask the model to verify whether certain conditions are met (Use Tactics 3),\
# #  And Share Some Examples of the Desired Output (Use Tactics 4)
# #  All these techniques will help you to get the best out of LLMs.
