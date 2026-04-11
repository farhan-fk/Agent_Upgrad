from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()

OpenAI.api_key  = os.getenv('OPENAI_API_KEY')
# prompt = " Tell me a joke about a cat and a dog"
# def get_completion(prompt, model="gpt-4o-mini"):
#     messages = [{"role": "user", "content": prompt}]
#     response = client.responses.create(
#         model=model,
#         input=messages,
#         temperature=0
#     )
#     return response.output_text

# response1 = get_completion(prompt)
# print(response1)


# # Understanding system and user roles in chat models
prompt = " Tell me about Maersk company in less than 100 words."
def get_completion_one(prompt, model="gpt-4o-mini"):
    messages = [{"role":"system","content":"you reply to query in humurous way"},
                {"role": "user", "content": prompt}]
    response = client.responses.create(
        model=model,
        input=messages,
        temperature=0
    )
    return response.output_text

response1 = get_completion_one(prompt)
print("Humouorus output: ", response1)


# # Understanding the interpolation 
prompt3= f" You review the  llm response {response1}and refine it to be more professional and structured "

def get_completion_two(prompt3, model="gpt-4o-mini"):
    messages = [{"role":"system","content":"you are a helpful assistant that helps improve the professionalism of text"},
                {"role": "user", "content": prompt3}]
    response = client.responses.create(
        model=model,
        input=messages,
        temperature=0
    )
    return response.output_text

response2 = get_completion_two(prompt3)
print("Professional output: ", response2)
