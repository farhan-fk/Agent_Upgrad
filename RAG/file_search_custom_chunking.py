"""
🔬 CUSTOM CHUNKING DEMONSTRATION
Learn how to control chunk size, overlap, and retrieval parameters

CHUNKING PARAMETERS EXPLAINED:
================================
📊 Chunk Size: Maximum tokens per chunk (default: 800)
   - Larger chunks (1600) → More context, fewer chunks
   - Smaller chunks (400) → More precise, more chunks

🔗 Chunk Overlap: Tokens shared between consecutive chunks (default: 400)
   - Prevents splitting ideas/sentences mid-thought
   - More overlap → better context continuity

📥 Max Results: Number of chunks retrieved for each query (default: 20)
   - More results → broader context but more tokens used
   - Fewer results → faster, more focused answers

USE CASES:
==========
🔹 Default (800/400): General purpose - news, reports, articles
🔹 Large Chunks (1600/800): Legal docs, technical manuals, research papers
🔹 Small Chunks (400/200): FAQs, product catalogs, quick lookups
"""

from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
client = OpenAI()

PDF_PATH = Path(r"C:\Users\ffarh\OneDrive\Desktop\Codes\Maersk\Maersk25-26\RAG\Profile (15).pdf")


# ========================================
# CHUNKING STRATEGY CONFIGURATIONS
# ========================================

def get_default_chunking():
    """Default OpenAI chunking (800 tokens, 400 overlap)"""
    return {
        "type": "static",
        "static": {
            "max_chunk_size_tokens": 800,
            "chunk_overlap_tokens": 400
        }
    }

def get_large_chunk_strategy():
    """Large chunks for documents needing more context"""
    return {
        "type": "static",
        "static": {
            "max_chunk_size_tokens": 1600,
            "chunk_overlap_tokens": 800
        }
    }

def get_small_chunk_strategy():
    """Small chunks for precise, specific lookups"""
    return {
        "type": "static",
        "static": {
            "max_chunk_size_tokens": 400,
            "chunk_overlap_tokens": 200
        }
    }


# ========================================
# VECTOR STORE FUNCTIONS
# ========================================

def create_vector_store_with_chunking(name, chunking_strategy):
    """
    Create vector store with specific chunking strategy
    
    Args:
        name: Name for the vector store
        chunking_strategy: Dict with chunking parameters
    """
    print(f"\n🆕 Creating vector store: '{name}'")
    print(f"   Chunk size: {chunking_strategy['static']['max_chunk_size_tokens']} tokens")
    print(f"   Chunk overlap: {chunking_strategy['static']['chunk_overlap_tokens']} tokens")
    
    try:
        vector_store = client.beta.vector_stores.create(name=name)
    except AttributeError:
        vector_store = client.vector_stores.create(name=name)
    
    print(f"✅ Created with ID: {vector_store.id}")
    return vector_store.id


def upload_document_with_chunking(vector_store_id, file_path, chunking_strategy):
    """
    Upload document with custom chunking strategy
    
    Args:
        vector_store_id: ID of the vector store
        file_path: Path to document
        chunking_strategy: Dict with chunking parameters
    """
    file_name = file_path.name
    print(f"\n📤 Uploading '{file_name}' with custom chunking...")
    
    with file_path.open("rb") as f:
        try:
            # Upload file with chunking strategy
            client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id,
                files=[f],
                chunking_strategy=chunking_strategy
            )
        except AttributeError:
            client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id,
                files=[f],
                chunking_strategy=chunking_strategy
            )
    
    print(f"✅ Uploaded and indexed with custom chunking!")


def ask_question_with_custom_retrieval(vector_store_id, question, max_results=20):
    """
    Ask question with custom max_num_results parameter
    
    Args:
        vector_store_id: ID of the vector store
        question: User's question
        max_results: Maximum number of chunks to retrieve (default: 20)
    """
    response = client.responses.create(
        model="gpt-4o-mini",
        input=question,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store_id],
            "file_search": {
                "max_num_results": max_results  # Control retrieval count
            }
        }],
    )
    return response.output_text


# ========================================
# DEMONSTRATION: Compare Chunking Strategies
# ========================================

