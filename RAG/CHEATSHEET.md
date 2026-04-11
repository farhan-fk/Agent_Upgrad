# 🔍 RAG (Retrieval-Augmented Generation) - Cheat Sheet

## 📚 Key Concepts

### 1. **What is RAG?**
Retrieval-Augmented Generation = Retrieve relevant docs + Generate answer
```
Query → Search Knowledge Base → Retrieve Context → LLM Generates Answer
```

### 2. **Why RAG?**
- ✅ Reduce hallucinations
- ✅ Access to up-to-date information
- ✅ Domain-specific knowledge
- ✅ Cite sources
- ❌ Without RAG: LLM only knows training data

### 3. **RAG Pipeline Components**
```python
1. Document Loader    → Load documents
2. Text Splitter      → Break into chunks
3. Embeddings         → Convert to vectors
4. Vector Store       → Store + search
5. Retriever          → Find relevant chunks
6. LLM                → Generate answer
```

## 💡 Complete RAG Implementation

### Step 1: Load Documents
```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://example.com/docs")
docs = loader.load()
```

### Step 2: Split Text
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
splits = text_splitter.split_documents(docs)
```

### Step 3: Create Embeddings
```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

### Step 4: Create Vector Store
```python
from langchain_chroma import Chroma

vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
```

### Step 5: Create Retriever
```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}  # Return top 3 chunks
)
```

### Step 6: Query
```python
# Retrieve relevant docs
relevant_docs = retriever.invoke("What is the refund policy?")

# Build context
context = "\n\n".join([doc.page_content for doc in relevant_docs])

# Generate answer with context
prompt = f"""
Use the following context to answer the question.

Context:
{context}

Question: {question}

Answer:
"""

response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt
)
```

## 🔑 Important Files

| File | Purpose |
|------|---------|
| `file_search_ui_one.py` | OpenAI Assistants API with file_search |
| `file_search_two.py` | OpenAI vector stores |
| `file_search_project_three.py` | Project-specific RAG |
| `hybrid_rag_chatbot_with_memory.ipynb` | RAG + conversational memory |
| `chroma_db/` | Persistent vector database |

## 🎯 RAG Patterns

### Pattern 1: Simple RAG
```python
docs = retrieve(query)
answer = llm(query, context=docs)
```

### Pattern 2: RAG with Memory
```python
conversation_history = []

# Add to history
conversation_history.append({"role": "user", "content": query})

# Retrieve + generate
docs = retrieve(query)
answer = llm(query, context=docs, history=conversation_history)

# Remember
conversation_history.append({"role": "assistant", "content": answer})
```

### Pattern 3: Hybrid RAG
```python
# Combine multiple sources
web_docs = retrieve_from_web(query)
db_results = query_database(query)
file_docs = retrieve_from_files(query)

all_context = web_docs + db_results + file_docs
answer = llm(query, context=all_context)
```

### Pattern 4: Re-ranking
```python
# Get more candidates
docs = retriever.invoke(query, k=10)

# Re-rank by relevance
ranked_docs = rerank(query, docs, top_k=3)

# Use best matches
answer = llm(query, context=ranked_docs)
```

## 🛠️ Vector Store Options

| Vector Store | Best For | Pros | Cons |
|--------------|----------|------|------|
| **Chroma** | Local/dev | Easy setup, persistent | Not for large scale |
| **Pinecone** | Production | Managed, scalable | Paid service |
| **Faiss** | Performance | Very fast | No persistence |
| **Weaviate** | Enterprise | Feature-rich | Complex setup |

## 📊 Chunking Strategies

### Fixed Size
```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
```

### Semantic
```python
# Split by paragraphs, sentences
separators=["\n\n", "\n", ". ", " "]
```

### Document Structure
```python
# Split by sections, headers
# Preserve document hierarchy
```

## 🎓 Memory Management

### Sliding Window
```python
MAX_HISTORY = 10

def add_to_memory(role, message):
    conversation_history.append({"role": role, "message": message})
    if len(conversation_history) > MAX_HISTORY:
        conversation_history.pop(0)  # Remove oldest
```

### Summary-based
```python
if len(conversation_history) > 10:
    # Summarize old messages
    summary = llm.summarize(conversation_history[:8])
    conversation_history = [summary] + conversation_history[8:]
```

## 🚨 Common Issues & Solutions

### Issue 1: Irrelevant Retrieval
```python
# ❌ Too many results
retriever = vectorstore.as_retriever(k=10)

# ✅ Fewer, more relevant
retriever = vectorstore.as_retriever(k=3)

# ✅ Add similarity threshold
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3, "score_threshold": 0.7}
)
```

### Issue 2: Chunks Too Large/Small
```python
# ❌ Too large (loses specificity)
chunk_size=5000

# ❌ Too small (loses context)
chunk_size=100

# ✅ Balanced
chunk_size=1000, chunk_overlap=200
```

### Issue 3: No Context in Answer
```python
# ✅ Explicit instruction
prompt = """
IMPORTANT: You must use ONLY the context provided below.
Do not use your general knowledge.

Context:
{context}

Question: {question}
"""
```

### Issue 4: Memory Overflow
```python
# ✅ Limit history
MAX_TOKENS = 3000
def trim_history(history):
    # Keep only recent messages that fit in token budget
    pass
```

## 🚀 Quick Start: RAG in 10 Lines

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Load, split, embed, store
docs = WebBaseLoader("https://example.com").load()
splits = RecursiveCharacterTextSplitter(chunk_size=1000).split_documents(docs)
vectorstore = Chroma.from_documents(splits, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# Query
context = retriever.invoke("What is X?")
answer = client.responses.create(
    model="gpt-4o-mini",
    input=f"Context: {context}\n\nQuestion: What is X?"
)
```

## 💰 Cost Optimization

### 1. Embeddings
```python
# Use smaller embedding model
OpenAIEmbeddings(model="text-embedding-3-small")  # Cheaper
# vs
OpenAIEmbeddings(model="text-embedding-3-large")  # More expensive
```

### 2. Chunk Size
```python
# Fewer, larger chunks = fewer embeddings
chunk_size=1500  # ~50% fewer embeddings than chunk_size=1000
```

### 3. Retrieval Count
```python
# Retrieve only what's needed
k=3  # vs k=10
```

### 4. Caching
```python
# Cache common queries
query_cache = {}
if query in query_cache:
    return query_cache[query]
```

## 🔍 Evaluation Metrics

```python
# 1. Retrieval Accuracy
relevant_retrieved / total_retrieved

# 2. Answer Quality
- Faithfulness (uses context)
- Relevance (answers question)
- Completeness

# 3. Latency
retrieval_time + generation_time
```

## 💡 Pro Tips
1. **Start simple**: Get basic RAG working first
2. **Test chunks**: Print retrieved chunks to verify relevance
3. **Experiment with k**: Try k=1,3,5 to find sweet spot
4. **Use overlap**: 200-character overlap prevents cutting mid-sentence
5. **Monitor costs**: Track embedding and LLM token usage
6. **Version control**: Keep track of prompt templates
7. **A/B test**: Compare with/without RAG
