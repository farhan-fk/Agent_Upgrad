from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
client = OpenAI()

PDF_PATH = Path(r"C:\Users\ffarh\OneDrive\Desktop\Openai_Sdk\RAG\Profile (30).pdf")

def create_vector_store(name="fk_vector_store"):
    try:
        vector_store = client.beta.vector_stores.create(name=name)
    except AttributeError:
        vector_store = client.vector_stores.create(name=name)
    return vector_store.id

def upload_document(vector_store_id, file_path):
    with file_path.open("rb") as f:
        try:
            client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id,
                files=[f],
            )
        except AttributeError:
            client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id,
                files=[f],
            )

def ask_question(vector_store_id, question):
    response = client.responses.create(
        model="gpt-5-nano",
        input=question,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store_id]
        }],
    )
    return response.output_text

# Setup
vector_store_id = create_vector_store("demo_docs")
upload_document(vector_store_id, PDF_PATH)

# Interactive Q&A
while True:
    user_question = input("You: ").strip()
    
    if user_question.lower() in ("exit", "quit"):
        break
    
    if not user_question:
        continue
    
    answer = ask_question(vector_store_id, user_question)
    print(f"AI: {answer}\n")