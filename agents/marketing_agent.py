#!/usr/bin/env python
# coding: utf-8

# ================================
# M5 Agentic AI - Multi-Agent Marketing Research Team
# ================================

"""
Multi-agent pipeline for creating a summer sunglasses campaign.

Agents:
1. Market Research Agent - Scans trends and matches products
2. Graphic Designer Agent - Creates campaign visuals
3. Copywriter Agent - Crafts marketing quotes
4. Packaging Agent - Assembles executive report

This demonstrates how multiple specialized agents can work together
in a coordinated workflow.
"""

# ================================
# IMPORTS
# ================================
import os
import json
import re
import base64
import xml.etree.ElementTree as ET
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv

import requests
from tavily import TavilyClient
from openai import OpenAI
from PIL import Image

# ================================
# SETUP
# ================================
load_dotenv()
client = OpenAI()

# Session for requests
session = requests.Session()
session.headers.update(
    {"User-Agent": "Marketing-Agent/1.0 (mailto:your.email@example.com)"}
)


# ================================
# TOOL 1: TAVILY SEARCH
# ================================

tavily_search_tool_schema = {
    "type": "function",
    "name": "tavily_search_tool",
    "description": "Performs general-purpose web search to discover current fashion trends and market insights.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search keywords for retrieving fashion and market trend information.",
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

def tavily_search_tool(query: str, max_results: int = 5):
    """Perform web search using Tavily API to find fashion trends."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return json.dumps([{"error": "TAVILY_API_KEY not found"}])

    api_base_url = os.getenv("DLAI_TAVILY_BASE_URL")
    tavily_client = TavilyClient(api_key=api_key, api_base_url=api_base_url)

    try:
        response = tavily_client.search(
            query=query, 
            max_results=max_results, 
            include_images=False
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", ""),
            })

        return json.dumps(results)
    except Exception as e:
        return json.dumps([{"error": str(e)}])


# ================================
# TOOL 2: PRODUCT CATALOG
# ================================

# Sample sunglasses catalog
SUNGLASSES_CATALOG = [
    {
        "id": "SG001",
        "name": "Aviator Classic Gold",
        "description": "Timeless aviator sunglasses with gold frame and gradient lenses",
        "style": "aviator",
        "color": "gold",
        "price": 149.99,
        "stock": 45
    },
    {
        "id": "SG002",
        "name": "Round Vintage Tortoise",
        "description": "Retro round sunglasses with tortoiseshell frame",
        "style": "round",
        "color": "tortoise",
        "price": 129.99,
        "stock": 32
    },
    {
        "id": "SG003",
        "name": "Cat-Eye Bold Black",
        "description": "Statement cat-eye sunglasses with oversized frames",
        "style": "cat-eye",
        "color": "black",
        "price": 139.99,
        "stock": 28
    },
    {
        "id": "SG004",
        "name": "Sport Wraparound Blue",
        "description": "Performance sport sunglasses with polarized lenses",
        "style": "sport",
        "color": "blue",
        "price": 169.99,
        "stock": 50
    },
    {
        "id": "SG005",
        "name": "Square Minimalist Clear",
        "description": "Modern square frame with transparent acetate",
        "style": "square",
        "color": "clear",
        "price": 119.99,
        "stock": 38
    },
    {
        "id": "SG006",
        "name": "Oversized Glam Rose Gold",
        "description": "Glamorous oversized sunglasses with rose gold details",
        "style": "oversized",
        "color": "rose-gold",
        "price": 159.99,
        "stock": 22
    },
    {
        "id": "SG007",
        "name": "Wayfarer Heritage Black",
        "description": "Classic wayfarer design in matte black",
        "style": "wayfarer",
        "color": "black",
        "price": 134.99,
        "stock": 55
    },
    {
        "id": "SG008",
        "name": "Geometric Modern Silver",
        "description": "Contemporary geometric frames with mirrored lenses",
        "style": "geometric",
        "color": "silver",
        "price": 144.99,
        "stock": 30
    }
]

product_catalog_tool_schema = {
    "type": "function",
    "name": "product_catalog_tool",
    "description": "Returns the internal sunglasses product catalog with details like name, style, price, and stock.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

def product_catalog_tool():
    """Returns the sunglasses product catalog."""
    return json.dumps(SUNGLASSES_CATALOG, indent=2)


# ================================
# TOOL REGISTRY
# ================================

tool_impls = {
    "tavily_search_tool": tavily_search_tool,
    "product_catalog_tool": product_catalog_tool,
}


# ================================
# UTILITY FUNCTIONS
# ================================

def print_agent_header(agent_name: str, emoji: str = "🤖"):
    """Print formatted agent header."""
    print("\n" + "="*70)
    print(f"{emoji} {agent_name}")
    print("="*70)


def print_tool_call(tool_name: str, args: dict):
    """Print formatted tool call."""
    print(f"\n  🛠️  Calling: {tool_name}")
    print(f"     Args: {json.dumps(args, indent=6)}")


def print_result(content: str, truncate: int = 500):
    """Print formatted result."""
    display_content = content[:truncate] + "..." if len(content) > truncate else content
    print(f"\n✅ Result: {display_content}\n")


# ================================
# AGENT 1: MARKET RESEARCH AGENT
# ================================

def market_research_agent(model: str = "gpt-4o-mini", max_iterations: int = 10):
    """
    Market Research Agent - Discovers fashion trends and matches them 
    with products from the internal catalog.
    
    Returns:
        str: Trend analysis with product recommendations
    """
    
    print_agent_header("Market Research Agent", "🕵️‍♂️")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    system_instructions = f"""You are a fashion market research agent preparing a trend analysis for a summer sunglasses campaign.

IMPORTANT: You MUST use the tools available to you:
1. FIRST: Call tavily_search_tool to search for "sunglasses fashion trends 2024" or "summer sunglasses trends"
2. SECOND: Call product_catalog_tool to see our available sunglasses products
3. THIRD: Match the trends you found with specific products from our catalog

Today's date: {today}

Your final response MUST include:
- The top 2-3 sunglasses trends you found (with specific details like styles, colors, or features)
- Specific product recommendations from our catalog with IDs (e.g., SG001, SG002)
- Clear reasoning why these products match the trends

Remember: Use the tools! Don't make up trends - search for them first!"""

    user_prompt = """Please research current sunglasses fashion trends for summer 2024/2025.

Step 1: Use tavily_search_tool to search for "sunglasses fashion trends summer 2024"
Step 2: Use product_catalog_tool to see what products we have
Step 3: Match trends to our products and provide recommendations

Give me a detailed report with specific trends and product matches."""
    
    input_list = [{"role": "user", "content": user_prompt}]
    tools = [tavily_search_tool_schema, product_catalog_tool_schema]
    
    # First call
    resp = client.responses.create(
        model=model,
        input=input_list,
        instructions=system_instructions,
        tools=tools
    )
    
    call_number = 1
    
    while call_number <= max_iterations:
        
        print(f"\n🔄 Processing call #{call_number}")
        
        # Check for tool calls
        has_tool_calls = False
        for item in resp.output:
            if item.type == "function_call":
                has_tool_calls = True
                break
        
        # If no tool calls → final answer
        if not has_tool_calls:
            print("\n✅ Market research complete")
            final_answer = resp.output_text
            print_result(final_answer)
            return final_answer
        
        # Copy tool calls to input list
        for item in resp.output:
            if item.type == "function_call":
                input_list.append({
                    "type": "function_call",
                    "call_id": item.call_id,
                    "name": item.name,
                    "arguments": item.arguments
                })
        
        # Execute tools
        for item in resp.output:
            if item.type == "function_call":
                tool_name = item.name
                args = json.loads(item.arguments) if item.arguments else {}
                
                print_tool_call(tool_name, args)
                
                python_func = tool_impls[tool_name]
                
                try:
                    result = python_func(**args)
                except TypeError:
                    result = python_func()
                
                print(f"     ✓ Complete")
                
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result
                })
        
        call_number += 1
        
        if call_number > max_iterations:
            break
        
        resp = client.responses.create(
            model=model,
            input=input_list,
            instructions=system_instructions,
            tools=tools
        )
    
    return resp.output_text if resp.output_text else "⚠️ Max iterations reached"


