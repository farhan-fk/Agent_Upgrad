# OpenAI File Search - Visual Explanation

## 🎯 KEY ARCHITECTURAL INSIGHT

**OpenAI File Search is AGENTIC, not a simple retrieval pipeline!**

```
Traditional RAG:  User Query → Always search vector DB → Return chunks → LLM generates

OpenAI File Search:  User Query → LLM Agent decides → [Use file_search tool? Yes/No] 
                                                        ↓                    ↓
                                            Search vector DB          Use own knowledge
                                                        ↓                    ↓
                                                  Generate answer with citations
```

**From OpenAI Docs:**
> "Once the `file_search` tool is enabled, **the model decides when to retrieve content** based on user messages."

This means:
- ✅ The LLM is the orchestrator/agent
- ✅ Query goes to LLM **first**, not directly to vector store
- ✅ LLM intelligently decides whether to use the file_search tool
- ✅ Can combine document knowledge + training knowledge
- ✅ More efficient - doesn't retrieve unnecessarily

---

## Diagram 1: High-Level User Experience (What You See)

```mermaid
graph TB
    Start([👤 User Starts]) --> Step1[📤 Upload PDF/Document]
    
    Step1 --> Step2[🗄️ Create Vector Store]
    
    Step2 --> Magic[✨ OpenAI Magic Box<br/>Processing...]
    
    Magic --> Step3[❓ Ask Question]
    
    Step3 --> Step4[🤖 Get Answer with Citations]
    
    Step4 --> Decision{More Questions?}
    
    Decision -->|Yes| Step3
    Decision -->|No| End([✅ Done])
    
    style Start fill:#e1f5ff
    style Magic fill:#fff4e1,stroke:#ff9800,stroke-width:3px
    style Step4 fill:#c8e6c9
    style End fill:#e1f5ff
    
    subgraph "Your Code (3 Lines)"
        Step1
        Step2
        Step3
    end
    
    subgraph "OpenAI Handles Everything"
        Magic
        Step4
    end
```

---

## Diagram 1B: The Agentic Flow (How It Really Works)

```mermaid
flowchart TD
    User([👤 User Query:<br/>'What is the refund policy?']) --> LLM[🤖 LLM Agent<br/>GPT-4/GPT-5]
    
    LLM --> Decision{🤔 LLM Decides:<br/>Do I need to search<br/>the documents?}
    
    Decision -->|"Yes, I need<br/>document info"| Tool[🔧 Call file_search tool]
    Decision -->|"No, I know this<br/>from training"| Direct[Generate answer<br/>from own knowledge]
    
    Tool --> Embed[Embed query]
    Embed --> VectorSearch[🔍 Search Vector Store]
    VectorSearch --> Retrieve[📚 Retrieve relevant chunks]
    Retrieve --> BackToLLM[Return to LLM with context]
    
    BackToLLM --> Generate[🤖 LLM generates answer<br/>using retrieved context]
    Direct --> Answer([✅ Final Answer])
    Generate --> Answer
    
    style User fill:#e3f2fd
    style LLM fill:#fff9c4,stroke:#f57c00,stroke-width:3px
    style Decision fill:#ffccbc,stroke:#ff5722,stroke-width:2px
    style Tool fill:#f3e5f5
    style VectorSearch fill:#e1f5ff
    style Generate fill:#c8e6c9
    style Answer fill:#a5d6a7,stroke:#4caf50,stroke-width:3px
    
    Note1[🎯 KEY INSIGHT:<br/>LLM is the orchestrator!<br/>It decides when to use RAG]
    
    style Note1 fill:#fff3e0,stroke:#ff9800,stroke-width:2px
```

---

## Diagram 1C: Agentic Decision Examples

