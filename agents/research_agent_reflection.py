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
# FUNCTION: REFLECTION AND REWRITE
# ================================

def reflection_and_rewrite(report: str, model: str = "gpt-4o-mini") -> dict:
    """
    Takes a research report and generates:
    1. A structured reflection (Strengths, Limitations, Suggestions, Opportunities)
    2. A revised and improved version of the report
    
    Args:
        report (str): The original research report
        model (str): OpenAI model to use
        
    Returns:
        dict: Contains 'reflection' and 'revised_report' keys
    """
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    system_instructions = (
        "You are an academic reviewer and editor. "
        "You provide structured reflections and improve research reports. "
        f"Today's date is: {today}"
    )
    
    user_prompt = f"""Please analyze the following research report and provide a structured reflection and revised version.

Your response must be ONLY valid JSON with this exact structure:
{{
  "reflection": "Your structured reflection here covering: Strengths, Limitations, Suggestions, and Opportunities",
  "revised_report": "Your improved version of the report here"
}}

The reflection should cover:
- **Strengths**: What works well in the report
- **Limitations**: Areas that need improvement  
- **Suggestions**: Specific recommendations for enhancement
- **Opportunities**: Ways to expand or deepen the analysis

The revised report should:
- Incorporate the reflection insights
- Improve clarity and academic tone
- Add or enhance citations where needed
- Fix any organizational issues

Original Report:
{report}

Remember: Output ONLY the JSON object, no additional text or commentary."""

    input_list = [{"role": "user", "content": user_prompt}]
    
    print("\n" + "="*60)
    print("🧠 REFLECTION AGENT STARTED")
    print("="*60)
    
    # Call the API
    resp = client.responses.create(
        model=model,
        input=input_list,
        instructions=system_instructions
    )
    
    # Get the response text
    reflection_output = resp.output_text
    
    print("\n✅ Reflection generated")
    
    # Parse JSON
    try:
        data = json.loads(reflection_output)
        return {
            "reflection": str(data.get("reflection", "")).strip(),
            "revised_report": str(data.get("revised_report", "")).strip(),
        }
    except json.JSONDecodeError:
        print("⚠️ Warning: Could not parse JSON, returning raw output")
        return {
            "reflection": "Error: Invalid JSON response",
            "revised_report": reflection_output
        }


# ================================
# FUNCTION: CONVERT TO HTML
# ================================

def convert_to_html(report: str, model: str = "gpt-4o-mini") -> str:
    """
    Converts a plaintext research report into a styled HTML page.
    
    Args:
        report (str): The research report in plain text
        model (str): OpenAI model to use
        
    Returns:
        str: HTML formatted version of the report
    """
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    system_instructions = (
        "You convert plaintext research reports into full, clean HTML documents with proper styling. "
        f"Today's date is: {today}"
    )
    
    user_prompt = f"""Convert the following research report into a well-structured HTML document.

Requirements:
- Use proper HTML5 structure (<html>, <head>, <body>, <header>, <main>, <section>)
- Include appropriate headers (<h1>, <h2>, <h3>)
- Format paragraphs with <p> tags
- Make all URLs clickable with <a href="..."> tags
- Preserve all citations and references
- Add CSS styling for readability (use a <style> tag in the <head>)
- Make it professional and academic-looking
- Output ONLY valid HTML, no additional commentary

Report to convert:
{report}"""

    input_list = [{"role": "user", "content": user_prompt}]
    
    print("\n" + "="*60)
    print("📄 HTML CONVERSION STARTED")
    print("="*60)
    
    # Call the API
    resp = client.responses.create(
        model=model,
        input=input_list,
        instructions=system_instructions
    )
    
    # Get the HTML
    html = resp.output_text
    
    print("\n✅ HTML generated")
    
    return html


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
            print("📝 PRELIMINARY RESEARCH REPORT")
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
# FULL PIPELINE WITH REFLECTION
# ================================

def research_pipeline_with_reflection(
    prompt: str, 
    model: str = "gpt-4o-mini",
    save_to_file: bool = True,
    generate_html: bool = True
):
    """
    Complete research pipeline:
    1. Generate initial research report (with tools)
    2. Reflect on the report
    3. Get revised report
    4. Optionally convert to HTML
    5. Optionally save to file
    
    Args:
        prompt (str): Research query
        model (str): Model to use
        save_to_file (bool): Whether to save the final report
        generate_html (bool): Whether to generate HTML version
        
    Returns:
        dict: Contains all outputs (preliminary, reflection, revised, html)
    """
    
    print("\n" + "🎯"*30)
    print("FULL RESEARCH PIPELINE WITH REFLECTION")
    print("🎯"*30 + "\n")
    
    # Step 1: Generate preliminary research report
    print("\n📍 STEP 1: Generating preliminary research report...")
    preliminary_report = research_agent(prompt, model=model)
    
    # Step 2: Reflect and revise
    print("\n📍 STEP 2: Reflecting on report and generating revision...")
    reflection_data = reflection_and_rewrite(preliminary_report, model=model)
    
    print("\n" + "="*60)
    print("💭 REFLECTION")
    print("="*60)
    print(reflection_data["reflection"])
    
    print("\n" + "="*60)
    print("📝 REVISED REPORT")
    print("="*60)
    print(reflection_data["revised_report"])
    
    # Step 3: Convert to HTML (optional)
    html_output = None
    if generate_html:
        print("\n📍 STEP 3: Converting to HTML...")
        html_output = convert_to_html(reflection_data["revised_report"], model=model)
        print("\n✅ HTML generated successfully")
    
    # Step 4: Save to file (optional)
    if save_to_file:
        print("\n📍 STEP 4: Saving outputs to files...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save preliminary report
        with open(f"preliminary_report_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(preliminary_report)
        print(f"✅ Saved: preliminary_report_{timestamp}.txt")
        
        # Save reflection
        with open(f"reflection_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(reflection_data["reflection"])
        print(f"✅ Saved: reflection_{timestamp}.txt")
        
        # Save revised report
        with open(f"revised_report_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(reflection_data["revised_report"])
        print(f"✅ Saved: revised_report_{timestamp}.txt")
        
        # Save HTML
        if html_output:
            with open(f"report_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(html_output)
            print(f"✅ Saved: report_{timestamp}.html")
    
    print("\n" + "="*60)
    print("✨ PIPELINE COMPLETE")
    print("="*60 + "\n")
    
    return {
        "preliminary_report": preliminary_report,
        "reflection": reflection_data["reflection"],
        "revised_report": reflection_data["revised_report"],
        "html": html_output
    }


# ================================
# EXAMPLE USAGE
# ================================

if __name__ == "__main__":
    
    # Example 1: Basic research query with full pipeline
    prompt_1 = (
        "Write a comprehensive research report about Retrieval-Augmented Generation (RAG). "
        "Include recent papers from arXiv and current web information about applications."
    )
    
    # Example 2: Specific academic topic
    prompt_2 = "Radio observations of recurrent novae"
    
    # Example 3: Technology research
    prompt_3 = (
        "Research the latest developments in Large Language Models in 2024. "
        "Include both academic papers and industry applications."
    )
    
    # Run the full pipeline
    print("Choose a prompt:")
    print("1. RAG research")
    print("2. Radio observations of recurrent novae")
    print("3. LLM developments 2024")
    
    # Run with full reflection pipeline
    results = research_pipeline_with_reflection(
        prompt=prompt_2,  # Change this to prompt_1, prompt_2, or prompt_3
        model="gpt-4o-mini",
        save_to_file=True,
        generate_html=True
    )
    
    print("\n🎉 All done! Check your files for the outputs.")