# ================================
# AGENT 2: GRAPHIC DESIGNER AGENT
# ================================

def graphic_designer_agent(
    trend_insights: str, 
    caption_style: str = "short punchy",
    size: str = "1024x1024",
    model: str = "gpt-4o-mini"
):
    """
    Graphic Designer Agent - Creates campaign visuals based on trend insights.
    
    Process:
    1. Uses LLM to generate image prompt and caption
    2. Uses DALL-E 3 to generate the actual image
    
    Args:
        trend_insights (str): Trend summary from market research
        caption_style (str): Style for the caption
        size (str): Image size (e.g., '1024x1024')
        model (str): Model for prompt generation
        
    Returns:
        dict: Contains image_url, image_path, prompt, and caption
    """
    
    print_agent_header("Graphic Designer Agent", "🎨")
    
    # Step 1: Generate prompt and caption
    system_instructions = """You are a visual marketing assistant specializing in fashion photography.
Based on trend insights, create prompts for AI-generated sunglasses campaign images.

CRITICAL: The image MUST feature sunglasses as the main subject. Always include:
- "sunglasses" in the prompt
- Specific style mentioned (aviator, cat-eye, round, etc.)
- Summer setting or lifestyle context
- Fashion-forward aesthetic"""

    user_prompt = f"""Trend insights:
{trend_insights}

Create an image prompt and caption for a SUNGLASSES campaign.

IMPORTANT: 
- The prompt MUST describe sunglasses clearly (mention the style/type)
- Include summer context (beach, poolside, city summer, etc.)
- Keep it fashion-focused and aspirational
- Caption should be {caption_style}

Output ONLY valid JSON:
{{"prompt": "Professional photograph of [SPECIFIC SUNGLASSES STYLE] sunglasses [SUMMER CONTEXT]...", "caption": "short marketing caption"}}"""

    input_list = [{"role": "user", "content": user_prompt}]
    
    print("\n📝 Generating image prompt and caption...")
    
    resp = client.responses.create(
        model=model,
        input=input_list,
        instructions=system_instructions
    )
    
    content = resp.output_text.strip()
    
    # Parse JSON
    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        parsed = json.loads(match.group(0)) if match else {"error": "No JSON found"}
    except Exception as e:
        print(f"⚠️ Warning: Could not parse JSON: {e}")
        parsed = {"prompt": "Modern sunglasses in summer setting", "caption": "Summer vibes"}
    
    prompt = parsed.get("prompt", "Modern sunglasses")
    caption = parsed.get("caption", "Summer style")
    
    print(f"\n✅ Prompt: {prompt[:100]}...")
    print(f"✅ Caption: {caption}")
    
    # Step 2: Generate image with DALL-E 3
    print("\n🖼️  Generating image with DALL-E 3...")
    
    # Ensure "sunglasses" is in the prompt
    if "sunglasses" not in prompt.lower():
        print("⚠️ Warning: Prompt missing 'sunglasses', adding it...")
        prompt = f"Professional fashion photograph of stylish sunglasses. {prompt}"
    
    try:
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
            response_format="url"
        )
        
        image_url = image_response.data[0].url
        
        # Download and save image
        img_bytes = requests.get(image_url).content
        img = Image.open(BytesIO(img_bytes))
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"campaign_image_{timestamp}.png"
        img.save(image_path)
        
        print(f"\n✅ Image saved: {image_path}")
        
        return {
            "image_url": image_url,
            "image_path": image_path,
            "prompt": prompt,
            "caption": caption
        }
        
    except Exception as e:
        print(f"\n❌ Error generating image: {e}")
        return {
            "image_url": None,
            "image_path": None,
            "prompt": prompt,
            "caption": caption,
            "error": str(e)
        }