```mermaid
graph TB
    subgraph Example1["📝 Example 1: Document-Specific Question"]
        Q1["User: 'What is the refund policy<br/>in the contract?'"]
        LLM1[🤖 LLM thinks:<br/>'This needs document info']
        A1[✅ Uses file_search tool]
        R1[Returns: 'Refunds within 30 days [0]']
        Q1 --> LLM1 --> A1 --> R1
    end
    
    subgraph Example2["🌍 Example 2: General Knowledge Question"]
        Q2["User: 'What is the capital<br/>of France?'"]
        LLM2[🤖 LLM thinks:<br/>'I know this from training']
        A2[❌ Skips file_search tool]
        R2[Returns: 'Paris']
        Q2 --> LLM2 --> A2 --> R2
    end
    
    subgraph Example3["🔀 Example 3: Hybrid Question"]
        Q3["User: 'How does our refund policy<br/>compare to industry standards?'"]
        LLM3[🤖 LLM thinks:<br/>'Need both document + knowledge']
        A3[✅ Uses file_search for company policy<br/>+ Uses own knowledge for industry info]
        R3[Returns: 'Your policy: 30 days [0]<br/>Industry average: 14-30 days']
        Q3 --> LLM3 --> A3 --> R3
    end
    
    style Q1 fill:#e3f2fd
    style Q2 fill:#e3f2fd
    style Q3 fill:#e3f2fd
    style LLM1 fill:#fff9c4
    style LLM2 fill:#fff9c4
    style LLM3 fill:#fff9c4
    style A1 fill:#c8e6c9
    style A2 fill:#ffcdd2
    style A3 fill:#b2dfdb
    style R1 fill:#a5d6a7
    style R2 fill:#a5d6a7
    style R3 fill:#a5d6a7
```

**Key Point:** The LLM acts as an intelligent agent, not a simple retrieval system!

---

## Diagram 2: Behind The Scenes (The Abstracted Magic)

```mermaid
flowchart TD
    Start([📄 Document Upload]) --> Parse
    
    subgraph Parse["🔍 STEP 1: Document Parsing"]
        P1[Extract Text from PDF/DOCX/MD]
        P2[Handle Multiple Encodings<br/>UTF-8, UTF-16, ASCII]
        P3[Parse Complex Layouts]
        P1 --> P2 --> P3
    end
    
    Parse --> Chunk
    
    subgraph Chunk["✂️ STEP 2: Text Chunking"]
        C1[Split into 800-token chunks]
        C2[Add 400-token overlap<br/>between chunks]
        C3[Smart boundary detection<br/>Avoid splitting sentences]
        C1 --> C2 --> C3
    end
    
    Chunk --> Embed
    
    subgraph Embed["🧠 STEP 3: Embedding Generation"]
        E1[Use text-embedding-3-large]
        E2[Generate 256-dimensional vectors<br/>for each chunk]
        E3[Store embeddings in<br/>vector database]
        E1 --> E2 --> E3
    end
    
    Embed --> Store
    
    subgraph Store["💾 STEP 4: Vector Storage & Indexing"]
        S1[Create dual indexes:<br/>• Vector index semantic<br/>• Keyword index BM25]
        S2[Support up to 10,000 files<br/>5M tokens per file]
        S1 --> S2
    end
    
    Store --> Ready[📦 Vector Store Ready]
    
    Ready --> Query([❓ User Query])
    
    Query --> AgentLLM[🤖 LLM Agent Receives Query]
    
    AgentLLM --> AgentDecision{🤔 Should I search<br/>the documents?}
    
    AgentDecision -->|Yes| Process
    AgentDecision -->|No| DirectAnswer[Generate from<br/>own knowledge]
    
    subgraph Process["🔄 STEP 5: Query Processing"]
        Q1[Rewrite query for<br/>optimal search]
        Q2[Break complex queries<br/>into sub-queries]
        Q3[Run parallel searches]
        Q1 --> Q2 --> Q3
    end
    
    Process --> Search
    
    subgraph Search["🔍 STEP 6: Hybrid Search"]
        H1[Semantic Search<br/>embedding similarity]
        H2[Keyword Search<br/>exact text matching]
        H3[Search both Assistant<br/>& Thread vector stores]
        H1 --> H3
        H2 --> H3
    end
    
    Search --> Rank
    
    subgraph Rank["🎯 STEP 7: Re-ranking"]
        R1[Combine results using<br/>Reciprocal Rank Fusion]
        R2[Apply score threshold<br/>default: 0.0]
        R3[Select top 20 chunks<br/>within 16K token budget]
        R1 --> R2 --> R3
    end
    
    Rank --> Inject
    
    subgraph Inject["📝 STEP 8: Context Injection"]
        I1[Format retrieved chunks]
        I2[Add citation markers]
        I3[Build prompt with context]
        I1 --> I2 --> I3
    end
    
    Inject --> Generate
    
    subgraph Generate["🤖 STEP 9: LLM Generation with Context"]
        G1[GPT-4/GPT-5 processes<br/>query + retrieved context]
        G2[Generate answer with<br/>inline citations]
        G3[Link citations to<br/>source files]
        G1 --> G2 --> G3
    end
    
    DirectAnswer --> Output([✅ Answer Delivered])
    Generate --> Output
    
    style Parse fill:#ffe1e1
    style Chunk fill:#fff4e1
    style Embed fill:#e1f5ff
    style Store fill:#f3e5f5
    style AgentLLM fill:#fff9c4,stroke:#f57c00,stroke-width:3px
    style AgentDecision fill:#ffccbc,stroke:#ff5722,stroke-width:3px
    style Process fill:#e8f5e9
    style Search fill:#fff3e0
    style Rank fill:#fce4ec
    style Inject fill:#e0f2f1
    style Generate fill:#f3e5f5
    style DirectAnswer fill:#e1bee7
    style Ready fill:#c8e6c9,stroke:#4caf50,stroke-width:3px
    style Output fill:#c8e6c9,stroke:#4caf50,stroke-width:3px
```

