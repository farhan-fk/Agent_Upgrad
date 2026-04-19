from openai import OpenAI
import json

from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


# response = client.responses.create(
#     model="gpt-4o-mini",
#     input="Who won India Vs pak t20 world cup 2026 Cricket match?",
#     instructions="Be concise and factual.",
#     temperature=1,
    
    
# )

# print("Response from LLM with tool integration:", response.output_text)


# response = client.responses.create(
#     model="gpt-4o-mini",
#     input="who won India Vs pak t20 world cup 2026 Cricket match?",
#     instructions="Be concise and factual.",
#     temperature=1,
#     max_output_tokens=200,
#     tools=[{"type":"web_search_preview"}],
    
# )

# print("Response from LLM with tool integration:", response.output_text)

#Passing Information Between LLM Calls##
#Student's learning topic

topic = "Find The latest news aboout Black holes and summarize it in simple terms."
    
   
    
# First LLM call - Get explanation with web search
explanation_response = client.responses.create(
    model="gpt-4o-mini",
    input=f"{topic}",
    instructions="Provide a clear, simple explanation suitable for high school students.",
    temperature=0.7,
    max_output_tokens=400,
    tools=[{"type": "web_search_preview"}],
)
    
explanation = explanation_response.output_text
print("\n📖 Explanation:")
print(explanation)
    
  
    
# Second LLM call - Generate questions based on the explanation
quiz_response = client.responses.create(
    model="gpt-4o-mini",
    input=f"""Based on this explanation, create 3 practice questions with answers:

    {explanation}

    Generate:
    1. One easy multiple-choice question
    2. One medium fill-in-the-blank question  
    3. One challenging short-answer question

    Include the correct answers at the end.""",
    instructions="Create educational questions that test understanding of the explanation provided.",
    temperature=0.8,
    max_output_tokens=500,
)
    
print("\n✏️ Practice Questions:")
print(quiz_response.output_text)
    
print("\n" + "=" * 60)
print("✅ COMPLETE: Explanation → Practice Questions")
print("=" * 60)


    