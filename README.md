# 🤖 Generative AI with OpenAI SDK - Complete Learning Guide

> A structured, hands-on course teaching Generative AI fundamentals using OpenAI's API

---

## 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Course Overview](#-course-overview)
3. [Learning Objectives](#-learning-objectives)
4. [Course Structure](#-course-structure)
5. [Getting Started](#-getting-started)
6. [Detailed Curriculum](#-detailed-curriculum)
7. [Project Files](#-project-files)
8. [Additional Resources](#-additional-resources)

---

## 🛠️ Prerequisites

### Required Software & Accounts

| Requirement | Description | Download Link |
|-------------|-------------|---------------|
| **Python 3.8+** | Programming language for AI development | [Download Python](https://www.python.org/downloads/) |
| **Visual Studio Code** | Code editor with AI extensions | [Download VS Code](https://code.visualstudio.com/download) |
| **Git** | Version control system | [Download Git](https://git-scm.com/downloads) |
| **GitHub Account** | For version control and Copilot access | [Create Account](https://github.com/signup) |
| **OpenAI API Key** | Access to OpenAI models | [Get API Key](https://platform.openai.com/api-keys) |

### Required VS Code Extensions

Install these extensions in Visual Studio Code:

1. **Python** (Microsoft) - `ms-python.python`
   - Provides Python language support, debugging, and IntelliSense

2. **GitHub Copilot** - `GitHub.copilot`
   - AI-powered code completion assistant
   - Requires GitHub Copilot subscription

3. **GitHub Copilot Chat** - `GitHub.copilot-chat`
   - Conversational AI assistant in VS Code

4. **Jupyter** (Microsoft) - `ms-toolsai.jupyter`
   - For running and editing Jupyter notebooks

5. **Pylance** (Microsoft) - `ms-python.vscode-pylance`
   - Fast Python language server

### Installation Steps

```bash
# 1. Install Python packages
pip install openai
pip install python-dotenv
pip install requests
pip install beautifulsoup4

# 2. Clone this repository
git clone <your-repo-url>
cd Openai_Sdk

# 3. Create .env file
# Add your OpenAI API key:
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 4. Verify installation
python --version
pip list
```

---

## 🎯 Course Overview

This course provides a **comprehensive, structured introduction to Generative AI** using OpenAI's SDK. Students will learn how to:

- Connect to and use various AI models
- Understand pricing and model selection strategies
- Work with different API endpoints (text, audio, images, reasoning)
- Implement memory and context management
- Build real-world AI applications
- Use advanced features like web search, code interpretation, and MCP

**Teaching Approach:** Progressive complexity - from basic API connections to advanced reasoning models

---

## 🎓 Learning Objectives

By the end of this course, students will be able to:

✅ Select appropriate AI models based on use case and budget  
✅ Make effective API calls to text, audio, and image generation endpoints  
✅ Implement stateless and stateful (memory-based) chatbots  
✅ Integrate web search capabilities into AI applications  
✅ Work with advanced reasoning models (o1, o3-mini)  
✅ Use code interpretation and execution features  
✅ Understand and implement Model Context Protocol (MCP)  
✅ Build production-ready AI applications  

---

## 📚 Course Structure

### Phase 1: Foundations (Lessons 1-3)
**Focus:** Understanding models, API basics, and conversation patterns

### Phase 2: Multimodal AI (Lessons 4-5)
**Focus:** Audio and image generation capabilities

### Phase 3: Advanced Integration (Lessons 6-9)
**Focus:** Web search, tool use, and Model Context Protocol

### Phase 4: Advanced Reasoning (Lessons 10-13)
**Focus:** Code interpretation and reasoning models

---

## 🚀 Getting Started

### Step 1: Environment Setup

Create a `.env` file in your project root:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### Step 2: Basic Connection Test

Run the first script to verify your setup:

```bash
python Connecting_llm_one.py
```

### Step 3: Explore Examples

Work through the examples in order, starting with `Connecting_llm_one.py` and progressing through the numbered files.

---

## 📖 Detailed Curriculum

### **Lesson 1: Understanding AI Models & API Connection**
**File:** `Connecting_llm_one.py` | `01_Connecting_LLM.ipynb`

**Topics Covered:**
- What are Large Language Models (LLMs)?
- OpenAI model family overview:
  - GPT-4o (Advanced multimodal)
  - GPT-4o-mini (Cost-effective)
  - GPT-4-turbo (Previous generation)
  - o1, o3-mini (Reasoning models)
- Understanding model pricing
- Model selection criteria:
  - Cost vs. performance
  - Speed vs. quality
  - Use case alignment
- Setting up OpenAI client
- Making your first API call
- Understanding parameters:
  - `temperature` (creativity control)
  - `max_output_tokens` (response length)
  - `instructions` (system prompts)

**Key Concepts:**
```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

response = client.responses.create(
    model="gpt-4o-mini",
    input="Your prompt here",
    temperature=0.7,
    max_output_tokens=500
)
```

**Learning Outcomes:**
- Understand different model capabilities and pricing
- Successfully connect to OpenAI API
- Generate basic text responses

---

### **Lesson 2: Stateless Chatbot (No Memory)**
**File:** `no_memory_chatbot_two.py` | `02_No_Memory_Chatbot.ipynb`

**Topics Covered:**
- What is a stateless conversation?
- Request-response architecture
- Limitations of no-memory systems
- Use cases for stateless bots:
  - FAQs
  - One-shot queries
  - Independent tasks

**Key Concepts:**
- Each request is independent
- No conversation history retained
- Lower cost per interaction
- Simpler implementation

**Learning Outcomes:**
- Build a basic chatbot without memory
- Understand when stateless design is appropriate

---

### **Lesson 3: Memory-Based Chatbot (Conversational AI)**
**File:** `memory_chatbot_three.py` | `03_Memory_Chatbot.ipynb`

**Topics Covered:**
- Importance of conversation history
- Implementing message arrays
- Role-based messaging:
  - `system` - Instructions for the AI
  - `user` - User messages
  - `assistant` - AI responses
- Managing context windows
- Token optimization strategies
- When to truncate history

**Key Concepts:**
```python
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "What's my name?"} # Can reference context
]
```

**Learning Outcomes:**
- Implement conversational memory
- Manage conversation context effectively
- Build more natural chatbot experiences

---

### **Lesson 4: Audio Generation (Text-to-Speech)**
**File:** `audio_four.py` | `04_Audio_Generation.ipynb`

**Topics Covered:**
- Text-to-Speech (TTS) API overview
- Available voice models:
  - `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
- Audio quality options (tts-1 vs tts-1-hd)
- Output formats (MP3, AAC, FLAC, WAV, PCM)
- Streaming audio responses
- Use cases:
  - Accessibility features
  - Content creation
  - Voice assistants

**Key Concepts:**
```python
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello! This is a text-to-speech demo."
)
response.stream_to_file("output.mp3")
```

**Learning Outcomes:**
- Generate audio from text
- Select appropriate voices for use cases
- Save and stream audio files

---

### **Lesson 5: Image Generation (DALL-E)**
**File:** `image_five.py` | `05_Image_Generation.ipynb`

**Topics Covered:**
- DALL-E 3 capabilities
- Prompt engineering for images
- Image parameters:
  - Size options (1024x1024, 1024x1792, 1792x1024)
  - Quality (standard vs HD)
  - Style (natural vs vivid)
- Image editing and variations
- Cost considerations
- Best practices for prompts

**Key Concepts:**
```python
response = client.images.generate(
    model="dall-e-3",
    prompt="A professional photo of a futuristic city at sunset",
    size="1024x1024",
    quality="hd",
    n=1
)
image_url = response.data[0].url
```

**Learning Outcomes:**
- Generate images from text descriptions
- Craft effective image prompts
- Understand image generation pricing

---

### **Lesson 6: Web Search Integration (Basic)**
**File:** `web_search_six.py` | `06_Web_Search.ipynb`

**Topics Covered:**
- Introduction to tool use in OpenAI API
- Web search tool capabilities
- Real-time information retrieval
- Combining LLM reasoning with current data
- Understanding tool responses
- Error handling

**Key Concepts:**
```python
response = client.responses.create(
    model="gpt-4o-mini",
    tools=[{"type": "web_search"}],
    input="What are the latest developments in AI?"
)
```

**Learning Outcomes:**
- Enable web search in AI applications
- Process and present search results
- Combine static knowledge with real-time data

---

### **Lesson 7: Web Search Project (Advanced)**
**File:** `web_search_project_seven.py` | `07_Web_Search_Project.ipynb`

**Topics Covered:**
- Building a complete web-search application
- Multi-step reasoning with search
- Formatting and presenting results
- Citation and source tracking
- Building research assistants
- Practical applications

**Learning Outcomes:**
- Build a production-ready search application
- Implement complex query workflows
- Present information professionally

---

### **Lesson 8: Model Context Protocol (MCP) Introduction**
**File:** `mcp_eight.py` | `08_MCP_GitHub.ipynb`

**Topics Covered:**
- What is Model Context Protocol?
- MCP architecture and benefits
- Setting up MCP servers
- GitHub MCP integration
- Reading repository data
- Automating GitHub workflows

**Key Concepts:**
- MCP provides standard way to connect AI to data sources
- Enables AI to access external tools and APIs
- GitHub example: read/write repos, issues, PRs

**Learning Outcomes:**
- Understand MCP architecture
- Connect AI to GitHub via MCP
- Automate repository interactions

---

### **Lesson 9: MCP Code Audit Exercise**
**File:** `mcp_exercise_nine.py` | `09_MCP_Code_Audit.ipynb`

**Topics Covered:**
- Practical MCP application
- Automated code review
- Security scanning
- Best practice checking
- Report generation
- Integration with CI/CD

**Learning Outcomes:**
- Build code audit tools with MCP
- Automate code quality checks
- Generate actionable reports

---

### **Lesson 10: Code Interpreter**
**File:** `gpt_code_interpretor_ten.py` | `10_Code_Interpreter.ipynb`

**Topics Covered:**
- Code interpreter tool overview
- Executing Python code in sandbox
- Data analysis capabilities
- File upload and processing
- Visualization generation
- Mathematical computations
- Container types (auto, hermetic, remote)

**Key Concepts:**
```python
response = client.responses.create(
    model="gpt-4o-mini",
    tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
    input="Calculate the factorial of 100"
)
```

**Learning Outcomes:**
- Execute code safely via API
- Perform data analysis with AI
- Generate charts and visualizations

---

### **Lesson 11: Code and Image Generation Combined**
**File:** `code_image_eleven.py` | `11_Code_Image_Output.ipynb`

**Topics Covered:**
- Multi-tool workflows
- Combining code execution with image generation
- Creating data visualizations
- Generating charts from computed data
- Advanced integration patterns

**Learning Outcomes:**
- Build complex multi-step AI workflows
- Combine multiple AI capabilities
- Create rich, dynamic outputs

---

### **Lesson 12: GPT Reasoning Models (o1/o3)**
**File:** `gpt_reasoning_12.py` | `12_GPT_Reasoning.ipynb`

**Topics Covered:**
- Introduction to reasoning models
- o1 vs o1-mini vs o3-mini
- When to use reasoning models:
  - Complex problem-solving
  - Mathematical reasoning
  - Coding challenges
  - Multi-step logic
- Reasoning model parameters
- Cost vs. performance tradeoffs
- Understanding reasoning traces

**Key Concepts:**
- Reasoning models "think" before responding
- Better for complex, multi-step problems
- Higher cost, slower responses
- Superior accuracy on difficult tasks

**Learning Outcomes:**
- Identify use cases for reasoning models
- Implement o1/o3 API calls
- Evaluate reasoning model outputs

---

### **Lesson 13: Advanced Reasoning Patterns**
**File:** `gpt_reasoning_improved_13.py` | `13_GPT_Reasoning_Improved.ipynb`

**Topics Covered:**
- Advanced prompting for reasoning models
- Chain-of-thought techniques
- Breaking down complex problems
- Iterative refinement
- Combining reasoning with tools
- Production best practices

**Learning Outcomes:**
- Master advanced reasoning patterns
- Build sophisticated AI agents
- Optimize for accuracy and cost

---

## 📁 Project Files

### Python Scripts (`.py`)
Standalone scripts for quick testing and deployment:

| File | Purpose | Complexity |
|------|---------|------------|
| `Connecting_llm_one.py` | Basic API connection | ⭐ Beginner |
| `no_memory_chatbot_two.py` | Stateless chatbot | ⭐ Beginner |
| `memory_chatbot_three.py` | Conversational chatbot | ⭐⭐ Intermediate |
| `audio_four.py` | Text-to-speech | ⭐⭐ Intermediate |
| `image_five.py` | Image generation | ⭐⭐ Intermediate |
| `web_search_six.py` | Basic web search | ⭐⭐ Intermediate |
| `web_search_project_seven.py` | Advanced search app | ⭐⭐⭐ Advanced |
| `mcp_eight.py` | MCP GitHub integration | ⭐⭐⭐ Advanced |
| `mcp_exercise_nine.py` | MCP code audit | ⭐⭐⭐ Advanced |
| `gpt_code_interpretor_ten.py` | Code execution | ⭐⭐ Intermediate |
| `code_image_eleven.py` | Multi-tool workflow | ⭐⭐⭐ Advanced |
| `gpt_reasoning_12.py` | Reasoning models | ⭐⭐⭐ Advanced |
| `gpt_reasoning_improved_13.py` | Advanced reasoning | ⭐⭐⭐⭐ Expert |

### Jupyter Notebooks (`Google_Colab/`)
Interactive notebooks for learning and experimentation - can run on Google Colab or locally

---

## 💰 Understanding OpenAI Pricing

### Model Cost Comparison (as of 2025)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Best For |
|-------|----------------------|------------------------|----------|
| **gpt-4o** | $2.50 | $10.00 | Production apps, complex tasks |
| **gpt-4o-mini** | $0.150 | $0.600 | Cost-effective, high-volume |
| **gpt-4-turbo** | $10.00 | $30.00 | Legacy support |
| **o1-preview** | $15.00 | $60.00 | Complex reasoning |
| **o1-mini** | $3.00 | $12.00 | Affordable reasoning |
| **o3-mini** | $1.10 | $4.40 | Cost-effective reasoning |
| **DALL-E 3** | - | $0.040/image (1024x1024) | Image generation |
| **TTS-1** | - | $15.00/1M characters | Fast audio |
| **TTS-1-HD** | - | $30.00/1M characters | High-quality audio |

**Pricing Source:** [OpenAI Pricing Page](https://openai.com/api/pricing/)

### Cost Optimization Tips

1. **Use gpt-4o-mini for most tasks** - 10x cheaper than gpt-4o
2. **Limit max_output_tokens** - Control response length
3. **Implement smart caching** - Avoid redundant API calls
4. **Use streaming** - Better user experience, same cost
5. **Choose the right model** - Don't use reasoning models for simple tasks

---

## 🎨 Model Selection Guide

### Decision Tree

```
Is it a simple factual question or basic task?
├─ Yes → Use gpt-4o-mini (fastest, cheapest)
└─ No → Does it require complex reasoning or math?
    ├─ Yes → Use o1-mini or o3-mini (reasoning models)
    └─ No → Does it need vision or multimodal?
        ├─ Yes → Use gpt-4o (multimodal support)
        └─ No → Use gpt-4o-mini (default choice)
```

### Use Case Recommendations

| Use Case | Recommended Model | Reason |
|----------|-------------------|---------|
| Chatbot, customer service | gpt-4o-mini | Cost-effective, fast |
| Content generation | gpt-4o-mini | Good quality/cost ratio |
| Code generation | gpt-4o or o3-mini | Better accuracy |
| Mathematical proofs | o1-preview or o1-mini | Reasoning capabilities |
| Image analysis | gpt-4o | Multimodal support |
| Audio generation | tts-1 | Fast, good quality |
| Image creation | dall-e-3 | Only option, great results |
| Web search tasks | gpt-4o-mini + tools | Efficient with tools |

---

## 🔑 Key Concepts Reference

### 1. **Temperature**
Controls randomness in responses:
- `0.0` - Deterministic, focused
- `0.7` - Balanced (default)
- `1.0+` - Creative, diverse

### 2. **Tokens**
Units of text processing:
- ~4 characters = 1 token
- ~750 words = 1000 tokens
- Input + output = total tokens charged

### 3. **Context Window**
Maximum tokens per request:
- gpt-4o: 128,000 tokens
- gpt-4o-mini: 128,000 tokens
- o1-preview: 128,000 tokens

### 4. **Roles**
Message types in conversation:
- `system` - Instructions to the AI
- `user` - User input
- `assistant` - AI responses
- `tool` - Tool/function outputs

### 5. **Tools**
Extended capabilities:
- `web_search` - Real-time internet search
- `code_interpreter` - Execute Python code
- `function_calling` - Custom function execution

---

## 📚 Additional Resources

### Official Documentation
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [OpenAI Cookbook](https://cookbook.openai.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

### Learning Materials
- [OpenAI Playground](https://platform.openai.com/playground) - Test prompts interactively
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI Community Forum](https://community.openai.com/)

### Tools & Extensions
- [Visual Studio Code](https://code.visualstudio.com/)
- [GitHub Copilot](https://github.com/features/copilot)
- [Postman](https://www.postman.com/) - API testing

### Quick Reference
- See `CHEATSHEET.md` for code snippets and common patterns

---

## 🎯 Course Completion Checklist

Track your progress through the course:

- [ ] ✅ Prerequisites installed (Python, VS Code, Git)
- [ ] ✅ OpenAI API key configured
- [ ] ✅ Lesson 1: Connected to OpenAI API
- [ ] ✅ Lesson 2: Built stateless chatbot
- [ ] ✅ Lesson 3: Implemented memory chatbot
- [ ] ✅ Lesson 4: Generated audio with TTS
- [ ] ✅ Lesson 5: Created images with DALL-E
- [ ] ✅ Lesson 6: Integrated web search
- [ ] ✅ Lesson 7: Built web search project
- [ ] ✅ Lesson 8: Set up MCP
- [ ] ✅ Lesson 9: Completed MCP exercise
- [ ] ✅ Lesson 10: Used code interpreter
- [ ] ✅ Lesson 11: Combined code and images
- [ ] ✅ Lesson 12: Explored reasoning models
- [ ] ✅ Lesson 13: Mastered advanced reasoning

---

## 🤝 Support & Contact

### Getting Help
1. Check the `CHEATSHEET.md` for quick references
2. Review the example code in each lesson
3. Consult the OpenAI documentation
4. Experiment in the Playground first

### Best Practices
- **Always use `.env` for API keys** - Never hardcode credentials
- **Start with small examples** - Test before building complex apps
- **Monitor your usage** - Check [OpenAI Usage Dashboard](https://platform.openai.com/usage)
- **Handle errors gracefully** - Implement try-catch blocks
- **Use streaming for better UX** - Especially in chatbots

---

## 📄 License & Usage

This educational material is designed for learning Generative AI development. Feel free to:
- Use the code examples in your projects
- Modify and extend the examples
- Share with other learners
- Build upon these foundations

**Remember:** OpenAI API usage is subject to [OpenAI's Usage Policies](https://openai.com/policies/usage-policies)

---

## 🚀 Next Steps

After completing this course, consider exploring:

1. **Advanced Topics:**
   - Fine-tuning custom models
   - Embeddings and vector databases
   - RAG (Retrieval-Augmented Generation)
   - LangChain and LlamaIndex frameworks

2. **Production Deployment:**
   - API rate limiting and caching
   - User authentication
   - Monitoring and logging
   - Scaling strategies

3. **Specialized Applications:**
   - AI coding assistants
   - Content moderation systems
   - Customer service automation
   - Data analysis tools

---

**Happy Learning! 🎓**

*Last Updated: April 2026*
