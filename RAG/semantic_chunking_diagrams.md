# Semantic Chunking - Mermaid Diagrams for Teaching

## Diagram 1: High-Level Comparison

```mermaid
graph TB
    subgraph "Character-Based Chunking"
        A1[Document] --> B1[Split every N characters]
        B1 --> C1[Chunk 1: 2000 chars]
        B1 --> C2[Chunk 2: 2000 chars]
        B1 --> C3[Chunk 3: 2000 chars]
        style C1 fill:#e1f5ff
        style C2 fill:#e1f5ff
        style C3 fill:#e1f5ff
    end
    
    subgraph "Semantic Chunking"
        A2[Document] --> B2[Split into sentences]
        B2 --> C4[Embed each sentence]
        C4 --> D2[Calculate similarity]
        D2 --> E2[Find topic boundaries]
        E2 --> F1[Chunk 1: History topic]
        E2 --> F2[Chunk 2: Tourism topic]
        E2 --> F3[Chunk 3: Architecture topic]
        style F1 fill:#ffe1e1
        style F2 fill:#ffe1e1
        style F3 fill:#ffe1e1
    end
```

## Diagram 2: Semantic Chunking Process Flow

```mermaid
flowchart TD
    A[📄 Original Document] --> B[Split into Sentences]
    B --> C[Sentence 1<br/>Sentence 2<br/>Sentence 3<br/>...<br/>Sentence N]
    
    C --> D[Generate Embeddings for Each Sentence]
    
    D --> E1[Embedding 1: 0.23, -0.45, 0.67, ...]
    D --> E2[Embedding 2: 0.25, -0.43, 0.69, ...]
    D --> E3[Embedding 3: -0.10, 0.82, -0.34, ...]
    D --> E4[Embedding N: ...]
    
    E1 --> F[Calculate Cosine Similarity<br/>Between Adjacent Sentences]
    E2 --> F
    E3 --> F
    E4 --> F
    
    F --> G[Similarity Scores<br/>S1↔S2: 0.95<br/>S2↔S3: 0.38 ⚠️<br/>S3↔S4: 0.89<br/>...]
    
    G --> H{Find Breakpoints<br/>Low similarity = Topic change}
    
    H --> I[Create Chunks at Breakpoints]
    
    I --> J1[📦 Chunk 1: S1 + S2]
    I --> J2[📦 Chunk 2: S3 + S4 + ...]
    
    style A fill:#f9f9f9
    style F fill:#fff4e1
    style H fill:#ffe1e1
    style J1 fill:#e1ffe1
    style J2 fill:#e1ffe1
```

## Diagram 3: Similarity Detection Process

```mermaid
graph LR
    subgraph "Document Flow"
        S1["Sentence 1:<br/>'Taj Mahal built in 1632'<br/>Topic: History"]
        S2["Sentence 2:<br/>'Shah Jahan commissioned it'<br/>Topic: History"]
        S3["Sentence 3:<br/>'Tourists visit annually'<br/>Topic: Tourism"]
        S4["Sentence 4:<br/>'Made of white marble'<br/>Topic: Architecture"]
    end
    
    S1 -->|Similarity: 0.94<br/>✅ HIGH| S2
    S2 -->|Similarity: 0.38<br/>❌ LOW - SPLIT!| S3
    S3 -->|Similarity: 0.72<br/>✅ MEDIUM| S4
    
    S1 -.->|Chunk 1| C1[Chunk 1:<br/>S1 + S2<br/>History]
    S3 -.->|Chunk 2| C2[Chunk 2:<br/>S3 + S4<br/>Tourism + Arch]
    
    style S1 fill:#e3f2fd
    style S2 fill:#e3f2fd
    style S3 fill:#fff3e0
    style S4 fill:#fff3e0
    style C1 fill:#c8e6c9
    style C2 fill:#ffccbc
```

## Diagram 4: Step-by-Step Algorithm

```mermaid
sequenceDiagram
    participant Doc as Document
    participant Splitter as Sentence Splitter
    participant Embedder as Embedding Model
    participant Analyzer as Similarity Analyzer
    participant Chunker as Chunk Creator
    
    Doc->>Splitter: Full text
    Splitter->>Embedder: [S1, S2, S3, ..., SN]
    
    loop For each sentence
        Embedder->>Embedder: Generate embedding
    end
    
    Embedder->>Analyzer: [E1, E2, E3, ..., EN]
    
    loop For adjacent pairs
        Analyzer->>Analyzer: Calculate cosine similarity
    end
    
    Analyzer->>Analyzer: Find breakpoints<br/>(low similarity scores)
    
    Analyzer->>Chunker: Breakpoint indices
    
    Chunker->>Chunker: Group sentences between breakpoints
    
    Chunker-->>Doc: [Chunk1, Chunk2, Chunk3, ...]
```

