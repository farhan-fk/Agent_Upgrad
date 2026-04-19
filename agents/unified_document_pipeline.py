"""
===============================================================================
UNIFIED DOCUMENT PROCESSING PIPELINE
===============================================================================

Handles multiple document types with:
1. Auto-classification
2. Schema-based extraction
3. Downstream routing (Database, Excel, API, etc.)

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
# STEP 1: DOCUMENT TYPE CLASSIFICATION
# ============================================================================

def classify_document(image_path):
    """
    Classify document into one of the supported types.
    
    Returns:
        str: Document type identifier
    """
    
    prompt = """
Classify this document into ONE of these types:
- ride_invoice (ride-sharing service invoice like OLA/Uber)
- restaurant_receipt (restaurant/cafe purchase receipt)
- student_worksheet (homework, quiz, or educational worksheet)
- academic_paper (research paper, academic table, or scientific document)
- other

Return ONLY the type as a single phrase in lowercase, nothing else.
"""
    
    response = get_completion_with_image(prompt, image_path)
    doc_type = response.strip().lower().replace(" ", "_")
    
    print(f"📋 Detected: {doc_type.upper()}")
    return doc_type

# ============================================================================
# STEP 2: SCHEMA DEFINITIONS
# ============================================================================

SCHEMAS = {
    "ride_invoice": {
        "fields": {
            "service_provider": "string (e.g., OLA, Uber)",
            "invoice_number": "string",
            "invoice_date": "date",
            "customer_name": "string",
            "mobile_number": "string",
            "ride_number": "string",
            "pickup_address": "string",
            "dropoff_address": "string",
            "base_fare": "number",
            "convenience_fees": "number",
            "parking_charges": "number",
            "cgst": "number",
            "sgst": "number",
            "total_amount": "number",
            "payment_method": "string",
            "transaction_date": "datetime",
            "gstin": "string",
            "sac_code": "string",
            "extraction_timestamp": "ISO timestamp"
        },
        "description": "Ride-sharing service invoice"
    },
    
    "restaurant_receipt": {
        "fields": {
            "merchant_name": "string",
            "merchant_address": "string",
            "merchant_phone": "string",
            "transaction_date": "date",
            "transaction_time": "time",
            "register_number": "string",
            "items": "list of items with description and price",
            "subtotal": "number",
            "tax": "number",
            "total_amount": "number",
            "payment_method": "string",
            "extraction_timestamp": "ISO timestamp"
        },
        "description": "Restaurant or cafe receipt"
    },
    
    "student_worksheet": {
        "fields": {
            "student_name": "string",
            "worksheet_title": "string",
            "questions": "list of questions with student answers",
            "subject": "string",
            "grade_level": "string if visible",
            "total_questions": "number",
            "extraction_timestamp": "ISO timestamp"
        },
        "description": "Student homework or worksheet"
    },
    
    "academic_paper": {
        "fields": {
            "document_title": "string",
            "table_number": "string if visible",
            "table_caption": "string",
            "column_headers": "list of column names",
            "data_rows": "list of rows with values",
            "paper_section": "string (e.g., Results, Methods)",
            "extraction_timestamp": "ISO timestamp"
        },
        "description": "Academic paper or research document"
    }
}

# ============================================================================
# STEP 3: EXTRACTION WITH RETRY
# ============================================================================

def extract_document_data(image_path, doc_type=None, max_retries=2):
    """
    Extract data from any document type with auto-detection.
    
    Args:
        image_path (str): Path to image file
        doc_type (str): Optional manual override for document type
        max_retries (int): Maximum retry attempts if parsing fails
    
    Returns:
        dict: Extracted document data with metadata
    """
    
    # Step 1: Classify if not provided
    if not doc_type:
        doc_type = classify_document(image_path)
    
    # Step 2: Get schema
    if doc_type not in SCHEMAS:
        print(f"⚠️  Unknown type: {doc_type}")
        doc_type = "other"
    
    if doc_type == "other":
        return {
            "error": "Unsupported document type",
            "detected_type": doc_type,
            "extraction_timestamp": datetime.now().isoformat()
        }
    
    schema = SCHEMAS[doc_type]
    schema_json = json.dumps(schema["fields"], indent=2)
    
    # Step 3: Build prompt
    prompt = f"""
Extract ALL information from this {schema["description"]}.

Return ONLY valid JSON with these exact fields (use null if not found):

{schema_json}

IMPORTANT: 
- Extract text EXACTLY as shown 
- Convert amounts to numbers (remove $, commas)
- For lists, use JSON array format
- Use null for missing fields
- Return only JSON, no extra text
"""
    
    previous_response = None
    required_fields = list(schema["fields"].keys())
    
    # Step 4: Retry loop
    for attempt in range(max_retries + 1):
        if previous_response:
            retry_prompt = f"""
