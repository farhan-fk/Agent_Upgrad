#!/usr/bin/env python
# coding: utf-8

# ================================
# M4 Agentic AI - Component-level Evaluation for Research Workflow
# ================================

"""
This lab focuses on evaluating ONE component of the research workflow: the research step.
Instead of generating essays and refining them, we design a component-level evaluation 
to check the quality of sources returned by the research step.

The evaluation compares URLs retrieved by the agent against a predefined list of 
preferred domains (e.g., arxiv.org, nature.com, nasa.gov).
"""

# ================================
# IMPORTS
# ================================
import os
import json
import re
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
    {"User-Agent": "Research-Agent/1.0 (mailto:your.email@example.com)"}
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
# TOOL 3: WIKIPEDIA SEARCH
# ================================

wikipedia_tool = {
    "type": "function",
    "name": "wikipedia_search_tool",
    "description": "Searches Wikipedia for encyclopedic summaries on a given topic.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search term for Wikipedia.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return.",
                "default": 3,
            },
        },
        "required": ["query"],
    },
}

def wikipedia_search_tool(query: str, max_results: int = 3):
    """Search Wikipedia for articles."""
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": query,
            "limit": max_results,
            "format": "json"
        }
        
        response = session.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if len(data) >= 4:
            titles = data[1]
            descriptions = data[2]
            urls = data[3]
            
            for i in range(len(titles)):
                results.append({
                    "title": titles[i],
                    "description": descriptions[i],
                    "url": urls[i]
                })
        
        return json.dumps(results)
    except Exception as e:
        return json.dumps([{"error": str(e)}])


# ================================
# TOOL REGISTRY
# ================================

tool_impls = {
    "arxiv_search_tool": arxiv_search_tool,
    "tavily_search_tool": tavily_search_tool,
    "wikipedia_search_tool": wikipedia_search_tool,
}


# ================================
# PREFERRED DOMAINS LIST
# ================================

TOP_DOMAINS = {
    # General reference / institutions / publishers
    "wikipedia.org", "nature.com", "science.org", "sciencemag.org", "cell.com",
    "mit.edu", "stanford.edu", "harvard.edu", "nasa.gov", "noaa.gov", "europa.eu",

    # CS/AI venues & indexes
    "arxiv.org", "acm.org", "ieee.org", "neurips.cc", "icml.cc", "openreview.net",

    # Other reputable outlets
    "elifesciences.org", "pnas.org", "jmlr.org", "springer.com", "sciencedirect.com",

    # Extra domains (case-specific additions)
    "pbs.org", "nova.edu", "nvcc.edu", "cccco.edu",

    # Well known programming sites
    "codecademy.com", "datacamp.com"
}


# ================================
# FUNCTION: FIND REFERENCES (Research Step)
# ================================

def find_references(task: str, model: str = "gpt-4o-mini", max_iterations: int = 5):
    """
    Perform a research task using external tools (arxiv, tavily, wikipedia).
    
    This is the RESEARCH STEP that we will evaluate.
    
    Args:
        task (str): The research task to perform
        model (str): OpenAI model to use
        max_iterations (int): Maximum number of agent turns
        
    Returns:
        str: Research results with citations and URLs
    """
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    system_instructions = f"""You are a research function with access to:
- arxiv_search_tool: academic papers
- tavily_search_tool: general web search
- wikipedia_search_tool: encyclopedic summaries

When providing results:
- Include full URLs for all sources
- Cite sources properly
- Provide clear, organized output
- Include publication dates where available

Today is {today}."""

    # Initialize input list with user message
    input_list = [{"role": "user", "content": task}]
    
    # Available tools
    tools = [arxiv_tool, tavily_tool, wikipedia_tool]
    
    print("\n" + "="*60)
    print("🔍 RESEARCH STEP - Finding References")
    print("="*60)
    print(f"Task: {task}")
    
    # ================================
    # FIRST CALL TO LLM
    # ================================
    
    print(f"\n📞 CALL #1 TO LLM")
    
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
        
        print(f"\n🔄 PROCESSING CALL #{call_number}")
        
        # Check for tool calls
        has_tool_calls = False
        for item in resp.output:
            if item.type == "function_call":
                has_tool_calls = True
                break
        
        # If no tool calls → final answer
        if not has_tool_calls:
            print("\n✅ Research complete - returning results")
            final_answer = resp.output_text
            return final_answer
        
        # Show tool calls
        print(f"🛠️  Tool calls detected")
        for item in resp.output:
            if item.type == "function_call":
                print(f"  └─ {item.name}")
        
        # Copy tool calls to input list
        for item in resp.output:
            if item.type == "function_call":
                input_list.append({
                    "type": "function_call",
                    "call_id": item.call_id,
                    "name": item.name,
                    "arguments": item.arguments
                })
        
        # Execute tools and add outputs
        for item in resp.output:
            if item.type == "function_call":
                tool_name = item.name
                raw_args = item.arguments
                args = json.loads(raw_args) if raw_args else {}
                
                print(f"  ▶️  Executing: {tool_name}({args})")
                
                # Get the Python function
                python_func = tool_impls[tool_name]
                
                # Execute the tool
                try:
                    result = python_func(**args)
                except TypeError:
                    result = python_func()
                
                print(f"     ✓ Complete")
                
                # Add tool output to input list
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result
                })
        
        # Next call to LLM
        call_number += 1
        
        if call_number > max_iterations:
            print(f"\n⚠️  Max iterations reached")
            break
        
        print(f"\n📞 CALL #{call_number} TO LLM")
        
        resp = client.responses.create(
            model=model,
            input=input_list,
            instructions=system_instructions,
            tools=tools
        )
    
    return resp.output_text if resp.output_text else "⚠️ Max iterations reached"