def demo_chunking_comparison():
    """
    Demonstrates different chunking strategies
    Choose which strategy to test by uncommenting
    """
    
    print("\n" + "="*70)
    print("🔬 CUSTOM CHUNKING DEMONSTRATION")
    print("="*70)
    
    # ========================================
    # STRATEGY 1: Default Chunking (800/400)
    # ========================================
    print("\n📌 STRATEGY 1: DEFAULT CHUNKING")
    print("-" * 70)
    
    chunking_strategy = get_default_chunking()
    vector_store_id = create_vector_store_with_chunking(
        "demo_default_chunks", 
        chunking_strategy
    )
    upload_document_with_chunking(vector_store_id, PDF_PATH, chunking_strategy)
    
    print("\n💬 Testing with default retrieval (20 chunks)...")
    question = "What are the main qualifications and skills?"
    answer = ask_question_with_custom_retrieval(vector_store_id, question, max_results=20)
    print(f"\nQ: {question}")
    print(f"A: {answer}")
    
    
    # ========================================
    # STRATEGY 2: Large Chunks (1600/800) - UNCOMMENT TO TEST
    # ========================================
    # print("\n📌 STRATEGY 2: LARGE CHUNKS (More Context)")
    # print("-" * 70)
    
    # chunking_strategy = get_large_chunk_strategy()
    # vector_store_id = create_vector_store_with_chunking(
    #     "demo_large_chunks", 
    #     chunking_strategy
    # )
    # upload_document_with_chunking(vector_store_id, PDF_PATH, chunking_strategy)
    
    # print("\n💬 Testing with more results (30 chunks)...")
    # question = "What are the main qualifications and skills?"
    # answer = ask_question_with_custom_retrieval(vector_store_id, question, max_results=30)
    # print(f"\nQ: {question}")
    # print(f"A: {answer}")
    
    
    # ========================================
    # STRATEGY 3: Small Chunks (400/200) - UNCOMMENT TO TEST
    # ========================================
    # print("\n📌 STRATEGY 3: SMALL CHUNKS (Precise Lookup)")
    # print("-" * 70)
    
    # chunking_strategy = get_small_chunk_strategy()
    # vector_store_id = create_vector_store_with_chunking(
    #     "demo_small_chunks", 
    #     chunking_strategy
    # )
    # upload_document_with_chunking(vector_store_id, PDF_PATH, chunking_strategy)
    
    # print("\n💬 Testing with fewer results (10 chunks)...")
    # question = "What are the main qualifications and skills?"
    # answer = ask_question_with_custom_retrieval(vector_store_id, question, max_results=10)
    # print(f"\nQ: {question}")
    # print(f"A: {answer}")
    
    
    print("\n" + "="*70)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*70)
    print("\n💡 TIP: Uncomment other strategies above to compare results!")
    print("   - Large chunks: Better for complex, contextual questions")
    print("   - Small chunks: Better for specific, factual lookups")
    print("   - Adjust max_results to control answer breadth vs. speed")


# ========================================
# INTERACTIVE MODE (Optional)
# ========================================

def interactive_mode(vector_store_id):
    """
    Interactive Q&A with custom retrieval settings
    """
    print("\n" + "="*70)
    print("💬 INTERACTIVE MODE")
    print("="*70)
    print("Commands:")
    print("  - Type your question")
    print("  - Type 'exit' to quit")
    print("  - Type 'results:N' to change max results (e.g., 'results:30')")
    print("="*70 + "\n")
    
    max_results = 20  # Default
    
    while True:
        user_input = input(f"You (max_results={max_results}): ").strip()
        
        if user_input.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break
        
        # Change max_results setting
        if user_input.lower().startswith("results:"):
            try:
                max_results = int(user_input.split(":")[1])
                print(f"✅ Set max_results to {max_results}")
            except:
                print("⚠️ Invalid format. Use 'results:20'")
            continue
        
        if not user_input:
            continue
        
        answer = ask_question_with_custom_retrieval(vector_store_id, user_input, max_results)
        print(f"AI: {answer}\n")


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    # Run the chunking comparison demo
    demo_chunking_comparison()
    
    # Uncomment to enable interactive mode after demo
    # print("\n" + "="*70)
    # print("Starting interactive mode with last vector store...")
    # interactive_mode(vector_store_id)  # Uses the last created vector_store_id


# ========================================
# 📚 LEARNING EXERCISES
# ========================================
"""
🎯 EXERCISE 1: Compare Chunk Sizes
1. Run the code with default chunking (800/400)
2. Uncomment Strategy 2 (large chunks 1600/800)
3. Uncomment Strategy 3 (small chunks 400/200)
4. Ask the same question to all three
5. Compare the answers - which works best for your use case?

🎯 EXERCISE 2: Optimize Retrieval
1. Test with max_results=5 (fewer chunks, faster)
2. Test with max_results=50 (more chunks, broader context)
3. Find the sweet spot for your questions

🎯 EXERCISE 3: Real-World Use Case
Think about Maersk documents:
- Shipping contracts → Large chunks (legal language needs context)
- FAQ database → Small chunks (quick, specific answers)
- Technical manuals → Medium chunks (balance of both)

Try uploading different document types and tune chunking accordingly!
"""
