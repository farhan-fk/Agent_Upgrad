"""
===============================================================================
DYNAMIC DOCUMENT PIPELINE - Zero-Schema Approach
===============================================================================

For environments with 100+ document formats or highly dynamic data.
LLM extracts ALL information without predefined schemas.

ADVANTAGES:
- Works with ANY document type
- No schema maintenance
- Adapts to new formats automatically
- Handles variations within same type

===============================================================================
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import base64
import pandas as pd
from datetime import datetime

load_dotenv()
client = OpenAI()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def encode_image(image_path):
    """Encode image to base64 for OpenAI API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_completion_with_image(prompt, image_path, model="gpt-4o-mini"):
    """Call OpenAI Vision API with image."""
    base64_image = encode_image(image_path)
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        }
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    
    return response.choices[0].message.content

# ============================================================================
# STEP 1: INTELLIGENT DOCUMENT CATEGORIZATION
# ============================================================================

def categorize_document(image_path):
    """
    High-level categorization into broad categories.
    Instead of 100 types, group into 5-10 categories.
    """
    
    prompt = """
Analyze this document and categorize it into ONE of these broad categories:

1. financial (invoices, receipts, bills, bank statements, tax forms)
2. educational (worksheets, exams, assignments, grades, certificates)
3. research (papers, tables, graphs, scientific documents)
4. legal (contracts, agreements, forms, certificates)
5. medical (prescriptions, reports, lab results)
6. correspondence (emails, letters, memos)
7. other

Return ONLY the category name in lowercase.
"""
    
    response = get_completion_with_image(prompt, image_path)
    category = response.strip().lower()
    
    print(f"📁 Category: {category.upper()}")
    return category

# ============================================================================
# STEP 2: OPEN EXTRACTION (No Predefined Schema)
# ============================================================================

def extract_document_intelligent(image_path, max_retries=2):
    """
    Extract ALL information without predefined schema.
    LLM decides what's important based on document type.
    
    Returns:
        dict: Dynamic extraction based on document content
    """
    
    prompt = """
Analyze this document and extract ALL relevant information.

Return a JSON object with:
1. "document_type": Brief description of document type (e.g., "ride-sharing invoice", "restaurant receipt")
2. "key_fields": Object containing all important fields you find
3. "metadata": Object with date, amounts, names, IDs, etc.
4. "structured_data": Any tables, lists, or structured content
5. "confidence": Your confidence level (high/medium/low)

BE INTELLIGENT:
- For invoices: extract amounts, dates, vendor, items, taxes
- For receipts: extract merchant, items, prices, totals
- For worksheets: extract questions, answers, student info
- For papers: extract tables, data, figures, citations
- For forms: extract all filled fields
- For any document: extract what matters most

Return ONLY valid JSON, no markdown formatting.

Example structure:
{
  "document_type": "restaurant receipt",
  "key_fields": {
    "merchant": "...",
    "total": ...,
    "date": "..."
  },
  "metadata": {...},
  "structured_data": {...},
  "confidence": "high"
}
"""
    
    previous_response = None
    
    for attempt in range(max_retries + 1):
        if previous_response:
            retry_prompt = f"""
Your previous response was INVALID JSON.

PREVIOUS RESPONSE (INCORRECT):
{previous_response}

Try again. Extract information and return ONLY valid JSON.
"""
            response = get_completion_with_image(retry_prompt, image_path)
            print(f"🔄 Retry {attempt}/{max_retries}...")
        else:
            response = get_completion_with_image(prompt, image_path)
        
        # Parse JSON
        try:
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            result = json.loads(cleaned.strip())
            
            # Add extraction metadata
            result["extraction_timestamp"] = datetime.now().isoformat()
            result["source_file"] = os.path.basename(image_path)
            
            if attempt > 0:
                print(f"✅ Success on retry {attempt}!")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON Error: {e}")
            
            if attempt < max_retries:
                previous_response = response
            else:
                print(f"❌ Failed after {max_retries + 1} attempts")
                return {
                    "error": "Parse failed",
                    "raw_response": response[:500],  # Truncate for safety
                    "extraction_timestamp": datetime.now().isoformat()
                }

# ============================================================================
# STEP 3: SMART ROUTING BASED ON CATEGORY
# ============================================================================