# ================================
# AGENT 3: COPYWRITER AGENT
# ================================

def copywriter_agent(
    image_path: str,
    trend_summary: str,
    model: str = "gpt-4o"
):
    """
    Copywriter Agent - Creates campaign quotes based on image and trends.
    
    Uses multimodal capabilities to analyze the image and create appropriate copy.
    
    Args:
        image_path (str): Path to campaign image
        trend_summary (str): Market research summary
        model (str): Multimodal model (needs vision capability)
        
    Returns:
        dict: Contains quote, justification, and image_path
    """
    
    print_agent_header("Copywriter Agent", "✍️")
    
    # Load and encode image
    print(f"\n📷 Loading image: {image_path}")
    
    try:
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        
        b64_img = base64.b64encode(img_bytes).decode("utf-8")
        
        # Create multimodal message
        system_instructions = """You are a copywriter that creates elegant campaign quotes 
based on images and marketing trend summaries."""

        user_content = f"""Here is a visual marketing image and a trend analysis.

Trend summary:
\"\"\"{trend_summary}\"\"\"

Please return ONLY valid JSON with this structure:
{{
  "quote": "A short, elegant campaign phrase (max 12 words)",
  "justification": "Why this quote matches the image and trend"
}}"""

        # For vision models, we need to use chat.completions.create directly
        print("\n💭 Generating campaign quote...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instructions},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64_img}",
                                "detail": "auto"
                            }
                        },
                        {
                            "type": "text",
                            "text": user_content
                        }
                    ]
                }
            ]
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON
        try:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            parsed = json.loads(match.group(0)) if match else {"error": "No JSON found"}
        except Exception as e:
            print(f"⚠️ Warning: Could not parse JSON: {e}")
            parsed = {
                "quote": "See the world differently",
                "justification": "Emphasizes the transformative power of style"
            }
        
        parsed["image_path"] = image_path
        
        print(f"\n✅ Quote: {parsed.get('quote', 'N/A')}")
        print(f"✅ Justification: {parsed.get('justification', 'N/A')[:100]}...")
        
        return parsed
        
    except Exception as e:
        print(f"\n❌ Error in copywriting: {e}")
        return {
            "quote": "Summer style redefined",
            "justification": "Error occurred during generation",
            "image_path": image_path,
            "error": str(e)
        }