---

## 🤖 Agentic vs Traditional RAG Comparison

| Aspect | Traditional RAG | OpenAI File Search (Agentic) |
|--------|----------------|------------------------------|
| **Query Flow** | User → Vector Search → LLM | User → **LLM Agent** → [Decides] → Vector Search or Direct |
| **Search Trigger** | Every query searches | **LLM decides** if search is needed |
| **General Questions** | Wastes time searching docs | LLM answers directly from knowledge |
| **Document Questions** | Retrieves relevant chunks | LLM triggers file_search tool |
| **Hybrid Questions** | Hard to implement | LLM combines both sources naturally |
| **Efficiency** | Always pays retrieval cost | Only retrieves when necessary |
| **Example: "What is AI?"** | Searches docs unnecessarily | LLM answers directly |
| **Example: "What's in section 3?"** | Searches and returns | LLM triggers search, returns with citations |
| **Intelligence** | Fixed pipeline | **Adaptive decision-making** |

**Why This Matters:**
- 💰 **Cost savings**: Avoids unnecessary vector searches
- ⚡ **Faster responses**: Direct answers for general questions
- 🎯 **Better UX**: Seamlessly blends document knowledge with training knowledge
- 🧠 **More intelligent**: LLM acts as reasoning layer, not just generator

---

## Diagram 2B: How Tool Calling Makes It Agentic

```mermaid
sequenceDiagram
    participant User
    participant LLM as LLM Agent<br/>(GPT-4/GPT-5)
    participant Tools as Available Tools<br/>[file_search]
    participant VectorDB as Vector Store
    
    User->>LLM: "What's the refund policy?"
    
    Note over LLM: LLM analyzes query:<br/>"This needs document info"
    
    LLM->>Tools: Call file_search tool<br/>with query
    
    Tools->>VectorDB: Search for "refund policy"
    VectorDB-->>Tools: Return top 20 chunks
    
    Tools-->>LLM: Here's the context
    
    Note over LLM: LLM generates answer<br/>using retrieved context
    
    LLM-->>User: "Refunds available within 30 days [0]"
    
    rect rgb(255, 243, 224)
    Note over User,VectorDB: Scenario 2: General Question
    end
    
    User->>LLM: "What is the capital of France?"
    
    Note over LLM: LLM analyzes query:<br/>"I know this from training"
    
    Note over LLM: Skips file_search tool
    
    LLM-->>User: "Paris"
    
    style LLM fill:#fff9c4,stroke:#f57c00,stroke-width:3px
    style Tools fill:#f3e5f5
```