Your previous response was INVALID.

PREVIOUS RESPONSE (INCORRECT):
{previous_response}

Please try again. Extract information and return ONLY valid JSON with the exact schema.
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
            
            # Validate schema
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields and attempt < max_retries:
                print(f"⚠️  Missing: {missing_fields}")
                previous_response = response
                continue
            
            # Add metadata
            result["document_type"] = doc_type
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
                    "raw_response": response,
                    "document_type": doc_type
                }

# ============================================================================
# STEP 4: DOWNSTREAM ROUTING
# ============================================================================

class DownstreamRouter:
    """
    Routes extracted documents to appropriate destinations.
    """
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def route(self, extracted_data):
        """
        Route document to appropriate handler based on type.
        
        Args:
            extracted_data (dict): Extracted document data
        """
        doc_type = extracted_data.get("document_type", "unknown")
        
        print(f"\n📤 Routing {doc_type.upper()} document...")
        
        # Route based on document type
        if doc_type == "ride_invoice":
            self.save_to_excel(extracted_data, "ride_invoices.xlsx")
            self.send_to_accounting_system(extracted_data)
            
        elif doc_type == "restaurant_receipt":
            self.save_to_excel(extracted_data, "restaurant_receipts.xlsx")
            self.send_to_expense_tracker(extracted_data)
            
        elif doc_type == "student_worksheet":
            self.save_to_json(extracted_data, "student_worksheets.json")
            self.send_to_grading_system(extracted_data)
            
        elif doc_type == "academic_paper":
            self.save_to_json(extracted_data, "academic_papers.json")
            self.send_to_research_database(extracted_data)
            
        else:
            self.save_to_json(extracted_data, "unknown_documents.json")
    
    def save_to_excel(self, data, filename):
        """Append to Excel file."""
        filepath = os.path.join(self.output_dir, filename)
        
        # Flatten nested structures
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
        
        # Load existing data
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                existing = json.load(f)
        else:
            existing = []
        
        existing.append(data)
        
        with open(filepath, 'w') as f:
            json.dump(existing, f, indent=2)
        
        print(f"   ✅ Saved to JSON: {filename}")
    
    def send_to_accounting_system(self, data):
        """Simulate sending to accounting API."""
        print(f"   📊 → Accounting System: Invoice #{data.get('invoice_number')}")
        # In production: POST to accounting API
        # requests.post("https://api.accounting.com/invoices", json=data)
    
    def send_to_expense_tracker(self, data):
        """Simulate sending to expense tracking system."""
        print(f"   💰 → Expense Tracker: ${data.get('total_amount')}")
        # In production: POST to expense API
    
    def send_to_grading_system(self, data):
        """Simulate sending to grading platform."""
        print(f"   📝 → Grading System: {data.get('student_name')}")
        # In production: POST to LMS/grading API
    
    def send_to_research_database(self, data):
        """Simulate sending to research database."""
        print(f"   🔬 → Research DB: {data.get('document_title')}")
        # In production: POST to research database API
    
    def _flatten_dict(self, d, parent_key='', sep='_'):
        """Flatten nested dictionary for Excel export."""
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
# STEP 5: BATCH PROCESSING PIPELINE
# ============================================================================

def process_document_batch(image_paths, output_dir="output"):
    """
    Process multiple documents through the full pipeline.
    
    Args:
        image_paths (list): List of image file paths
        output_dir (str): Output directory for results
    """
    router = DownstreamRouter(output_dir)
    results = []
    
    print("\n" + "="*70)
    print("UNIFIED DOCUMENT PROCESSING PIPELINE")
    print("="*70)
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"\n[{i}/{len(image_paths)}] Processing: {os.path.basename(image_path)}")
        print("-" * 70)
        
        if not os.path.exists(image_path):
            print(f"❌ File not found: {image_path}")
            continue
        
        try:
            # Extract data
            extracted = extract_document_data(image_path)
            
            # Route downstream
            router.route(extracted)
            
            results.append(extracted)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"error": str(e), "file": image_path})
    
    print("\n" + "="*70)
    print(f"✅ COMPLETE! Processed {len(results)} documents")
    print(f"📂 Output directory: {output_dir}")
    print("="*70)
    
    return results

# ============================================================================
# MAIN TEST
# ============================================================================

if __name__ == "__main__":
    
    # Process actual document images
    test_images = [
        "invoice.png",
        "receipt.jpg",
        "fill_in_the_blanks.jpg",
        "table.png"
    ]
    
    # Process batch
    results = process_document_batch(test_images)
    
    # Save summary report
    with open("output/processing_summary.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n📄 Summary report: output/processing_summary.json")