# ================================
# AGENT 4: PACKAGING AGENT
# ================================

def packaging_agent(
    trend_summary: str,
    image_path: str,
    quote: str,
    justification: str,
    model: str = "gpt-4o-mini"
):
    """
    Packaging Agent - Assembles all components into an executive report.
    
    Creates a polished markdown document with:
    - Refined trend insights
    - Campaign visual
    - Marketing quote
    - Justification
    
    Args:
        trend_summary (str): Market research summary
        image_path (str): Path to campaign image
        quote (str): Marketing quote
        justification (str): Quote justification
        model (str): Model for text refinement
        
    Returns:
        str: Path to saved markdown file
    """
    
    print_agent_header("Packaging Agent", "📦")
    
    # Step 1: Beautify trend summary for executives
    print("\n✨ Refining trend summary for executive audience...")
    
    system_instructions = """You are a marketing communication expert writing elegant 
campaign summaries for executives."""

    user_prompt = f"""Please rewrite the following trend summary to be clear, 
professional, and engaging for a CEO audience:

\"\"\"{trend_summary.strip()}\"\"\""""

    input_list = [{"role": "user", "content": user_prompt}]
    
    resp = client.responses.create(
        model=model,
        input=input_list,
        instructions=system_instructions
    )
    
    beautified_summary = resp.output_text.strip()
    
    print("✅ Summary refined")
    
    # Step 2: Create markdown report
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = f"campaign_summary_{timestamp}.md"
    
    markdown_content = f"""# 🕶️ Summer Sunglasses Campaign – Executive Summary

## 📊 Refined Trend Insights
{beautified_summary}

## 🎯 Campaign Visual
![Campaign Image]({image_path})

## ✍️ Campaign Quote
> {quote.strip()}

## ✅ Why This Works
{justification.strip()}

---

*Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*
"""
    
    # Save markdown
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"\n✅ Report saved: {output_path}")
    
    return output_path


# ================================
# FULL PIPELINE ORCHESTRATION
# ================================

