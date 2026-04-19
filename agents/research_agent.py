# ================================
# IMPORTS
# ================================
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

import requests
from tavily import TavilyClient
from openai import OpenAI

# ================================
# SETUP
# ================================
load_dotenv()
client = OpenAI()

# Session for arXiv requests
session = requests.Session()
session.headers.update(
    {"User-Agent": "LF-ADP-Agent/1.0 (mailto:your.email@example.com)"}
)


# ================================
# TOOL 1: ARXIV SEARCH
# ================================

arxiv_tool = {
    "type": "function",
    "name": "arxiv_search_tool",
    "description": "Searches for research papers on arXiv by query string.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search keywords for research papers.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return.",
                "default": 5,
            },
        },
        "required": ["query"],
    },
}

def arxiv_search_tool(query: str, max_results: int = 5):
    """Searches arXiv for research papers matching the given query."""
    url = f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return json.dumps([{"error": str(e)}])

    try:
        root = ET.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        results = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text.strip()
            authors = [
                author.find("atom:name", ns).text
                for author in entry.findall("atom:author", ns)
            ]
            published = entry.find("atom:published", ns).text[:10]
            url_abstract = entry.find("atom:id", ns).text
            summary = entry.find("atom:summary", ns).text.strip()

            link_pdf = None
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf":
                    link_pdf = link.attrib.get("href")
                    break

            results.append({
                "title": title,
                "authors": authors,
                "published": published,
                "url": url_abstract,
                "summary": summary,
                "link_pdf": link_pdf,
            })

        return json.dumps(results)
    except Exception as e:
        return json.dumps([{"error": f"Parsing failed: {str(e)}"}])


# ================================
# TOOL 2: TAVILY SEARCH
# ================================

tavily_tool = {
    "type": "function",
    "name": "tavily_search_tool",
    "description": "Performs a general-purpose web search using the Tavily API.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search keywords for retrieving information from the web.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return.",
                "default": 5,
            },
            "include_images": {
                "type": "boolean",
                "description": "Whether to include image results.",
                "default": False,
            },
        },
        "required": ["query"],
    },
}

def tavily_search_tool(query: str, max_results: int = 5, include_images: bool = False):
    """Perform a search using the Tavily API."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return json.dumps([{"error": "TAVILY_API_KEY not found in environment variables."}])

    api_base_url = os.getenv("DLAI_TAVILY_BASE_URL")
    tavily_client = TavilyClient(api_key=api_key, api_base_url=api_base_url)

    try:
        response = tavily_client.search(
            query=query, max_results=max_results, include_images=include_images
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", ""),
            })

        if include_images:
            for img_url in response.get("images", []):
                results.append({"image_url": img_url})

        return json.dumps(results)

    except Exception as e:
        return json.dumps([{"error": str(e)}])


# ================================
# TOOL 3: WRITE FILE
# ================================

write_file_tool = {
    "type": "function",
    "name": "write_file",
    "description": (
        "Write text content into a file on disk. "
        "Use this tool to save research reports, summaries, or any text output."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path where the file should be saved."},
            "content": {"type": "string", "description": "The text content to write to the file."}
        },
        "required": ["file_path", "content"]
    }
}

def write_file(file_path: str, content: str):
    """Write content to a text file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ File saved successfully at {file_path}"
    except Exception as e:
        return f"❌ Error saving file: {str(e)}"


# ================================
# TOOL REGISTRY
# ================================

tool_impls = {
    "arxiv_search_tool": arxiv_search_tool,
    "tavily_search_tool": tavily_search_tool,
    "write_file": write_file,
}


# ================================
# MAIN RESEARCH AGENT FUNCTION
# ================================

