from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
client = OpenAI()

PDF_PATH = Path(r"C:\Users\ffarh\OneDrive\Desktop\Codes\Maersk\Maersk25-26\RAG\Profile (15).pdf")

# Add more documents here as needed
ADDITIONAL_DOCS = [
    Path(r"C:\Users\ffarh\OneDrive\Desktop\Codes\Maersk\Maersk25-26\RAG\Dummy_HR_Policy_Manual.pdf"),
    # Path(r"C:\Users\ffarh\OneDrive\Desktop\Codes\Maersk\Maersk25-26\RAG\third_doc.pdf"),
]

def get_or_create_vector_store(name="fk_vector_store"):
    """
    Check if vector store exists by name. If yes, return its ID.
    If no, create a new one. This prevents duplicate stores.
    """
    try:
        vector_stores = client.beta.vector_stores.list()
    except AttributeError:
        vector_stores = client.vector_stores.list()
    
    # Search for existing store with this name
    for store in vector_stores.data:
        if store.name == name:
            print(f"✅ Found existing vector store: '{name}' (ID: {store.id})")
            return store.id
    
    # Not found, create new one
    print(f"🆕 Creating new vector store: '{name}'")
    try:
        vector_store = client.beta.vector_stores.create(name=name)
    except AttributeError:
        vector_store = client.vector_stores.create(name=name)
    print(f"✅ Created with ID: {vector_store.id}")
    return vector_store.id

def is_file_already_uploaded(vector_store_id, file_name):
    """
    Check if a file with this name already exists in the vector store.
    Returns True if found, False otherwise.
    """
    try:
        files = client.beta.vector_stores.files.list(vector_store_id=vector_store_id)
    except AttributeError:
        files = client.vector_stores.files.list(vector_store_id=vector_store_id)
    
    # Check if any files exist
    if not hasattr(files, 'data') or not files.data:
        return False
    
    # Debug: Print what files are found
    print(f"🔍 Checking for '{file_name}' in vector store...")
    print(f"   Found {len(files.data)} file(s) in vector store")
    
    # Check each file by retrieving its details
    for file_obj in files.data:
        file_id = getattr(file_obj, 'id', None)
        if not file_id:
            continue
            
        try:
            # Retrieve the actual file details to get the filename
            file_details = client.files.retrieve(file_id)
            actual_filename = getattr(file_details, 'filename', '')
            
            print(f"   File ID: {file_id}, Filename: {actual_filename}")
            
            if file_name in actual_filename:
                print(f"   ✅ Match found!")
                return True
        except Exception as e:
            print(f"   ⚠️  Could not retrieve details for {file_id}")
            continue
    
    print(f"   ❌ No match found")
    return False

def upload_document(vector_store_id, file_path):
    """Upload a single document to vector store"""
    file_name = file_path.name
    
    # Check if already uploaded
    if is_file_already_uploaded(vector_store_id, file_name):
        print(f"⏭️  Skipping '{file_name}' - already in vector store")
        return
    
    print(f"📤 Uploading '{file_name}'...")
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
    print(f"✅ Uploaded '{file_name}'")

def upload_multiple_documents(vector_store_id, file_paths):
    """Upload multiple documents to the same vector store"""
    for file_path in file_paths:
        if file_path.exists():
            upload_document(vector_store_id, file_path)
        else:
            print(f"⚠️  File not found: {file_path}")

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

# Setup: Get or create vector store (reuses existing one)
print("\n" + "="*60)
print("📚 VECTOR STORE SETUP")
print("="*60)

# OPTIONAL: Uncomment the next 2 lines to delete existing vector store and start fresh
# delete_vector_store("demo_docs")
# print("="*60)

vector_store_id = get_or_create_vector_store("demo_docs")

# Upload primary document
upload_document(vector_store_id, PDF_PATH)

# Upload additional documents (if any)
if ADDITIONAL_DOCS:
    upload_multiple_documents(vector_store_id, ADDITIONAL_DOCS)

print("="*60)
print("✅ Setup complete! Ready for questions.\n")

# Interactive Q&A
while True:
    user_question = input("You: ").strip()
    
    if user_question.lower() in ("exit", "quit"):
        break
    
    if not user_question:
        continue
    
    answer = ask_question(vector_store_id, user_question)