**How Tool Calling Works:**

1. You register the `file_search` tool when creating the assistant
2. For each user query, the LLM receives:
   - The user's question
   - List of available tools: `[{"type": "file_search"}]`
3. LLM decides: "Do I need to call this tool?"
4. If yes → Makes a tool call → Gets results → Generates answer
5. If no → Generates answer directly

This is the same mechanism used for function calling, but optimized for RAG!

---

## 📘 Complete RAG Flow - Single Comprehensive Diagram

```mermaid
flowchart TD
    %% Initial Setup
    Docs[📄 Documents<br/>PDFs, DOCX, etc.] --> Parse[Parse & Extract Text]
    Parse --> Chunk[Split into Chunks<br/>800 tokens, 400 overlap]
    Chunk --> EmbedDocs[Embedding Model<br/>text-embedding-3-large]
    EmbedDocs --> VectorStore[(💾 Vector Store<br/>Vector Database<br/>Stores: Embeddings + Metadata)]
    
    %% User Query Flow
    User([👤 User Query:<br/>'What is the refund policy?']) --> LLM{🤖 LLM Agent<br/>GPT-4/GPT-5<br/><br/>Decision Time!}
    
    %% Path 1: Use Own Knowledge
    LLM -->|🚫 Don't need docs<br/>General question| OwnKnowledge[Use Training Knowledge]
    OwnKnowledge --> DirectAnswer[📝 Generate Answer<br/>from own knowledge]
    DirectAnswer --> FinalOutput([✅ Final Answer to User])
    
    %% Path 2: Search Vector Store
    LLM -->|✅ Need document info<br/>Specific to uploaded docs| NeedSearch[Search Required]
    
    NeedSearch --> EmbedQuery[🧠 Embed User Query<br/>Same embedding model<br/>→ Query Vector]
    
    EmbedQuery --> VectorSearch[🔍 Vector Similarity Search<br/>Compare query vector with<br/>document chunk vectors]
    
    VectorSearch --> VectorStore
    
    VectorStore --> TopChunks[📊 Retrieve Top K Chunks<br/>Most similar by cosine distance<br/>e.g., Top 20 chunks]
    
    TopChunks --> Rerank[🎯 Re-rank Results<br/>Hybrid: Semantic + Keyword<br/>Score threshold filtering]
    
    Rerank --> Context[📚 Retrieved Context:<br/>Chunk 1: 'Refunds within 30 days...'<br/>Chunk 2: 'Contact support...'<br/>Chunk 3: ...]
    
    Context --> AugmentedPrompt["🔧 Build Augmented Prompt:<br/>━━━━━━━━━━━━━━━━<br/>Context: [chunks]<br/>━━━━━━━━━━━━━━━━<br/>Question: [user query]<br/>━━━━━━━━━━━━━━━━<br/>Answer based on context:"]
    
    AugmentedPrompt --> LLMGenerate[🤖 LLM Generates Answer<br/>Using retrieved context<br/>+ Add citations]
    
    LLMGenerate --> FinalOutput
    
    %% Styling
    style User fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style LLM fill:#fff9c4,stroke:#f57c00,stroke-width:4px
    style VectorStore fill:#e1f5ff,stroke:#0288d1,stroke-width:3px
    style EmbedQuery fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style VectorSearch fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style Context fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style AugmentedPrompt fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    style LLMGenerate fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style FinalOutput fill:#a5d6a7,stroke:#1b5e20,stroke-width:3px
    style OwnKnowledge fill:#e1bee7,stroke:#8e24aa,stroke-width:2px
    style DirectAnswer fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px
    
    %% Annotations
    Note1[💡 KEY POINTS:<br/>1. LLM decides the path<br/>2. Query embedding uses SAME model as docs<br/>3. Vector search finds semantic similarity<br/>4. Context is injected into prompt<br/>5. LLM generates augmented response]
    
    style Note1 fill:#ffeb3b,stroke:#f57c00,stroke-width:2px
```