class DynamicRouter:
    """
    Routes documents based on broad category, not specific type.
    """
    
    def __init__(self, output_dir="output_dynamic"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def route(self, extracted_data, category):
        """
        Route based on category, not specific document type.
        """
        print(f"\n📤 Routing {category.upper()} document...")
        
        # Route by category instead of specific type
        routing_map = {
            "financial": self.handle_financial,
            "educational": self.handle_educational,
            "research": self.handle_research,
            "legal": self.handle_legal,
            "medical": self.handle_medical,
            "correspondence": self.handle_correspondence
        }
        
        handler = routing_map.get(category, self.handle_other)
        handler(extracted_data)
    
    def handle_financial(self, data):
        """Handle any financial document."""
        self.save_to_excel(data, "financial_documents.xlsx")
        print(f"   💰 → Financial System")
    
    def handle_educational(self, data):
        """Handle any educational document."""
        self.save_to_json(data, "educational_documents.json")
        print(f"   📚 → Education System")
    
    def handle_research(self, data):
        """Handle any research document."""
        self.save_to_json(data, "research_documents.json")
        print(f"   🔬 → Research Database")
    
    def handle_legal(self, data):
        """Handle any legal document."""
        self.save_to_json(data, "legal_documents.json")
        print(f"   ⚖️  → Legal Archive")
    
    def handle_medical(self, data):
        """Handle any medical document."""
        self.save_to_json(data, "medical_documents.json")
        print(f"   🏥 → Medical Records")
    
    def handle_correspondence(self, data):
        """Handle any correspondence."""
        self.save_to_json(data, "correspondence.json")
        print(f"   📧 → Communication Archive")
    
    def handle_other(self, data):
        """Handle unknown documents."""
        self.save_to_json(data, "other_documents.json")
        print(f"   📄 → General Archive")
    
    def save_to_excel(self, data, filename):
        """Flatten and save to Excel."""
        filepath = os.path.join(self.output_dir, filename)
        
        # Flatten nested data
        flat_data = self._flatten_dict(data)
        new_df = pd.DataFrame([flat_data])
        
        if os.path.exists(filepath):
            existing_df = pd.read_excel(filepath)
            df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            df = new_df
        
        df.to_excel(filepath, index=False)
        print(f"   ✅ Saved to Excel: {filename}")
    
    def save_to_json(self, data, filename):
        """Append to JSON file."""
        filepath = os.path.join(self.output_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                existing = json.load(f)
        else:
            existing = []
        
        existing.append(data)
        
        with open(filepath, 'w') as f:
            json.dump(existing, f, indent=2)
        
        print(f"   ✅ Saved to JSON: {filename}")
    
    def _flatten_dict(self, d, parent_key='', sep='_'):
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        return dict(items)

# ============================================================================
# STEP 4: UNIFIED PIPELINE
# ============================================================================

def process_dynamic_documents(image_paths, output_dir="output_dynamic"):
    """
    Process any number of document types without predefined schemas.
    """
    router = DynamicRouter(output_dir)
    results = []
    
    print("\n" + "="*70)
    print("DYNAMIC DOCUMENT PIPELINE - Zero-Schema Approach")
    print("="*70)
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"\n[{i}/{len(image_paths)}] Processing: {os.path.basename(image_path)}")
        print("-" * 70)
        
        if not os.path.exists(image_path):
            print(f"❌ File not found: {image_path}")
            continue
        
        try:
            # Categorize broadly
            category = categorize_document(image_path)
            
            # Extract intelligently (no schema)
            extracted = extract_document_intelligent(image_path)
            
            # Route by category
            router.route(extracted, category)
            
            results.append(extracted)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"error": str(e), "file": image_path})
    
    print("\n" + "="*70)
    print(f"✅ COMPLETE! Processed {len(results)} documents")
    print(f"📂 Output: {output_dir}")
    print("="*70)
    
    # Save summary
    summary_path = os.path.join(output_dir, "processing_summary.json")
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)
    
    return results

# ============================================================================
# MAIN TEST
# ============================================================================

if __name__ == "__main__":
    
    # Works with ANY document types
    test_images = [
        "invoice.png",
        "receipt.jpg",
        "fill_in_the_blanks.jpg",
        "table.png"
    ]
    
    # Process dynamically
    results = process_dynamic_documents(test_images)
    
    print(f"\n📊 Extracted {len(results)} documents without predefined schemas!")