def research_agent(prompt: str, model: str = "gpt-4o-mini", max_iterations: int = 10):
    """
    Agentic research assistant that uses arXiv and Tavily search tools
    to generate comprehensive research reports.
    
    Args:
        prompt (str): The user's research request
        model (str): OpenAI model to use
        max_iterations (int): Maximum number of agent turns
    
    Returns:
        str: Final research report
    """
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    system_instructions = (
        "You are a research assistant that can search the web and arXiv to write detailed, "
        "accurate, and properly sourced research reports.\n\n"
        "🔍 Use tools when appropriate (e.g., to find scientific papers or web content).\n"
        "📚 Cite sources whenever relevant. Do NOT omit citations for brevity.\n"
        "🌐 When possible, include full URLs (arXiv links, web sources, etc.).\n"
        "✍️ Use an academic tone, organize output into clearly labeled sections, and include "
        "inline citations or footnotes as needed.\n"
        "🚫 Do not include placeholder text such as '(citation needed)' or '(citations omitted)'.\n"
        f"📅 Today's date is: {today}"
    )
    
    # Initialize input list with user message
    input_list = [{"role": "user", "content": prompt}]
    
    # Available tools
    tools = [arxiv_tool, tavily_tool, write_file_tool]
    
    print("\n" + "="*60)
    print("🔬 RESEARCH AGENT STARTED")
    print("="*60)
    
    # ================================
    # FIRST CALL TO LLM
    # ================================
    
    print(f"\n{'='*60}")
    print(f"📞 CALL #1 TO LLM")
    print(f"{'='*60}")
    
    resp = client.responses.create(
        model=model,
        input=input_list,
        instructions=system_instructions,
        tools=tools
    )
    
    # ================================
    # AGENTIC LOOP
    # ================================
    
    call_number = 1
    
    while call_number <= max_iterations:
        
        print(f"\n{'='*60}")
        print(f"🔄 PROCESSING CALL #{call_number}")
        print(f"{'='*60}")
        
        # ================================
        # CHECK: DOES RESPONSE HAVE TOOL CALLS?
        # ================================
        
        has_tool_calls = False
        for item in resp.output:
            if item.type == "function_call":
                has_tool_calls = True
                break
        
        # ================================
        # IF NO TOOL CALLS → FINAL ANSWER
        # ================================
        
        if not has_tool_calls:
            print("\n✅ NO TOOL CALLS - FINAL ANSWER RECEIVED")
            print("\n" + "="*60)
            print("📝 FINAL RESEARCH REPORT")
            print("="*60 + "\n")
            final_answer = resp.output_text
            print(final_answer)
            return final_answer
        
        # ================================
        # DEBUG: SHOW TOOL CALLS
        # ================================
        
        print(f"\n🛠️  TOOL CALLS DETECTED")
        for item in resp.output:
            if item.type == "function_call":
                print(f"\n  └─ 🔧 {item.name}")
                print(f"     Call ID: {item.call_id}")
                print(f"     Arguments: {item.arguments}")
        
        # ================================
        # COPY TOOL CALLS TO INPUT LIST
        # ================================
        
        for item in resp.output:
            if item.type == "function_call":
                input_list.append({
                    "type": "function_call",
                    "call_id": item.call_id,
                    "name": item.name,
                    "arguments": item.arguments
                })
        
        # ================================
        # EXECUTE TOOLS AND ADD OUTPUTS
        # ================================
        
        for item in resp.output:
            if item.type == "function_call":
                tool_name = item.name
                raw_args = item.arguments
                args = json.loads(raw_args) if raw_args else {}
                
                print(f"\n  ▶️  EXECUTING: {tool_name}")
                print(f"     Arguments: {args}")
                
                # Get the Python function
                python_func = tool_impls[tool_name]
                
                # Execute the tool
                try:
                    result = python_func(**args)
                except TypeError:
                    result = python_func()
                
                # Truncate output for display
                display_result = result[:200] + "..." if len(result) > 200 else result
                print(f"     ✓ Returned: {display_result}")
                
                # Add tool output to input list
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result
                })
        
        # ================================
        # DEBUG: SHOW INPUT FOR NEXT CALL
        # ================================
        
        print(f"\n📋 INPUT LIST NOW HAS {len(input_list)} ITEMS")
        
        # ================================
        # NEXT CALL TO LLM
        # ================================
        
        call_number += 1
        
        if call_number > max_iterations:
            print(f"\n⚠️  WARNING: Hit max iterations ({max_iterations}). Stopping.")
            break
        
        print(f"\n{'='*60}")
        print(f"📞 CALL #{call_number} TO LLM")
        print(f"{'='*60}")
        
        resp = client.responses.create(
            model=model,
            input=input_list,
            instructions=system_instructions,
            tools=tools
        )
    
    return "⚠️ Max iterations reached without final answer."


# ================================
# EXAMPLE USAGE
# ================================

if __name__ == "__main__":
    
    # Example 1: Basic research query
    prompt_1 = (
        "Write a comprehensive research report about Retrieval-Augmented Generation (RAG). "
        "Include recent papers from arXiv and current web information. "
        "Save the report to 'rag_research_report.txt'."
    )
    
    # Example 2: Comparative analysis
    prompt_2 = (
        "Research the latest developments in Large Language Models in 2024. "
        "1. Search arXiv for recent papers on LLMs\n"
        "2. Search the web for current industry applications\n"
        "3. Write a structured report comparing academic research vs industry implementations\n"
        "4. Save the report to 'llm_2024_analysis.txt'"
    )
    
    # Example 3: Specific topic
    prompt_3 = (
        "I need a research summary on 'transformer attention mechanisms'. "
        "Find 3 key papers from arXiv and 3 web articles, then create a "
        "synthesis document with proper citations."
    )
    
    # Run the agent
    result = research_agent(prompt_1)