**Step-by-Step Explanation:**

### 📥 **Setup Phase (Before Query):**
1. **Documents** → Parsed and chunked into 800-token pieces
2. **Chunks** → Converted to vectors via embedding model
3. **Vectors** → Stored in vector database with metadata

### ❓ **Query Phase (User Asks):**
1. **User Query** → Goes to LLM Agent first
2. **LLM Decision** → "Do I need to search documents?"
   - **NO** → Use own training knowledge (Path 1)
   - **YES** → Search vector store (Path 2)

### 🔍 **Path 2: RAG Search Flow:**
1. **Embed Query** → Convert user question to vector (same model!)
2. **Vector Search** → Find most similar chunk vectors (cosine similarity)
3. **Retrieve Top-K** → Get 20 most relevant chunks
4. **Re-rank** → Apply hybrid scoring (semantic + keyword)
5. **Build Prompt** → Inject context + original query
6. **LLM Generates** → Answer using context + citations
7. **Return to User** → Final answer with sources

---

## Diagram 3: Simplified Side-by-Side Comparison

```mermaid
graph LR
    subgraph UserView["👤 What You Do"]
        U1[Upload File]
        U2[Ask Question]
        U3[Get Answer]
        U1 --> U2 --> U3
    end
    
    subgraph OpenAIView["✨ What OpenAI Does"]
        O1[Parse Document]
        O2[Chunk Text]
        O3[Generate Embeddings]
        O4[Index Vectors]
        O5[Optimize Query]
        O6[Hybrid Search]
        O7[Re-rank Results]
        O8[Inject Context]
        O9[Generate with LLM]
        
        O1 --> O2 --> O3 --> O4 --> O5 --> O6 --> O7 --> O8 --> O9
    end
    
    U1 -.->|3 lines of code| O1
    U2 -.->|triggers| O5
    O9 -.->|returns| U3
    
    style UserView fill:#e3f2fd
    style OpenAIView fill:#fff3e0
```

---

## Diagram 4: Technical Architecture Deep Dive

```mermaid
graph TB
    Doc[📄 Your Document<br/>contract.pdf]
    
    Doc --> API[OpenAI API]
    
    API --> Parser[Document Parser]
    
    Parser --> Chunker[Text Chunker<br/>800 tokens<br/>400 overlap]
    
    Chunker --> Chunks["Chunk 1<br/>Chunk 2<br/>...<br/>Chunk N"]
    
    Chunks --> EmbedModel[text-embedding-3-large<br/>256 dimensions]
    
    EmbedModel --> Vectors["Vector 1: [0.23, -0.45, ..., 0.67]<br/>Vector 2: [0.25, -0.43, ..., 0.69]<br/>...<br/>Vector N: [...]"]
    
    Vectors --> VectorDB[Vector Database<br/>Managed by OpenAI]
    
    VectorDB --> Index1[Semantic Index<br/>ANN Search]
    VectorDB --> Index2[Keyword Index<br/>BM25 Search]
    
    Query[❓ User Query:<br/>'What is the refund policy?'] --> QueryOpt[Query Optimizer]
    
    QueryOpt --> Index1
    QueryOpt --> Index2
    
    Index1 --> SemResults[Semantic Results<br/>Score: 0.92, 0.88, ...]
    Index2 --> KeyResults[Keyword Results<br/>Score: 0.95, 0.76, ...]
    
    SemResults --> RRF[Reciprocal Rank Fusion]
    KeyResults --> RRF
    
    RRF --> TopK[Top 20 Chunks<br/>within 16K token budget]
    
    TopK --> Prompt["Prompt Template:<br/>Context: chunk1, chunk2, ...<br/>Question: refund policy<br/>Answer:"]
    
    Prompt --> LLM[GPT-4o / GPT-5]
    
    LLM --> Answer[✅ Answer:<br/>'Refunds available within 30 days [0]'<br/>---<br/>[0] contract.pdf]
    
    style Doc fill:#e3f2fd
    style Parser fill:#ffe1e1
    style Chunker fill:#fff4e1
    style EmbedModel fill:#e1f5ff
    style VectorDB fill:#f3e5f5,stroke:#9c27b0,stroke-width:3px
    style RRF fill:#fce4ec
    style LLM fill:#c8e6c9
    style Answer fill:#a5d6a7,stroke:#4caf50,stroke-width:3px
```