# ================================
# FUNCTION: EVALUATE TAVILY RESULTS
# ================================

def evaluate_tavily_results(top_domains: set, raw: str, min_ratio: float = 0.4):
    """
    Evaluate whether research results mostly come from preferred domains.
    
    This is a COMPONENT-LEVEL EVALUATION that checks the quality of sources
    returned by the research step.
    
    Args:
        top_domains (set[str]): Set of preferred domains (e.g., 'arxiv.org', 'nature.com')
        raw (str): Plain text or Markdown containing URLs
        min_ratio (float): Minimum preferred ratio required to pass (e.g., 0.4 = 40%)
        
    Returns:
        tuple[bool, str]: (flag, markdown_report)
            flag -> True if PASS, False if FAIL
            markdown_report -> Markdown-formatted summary of the evaluation
    """
    
    print("\n" + "="*60)
    print("📊 EVALUATING RESEARCH RESULTS")
    print("="*60)
    
    # Extract URLs from the text
    url_pattern = re.compile(r'https?://[^\s\]\)>\}]+', flags=re.IGNORECASE)
    urls = url_pattern.findall(raw)
    
    if not urls:
        report = """### Evaluation – Tavily Preferred Domains
❌ No URLs detected in the provided text.
Please include links in your research results.
"""
        print("\n❌ FAIL: No URLs found")
        return False, report
    
    # Count preferred vs total
    total = len(urls)
    preferred_count = 0
    details = []
    
    for url in urls:
        try:
            domain = url.split("/")[2]
            preferred = any(td in domain for td in top_domains)
            if preferred:
                preferred_count += 1
            status = "✅ PREFERRED" if preferred else "❌ NOT PREFERRED"
            details.append(f"- {url} → {status}")
        except IndexError:
            details.append(f"- {url} → ⚠️ INVALID URL")
    
    ratio = preferred_count / total if total > 0 else 0.0
    flag = ratio >= min_ratio
    
    # Markdown report
    status = "✅ PASS" if flag else "❌ FAIL"
    report = f"""
### Evaluation – Tavily Preferred Domains
- Total results: {total}
- Preferred results: {preferred_count}
- Ratio: {ratio:.2%}
- Threshold: {min_ratio:.0%}
- Status: {status}

**Details:**
{chr(10).join(details)}
"""
    
    print(f"\n{status}: {preferred_count}/{total} URLs from preferred domains ({ratio:.1%})")
    
    return flag, report


# ================================
# HELPER FUNCTION: PRINT FORMATTED OUTPUT
# ================================

def print_section(content: str, title: str = ""):
    """Print formatted output sections."""
    print("\n" + "="*60)
    if title:
        print(f"📋 {title}")
        print("="*60)
    print(content)
    print("="*60)


# ================================
# MAIN EVALUATION PIPELINE
# ================================