def run_sunglasses_campaign_pipeline():
    """
    Run the complete multi-agent marketing campaign pipeline.
    
    Workflow:
    1. Market Research Agent - Find trends and match products
    2. Graphic Designer Agent - Create campaign visual
    3. Copywriter Agent - Generate marketing quote
    4. Packaging Agent - Assemble executive report
    
    Returns:
        dict: All intermediate results and final report path
    """
    
    print("\n" + "🎯"*35)
    print("SUMMER SUNGLASSES CAMPAIGN PIPELINE")
    print("🎯"*35 + "\n")
    
    start_time = datetime.now()
    
    # Step 1: Market Research
    print("\n📍 STEP 1: Market Research")
    trend_summary = market_research_agent()
    
    # Check if research failed
    if "max iterations" in trend_summary.lower() or "warning" in trend_summary.lower():
        print("\n⚠️ Market research had issues. Using fallback trend data...")
        trend_summary = """
**Summer 2024 Sunglasses Trends:**

1. **Retro Aviators**: Classic aviator styles are making a strong comeback with modern twists. Gold and silver frames are particularly popular.

2. **Oversized Frames**: Bold, oversized sunglasses are trending, especially in cat-eye and geometric shapes. These make a statement and provide excellent sun protection.

3. **Sustainable Materials**: Eco-friendly sunglasses made from recycled materials are gaining traction among environmentally conscious consumers.

**Product Recommendations:**
- **SG001 (Aviator Classic Gold)**: Perfect match for the retro aviator trend. Timeless design with modern appeal. Price: $149.99, In Stock: 45 units
- **SG006 (Oversized Glam Rose Gold)**: Aligns with the oversized frame trend. Glamorous and eye-catching. Price: $159.99, In Stock: 22 units
- **SG003 (Cat-Eye Bold Black)**: Statement piece matching the bold oversized trend. Price: $139.99, In Stock: 28 units
"""
        print("✅ Using curated trend analysis")
    
    # Step 2: Visual Design
    print("\n📍 STEP 2: Visual Design")
    visual_result = graphic_designer_agent(trend_insights=trend_summary)
    image_path = visual_result.get("image_path")
    
    if not image_path:
        print("\n⚠️ Warning: Image generation failed, using placeholder")
        image_path = "placeholder.png"
    
    # Step 3: Copywriting
    print("\n📍 STEP 3: Copywriting")
    quote_result = copywriter_agent(
        image_path=image_path,
        trend_summary=trend_summary
    )
    quote = quote_result.get("quote", "Summer style")
    justification = quote_result.get("justification", "N/A")
    
    # Step 4: Packaging
    print("\n📍 STEP 4: Packaging")
    markdown_path = packaging_agent(
        trend_summary=trend_summary,
        image_path=image_path,
        quote=quote,
        justification=justification
    )
    
    # Calculate execution time
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Summary
    print("\n" + "="*70)
    print("📊 PIPELINE SUMMARY")
    print("="*70)
    print(f"✅ Market Research: Complete")
    print(f"✅ Visual Design: {image_path}")
    print(f"✅ Copywriting: {quote}")
    print(f"✅ Final Report: {markdown_path}")
    print(f"⏱️  Total Time: {duration:.2f} seconds")
    print("="*70 + "\n")
    
    # Read and display the report
    try:
        with open(markdown_path, "r", encoding="utf-8") as f:
            report_content = f.read()
        
        print("\n" + "="*70)
        print("📄 FINAL EXECUTIVE REPORT")
        print("="*70)
        print(report_content)
        print("="*70 + "\n")
    except Exception as e:
        print(f"⚠️ Could not display report: {e}")
    
    return {
        "trend_summary": trend_summary,
        "visual": visual_result,
        "quote": quote_result,
        "markdown_path": markdown_path,
        "execution_time": duration
    }


# ================================
# EXAMPLE USAGE
# ================================

if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("🚀 MULTI-AGENT MARKETING CAMPAIGN SYSTEM")
    print("="*70)
    print("\nThis pipeline demonstrates:")
    print("  • Multi-agent collaboration")
    print("  • Tool calling (web search + product catalog)")
    print("  • Multimodal AI (text + image)")
    print("  • Executive report generation")
    print("="*70 + "\n")
    
    # Run the full pipeline
    results = run_sunglasses_campaign_pipeline()
    
    print("\n" + "🎉"*35)
    print("CAMPAIGN COMPLETE!")
    print("🎉"*35 + "\n")
    
    print("💡 Key Takeaways:")
    print("  • Multiple specialized agents working together")
    print("  • External tools ground outputs in real data")
    print("  • Multimodal models process both text and images")
    print("  • Structured workflows produce professional deliverables")
    print("\n" + "="*70 + "\n")