## Diagram 5: Cost Comparison

```mermaid
graph TB
    subgraph "Character Chunking Cost"
        D1[10,000 word document] --> S1[Split into ~20 chunks]
        S1 --> E1[Embed 20 chunks]
        E1 --> Cost1[💰 Cost: $0.02]
    end
    
    subgraph "Semantic Chunking Cost"
        D2[10,000 word document] --> S2[Split into ~500 sentences]
        S2 --> E2[Embed 500 sentences]
        E2 --> A2[Calculate 500 similarities]
        A2 --> E3[Embed 25 final chunks]
        E3 --> Cost2[💰 Cost: $0.40]
    end
    
    style Cost1 fill:#c8e6c9
    style Cost2 fill:#ffcdd2
```

## Diagram 6: When to Use Each Method

```mermaid
flowchart TD
    Start{What type of content?}
    
    Start -->|Multi-topic, long-form| Q1{Budget flexible?}
    Start -->|Short, uniform| Char1[Use Character Chunking]
    
    Q1 -->|Yes| Q2{Need high accuracy?}
    Q1 -->|No| Char2[Use Character Chunking]
    
    Q2 -->|Critical use case| Sem1[Use Semantic Chunking]
    Q2 -->|Standard use case| Q3{Try hybrid?}
    
    Q3 -->|Yes| Hybrid[Structure-based + Semantic<br/>for key sections]
    Q3 -->|No| Char3[Use Character Chunking]
    
    style Sem1 fill:#ffe1e1
    style Char1 fill:#e1f5ff
    style Char2 fill:#e1f5ff
    style Char3 fill:#e1f5ff
    style Hybrid fill:#fff4e1
```

## Diagram 7: Breakpoint Detection Methods

```mermaid
graph TD
    A[Similarity Scores:<br/>0.95, 0.93, 0.88, 0.42, 0.85, 0.91] --> B{Choose Method}
    
    B --> C[Percentile Method]
    B --> D[Standard Deviation Method]
    B --> E[Interquartile Range Method]
    
    C --> C1[Calculate 25th percentile<br/>Threshold = 0.50<br/>Split where sim < 0.50]
    
    D --> D1[Calculate mean & std dev<br/>Threshold = mean - 1.5×σ<br/>Split where sim < threshold]
    
    E --> E1[Calculate IQR<br/>Threshold = Q1 - 1.5×IQR<br/>Split where sim < threshold]
    
    C1 --> F[Breakpoints Found]
    D1 --> F
    E1 --> F
    
    F --> G[Create chunks at breakpoints]
    
    style C1 fill:#e1f5ff
    style D1 fill:#ffe1e1
    style E1 fill:#fff4e1
```

## Diagram 8: Real Example Walkthrough

```mermaid
flowchart TB
    subgraph "Original Document"
        direction TB
        T1["The Taj Mahal was built in 1632.<br/>Shah Jahan commissioned it.<br/>Construction took 22 years."]
        T2["Today millions visit annually.<br/>It's a UNESCO World Heritage Site."]
    end
    
    subgraph "Embeddings & Similarity"
        direction TB
        E1[S1: 0.8, 0.2, 0.1] 
        E2[S2: 0.7, 0.3, 0.1]
        E3[S3: 0.9, 0.1, 0.0]
        E4[S4: 0.1, 0.2, 0.9]
        E5[S5: 0.2, 0.3, 0.8]
        
        E1 -.->|0.94| E2
        E2 -.->|0.91| E3
        E3 -.->|0.42 ❌| E4
        E4 -.->|0.88| E5
    end
    
    subgraph "Final Chunks"
        direction TB
        C1["📦 Chunk 1 History:<br/>S1 + S2 + S3"]
        C2["📦 Chunk 2 Tourism:<br/>S4 + S5"]
    end
    
    T1 --> E1
    T1 --> E2
    T1 --> E3
    T2 --> E4
    T2 --> E5
    
    E3 --> C1
    E5 --> C2
    
    style C1 fill:#c8e6c9
    style C2 fill:#ffccbc
    style E3 fill:#ffeb3b
```

## Diagram 9: Threshold Calculation - Math Explained