---

## Diagram 5: Manual RAG vs OpenAI File Search

```mermaid
graph TB
    subgraph Manual["🔧 Manual RAG Implementation"]
        M1[Choose PDF library<br/>PyPDF2, pdfplumber]
        M2[Write parsing logic<br/>Handle errors]
        M3[Implement chunking<br/>RecursiveCharacterTextSplitter]
        M4[Call Embeddings API<br/>Manage API keys]
        M5[Setup Vector DB<br/>Pinecone, Chroma, Weaviate]
        M6[Write search logic<br/>Similarity + filtering]
        M7[Implement re-ranking<br/>Cohere, custom logic]
        M8[Build prompt template<br/>Context formatting]
        M9[Call LLM<br/>Parse response]
        M10[Add citations manually<br/>Track sources]
        
        M1-->M2-->M3-->M4-->M5-->M6-->M7-->M8-->M9-->M10
        
        Cost1[💰 Cost:<br/>- Infrastructure<br/>- DB hosting<br/>- Development time<br/>- Maintenance]
    end
    
    subgraph FileSearch["✨ OpenAI File Search"]
        F1[upload_document]
        F2[create_vector_store]
        F3[ask_question]
        
        F1-->F2-->F3
        
        Cost2[💰 Cost:<br/>- $0.10/GB/day<br/>- First 1GB free<br/>- Zero maintenance]
    end
    
    M10 --> Result1[100+ lines of code<br/>Weeks of development]
    F3 --> Result2[3 lines of code<br/>5 minutes setup]
    
    style Manual fill:#ffebee
    style FileSearch fill:#e8f5e9
    style Result1 fill:#ffcdd2
    style Result2 fill:#c8e6c9
```

---

## Diagram 6: Data Flow with Token Budgets

```mermaid
sequenceDiagram
    participant User
    participant API as OpenAI API
    participant Parser
    participant Chunker
    participant Embedder as Embedding Model
    participant VectorDB as Vector DB
    participant Search
    participant Ranker
    participant LLM
    
    User->>API: Upload contract.pdf (5000 tokens)
    API->>Parser: Parse document
    Parser->>Chunker: Extract text
    
    Note over Chunker: Split into chunks<br/>800 tokens each<br/>400 overlap
    
    Chunker->>Embedder: Chunk 1, 2, 3, ..., N
    
    loop For each chunk
        Embedder->>Embedder: Generate 256-dim vector
    end
    
    Embedder->>VectorDB: Store N vectors + metadata
    VectorDB-->>User: ✅ Ready (async)
    
    User->>API: "What is the refund policy?"
    API->>Search: Optimized query
    
    par Parallel Search
        Search->>VectorDB: Semantic search
        Search->>VectorDB: Keyword search
    end
    
    VectorDB-->>Search: 50 candidate chunks
    Search->>Ranker: Re-rank candidates
    
    Note over Ranker: Apply RRF<br/>Score threshold<br/>Token budget: 16K
    
    Ranker->>LLM: Top 20 chunks (12,000 tokens)
    
    Note over LLM: Context + Query<br/>Total: ~13,000 tokens
    
    LLM->>LLM: Generate answer
    LLM-->>User: Answer + Citations
    
    Note over User: Response: 500 tokens<br/>Total: 13,500 tokens used
```