def run_evaluation_pipeline(
    topic: str,
    min_ratio: float = 0.4,
    custom_domains: set = None,
    model: str = "gpt-4o-mini"
):
    """
    Run the complete evaluation pipeline:
    1. Perform research (find_references)
    2. Evaluate sources against preferred domains
    
    Args:
        topic (str): Research topic
        min_ratio (float): Minimum ratio of preferred sources (0.0-1.0)
        custom_domains (set): Optional custom set of preferred domains
        model (str): Model to use for research
        
    Returns:
        dict: Contains research results, evaluation flag, and report
    """
    
    print("\n" + "🎯"*30)
    print(f"EVALUATION PIPELINE: {topic}")
    print("🎯"*30 + "\n")
    
    # Use custom domains if provided, otherwise use default
    domains = custom_domains if custom_domains else TOP_DOMAINS
    
    # Show sample of preferred domains
    print("\n📚 PREFERRED DOMAINS (sample):")
    print(json.dumps(sorted(list(domains))[:8], indent=2))
    
    # Step 1: Research
    research_task = f"Find 2-3 key papers and reliable overviews about {topic}."
    research_output = find_references(research_task, model=model)
    
    print_section(research_output, f"RESEARCH RESULTS: {topic}")
    
    # Step 2: Evaluate
    flag, eval_report = evaluate_tavily_results(domains, research_output, min_ratio=min_ratio)
    
    print_section(eval_report, "EVALUATION SUMMARY")
    
    # Return results
    return {
        "topic": topic,
        "research_output": research_output,
        "evaluation_passed": flag,
        "evaluation_report": eval_report,
        "ratio_threshold": min_ratio
    }


# ================================
# EXAMPLE USAGE
# ================================

if __name__ == "__main__":
    
    # Example 1: Black hole science (from the lab)
    print("\n" + "="*70)
    print("EXAMPLE 1: Black Hole Science")
    print("="*70)
    
    results1 = run_evaluation_pipeline(
        topic="recent developments in black hole science",
        min_ratio=0.4,
        model="gpt-4o-mini"
    )
    
    # Example 2: Custom topic and domains
    print("\n\n" + "="*70)
    print("EXAMPLE 2: AI Research with Custom Domains")
    print("="*70)
    
    custom_ai_domains = {
        "arxiv.org", "openai.com", "anthropic.com", "deepmind.com",
        "neurips.cc", "icml.cc", "acm.org", "ieee.org"
    }
    
    results2 = run_evaluation_pipeline(
        topic="transformer architectures in large language models",
        min_ratio=0.5,
        custom_domains=custom_ai_domains,
        model="gpt-4o-mini"
    )
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 EVALUATION SUMMARY")
    print("="*70)
    print(f"\nExample 1 (Black Holes): {'✅ PASSED' if results1['evaluation_passed'] else '❌ FAILED'}")
    print(f"Example 2 (AI Research): {'✅ PASSED' if results2['evaluation_passed'] else '❌ FAILED'}")
    
    print("\n" + "="*70)
    print("🎉 EVALUATION PIPELINE COMPLETE")
    print("="*70)
    print("\n💡 Key Takeaways:")
    print("  • Component-level evaluation focuses on ONE step (research)")
    print("  • Objective evaluation with clear ground truth (preferred domains)")
    print("  • Faster and cheaper than evaluating full essays")
    print("  • Provides actionable metrics for improvement")
    print("="*70 + "\n")


# ================================
# INTERACTIVE TESTING SECTION
# ================================

def interactive_test():
    """
    Interactive function for testing different topics and settings.
    """
    
    print("\n" + "🔬"*30)
    print("INTERACTIVE TESTING MODE")
    print("🔬"*30 + "\n")
    
    # Customizable parameters
    topic = "quantum computing advances"  # <- Change this
    min_ratio = 0.4                       # <- Change threshold (0.0–1.0)
    
    # Optional: customize domains
    custom_domains = {
        "nature.com", "science.org", "arxiv.org", "mit.edu",
        "quantum.com", "ibm.com", "google.com"
    }
    
    # Run evaluation
    results = run_evaluation_pipeline(
        topic=topic,
        min_ratio=min_ratio,
        custom_domains=custom_domains,
        model="gpt-4o-mini"
    )
    
    return results


# Uncomment to run interactive test
# interactive_results = interactive_test()