```mermaid
graph TB
    A["Similarity Scores:<br/>[0.95, 0.93, 0.88, 0.42, 0.85, 0.91, 0.39, 0.87, 0.92]"] --> B{Choose Method}
    
    B --> M1["METHOD 1:<br/>Percentile"]
    B --> M2["METHOD 2:<br/>Standard Deviation"]
    B --> M3["METHOD 3:<br/>Interquartile Range"]
    
    M1 --> C1["Sort: [0.39, 0.42, 0.85, 0.87, 0.88, 0.91, 0.92, 0.93, 0.95]<br/>25th percentile = 0.50<br/>Threshold = 0.50"]
    
    M2 --> C2["Mean μ = 0.79<br/>Std Dev σ = 0.22<br/>Threshold = μ - 1.5×σ<br/>Threshold = 0.79 - 0.33 = 0.46"]
    
    M3 --> C3["Q1 25% = 0.50<br/>Q3 75% = 0.91<br/>IQR = 0.91 - 0.50 = 0.41<br/>Threshold = Q1 - 1.5×IQR<br/>Threshold = 0.50 - 0.62 = -0.11"]
    
    C1 --> R1["Split at: 0.42, 0.39<br/>✂️ 2 breakpoints"]
    C2 --> R2["Split at: 0.42, 0.39<br/>✂️ 2 breakpoints"]
    C3 --> R3["No splits<br/>✂️ 0 breakpoints"]
    
    style M1 fill:#e3f2fd
    style M2 fill:#fff3e0
    style M3 fill:#f3e5f5
    style R1 fill:#c8e6c9
    style R2 fill:#c8e6c9
    style R3 fill:#ffcdd2
```

## Diagram 10: How to Choose Your Threshold Method

```mermaid
flowchart TD
    Start{What's your data like?}
    
    Start -->|Uniform content,<br/>clear sections| P[Use PERCENTILE]
    Start -->|Varied content,<br/>some noise| S[Use STD DEVIATION]
    Start -->|Very noisy,<br/>outliers exist| I[Use IQR]
    
    P --> P1{How many chunks<br/>do you want?}
    P1 -->|Few large chunks| P2["percentile=10<br/>Only biggest gaps"]
    P1 -->|Balanced| P3["percentile=25<br/>DEFAULT"]
    P1 -->|Many small chunks| P4["percentile=50<br/>Split frequently"]
    
    S --> S1{How strict?}
    S1 -->|Conservative| S2["multiplier=2.0<br/>Fewer splits"]
    S1 -->|Balanced| S3["multiplier=1.5<br/>DEFAULT"]
    S1 -->|Aggressive| S4["multiplier=1.0<br/>More splits"]
    
    I --> I1["Usually use default:<br/>multiplier=1.5"]
    
    style P fill:#e1f5ff
    style S fill:#fff4e1
    style I fill:#ffe1f5
    style P3 fill:#90ee90
    style S3 fill:#90ee90
```

## Diagram 11: Real Example with All Three Methods

```mermaid
graph TD
    subgraph "Input Data"
        D["Document with 10 sentences<br/>9 similarity scores:<br/>0.95, 0.93, 0.88, 0.42, 0.85, 0.91, 0.39, 0.87, 0.92"]
    end
    
    D --> A["Percentile 25%<br/>Threshold = 0.50"]
    D --> B["Std Dev 1.5σ<br/>Threshold = 0.46"]
    D --> C["IQR 1.5<br/>Threshold = -0.11"]
    
    A --> A1["Chunks: 3<br/>Sizes: 4, 3, 3 sentences<br/>🎯 RECOMMENDED"]
    B --> B1["Chunks: 3<br/>Sizes: 4, 3, 3 sentences<br/>✅ Good"]
    C --> C1["Chunks: 1<br/>Size: 10 sentences<br/>⚠️ Too conservative"]
    
    style A1 fill:#c8e6c9
    style B1 fill:#fff9c4
    style C1 fill:#ffcdd2
```

---

## Usage Tips for Teaching:

1. **Start with Diagram 1** - Show the conceptual difference
2. **Use Diagram 2** - Walk through the complete process
3. **Show Diagram 3** - Concrete example with actual sentences
4. **Explain with Diagram 7** - How breakpoints are found mathematically
5. **Compare with Diagram 5** - Cost reality check
6. **Conclude with Diagram 6** - When to actually use it

These diagrams can be rendered in:
- Markdown preview in VS Code
- Jupyter notebooks (with mermaid extension)
- Online tools like mermaid.live
- Documentation sites (GitHub, GitLab, etc.)