---

## Diagram 7: Key Abstraction Layers

```mermaid
graph TD
    L1[Layer 1: Your Code]
    L2[Layer 2: OpenAI SDK]
    L3[Layer 3: File Processing]
    L4[Layer 4: RAG Pipeline]
    L5[Layer 5: Infrastructure]
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5
    
    L1 -.->|"create_vector_store()<br/>upload_document()<br/>ask_question()"| Hide1
    
    L3 -.->|"PDF parsing<br/>Text extraction<br/>Format handling"| Hide2
    
    L4 -.->|"Chunking<br/>Embedding<br/>Indexing<br/>Searching<br/>Re-ranking"| Hide3
    
    L5 -.->|"Vector database<br/>API scaling<br/>Storage management<br/>Load balancing"| Hide4
    
    Hide1["✅ You control"]
    Hide2["🔒 Abstracted"]
    Hide3["🔒 Abstracted"]
    Hide4["🔒 Abstracted"]
    
    style L1 fill:#c8e6c9,stroke:#4caf50,stroke-width:3px
    style L2 fill:#e1f5ff
    style L3 fill:#fff4e1
    style L4 fill:#ffe1e1
    style L5 fill:#f3e5f5
    style Hide1 fill:#a5d6a7
    style Hide2 fill:#ffccbc
    style Hide3 fill:#ffccbc
    style Hide4 fill:#ffccbc
```

---

## Quick Reference: The 9 Abstracted Steps

| Step | What Happens | You See It? | Configurable? |
|------|--------------|-------------|---------------|
| 1. **Document Parsing** | Extract text from PDF/DOCX/MD | ❌ No | ❌ No |
| 2. **Text Chunking** | Split into 800-token chunks, 400 overlap | ❌ No | ✅ Yes (100-4096 tokens) |
| 3. **Embedding Generation** | text-embedding-3-large @ 256d | ❌ No | ❌ No |
| 4. **Vector Storage** | Store in managed vector DB | ❌ No | ❌ No |
| 5. **Query Optimization** | Rewrite & break down queries | ❌ No | ❌ No |
| 6. **Hybrid Search** | Semantic + Keyword search | ❌ No | ⚠️ Partial (weights) |
| 7. **Re-ranking** | RRF, score threshold, top-K | ❌ No | ✅ Yes (max_num_results) |
| 8. **Context Injection** | Format prompt with chunks | ❌ No | ❌ No |
| 9. **LLM Generation** | Generate answer with citations | ✅ Yes | ⚠️ Partial (model choice) |

---

## Cost Breakdown Visual

```mermaid
pie title OpenAI File Search Cost Distribution
    "Storage (10GB @ $0.10/GB/day)" : 1000
    "Embedding Generation" : 0
    "Vector DB Operations" : 0
    "Search & Retrieval" : 0
    "LLM Token Usage (only normal rates)" : 500
```

**Key Insight:** Most RAG operations are FREE - you only pay for storage and normal LLM token usage!

---

## Performance Characteristics

```mermaid
graph LR
    subgraph Latency["⏱️ Typical Latency"]
        direction TB
        A1[Document Upload: 5-30 sec]
        A2[Indexing: Background async]
        A3[Query: 2-5 sec]
        A1 --> A2 --> A3
    end
    
    subgraph Limits["📊 Scale Limits"]
        direction TB
        B1[Files per store: 10,000]
        B2[Tokens per file: 5M]
        B3[File size: 512 MB]
        B4[Vector stores: Unlimited]
        B1 --> B2 --> B3 --> B4
    end
    
    subgraph Quality["✨ Quality Factors"]
        direction TB
        C1[Chunk Quality: High]
        C2[Search Accuracy: 85-95%]
        C3[Citation Accuracy: High]
        C4[Hallucination Risk: Low]
        C1 --> C2 --> C3 --> C4
    end
    
    style Latency fill:#e1f5ff
    style Limits fill:#fff4e1
    style Quality fill:#e8f5e9
```
