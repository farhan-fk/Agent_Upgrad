"""
===============================================================================
DYNAMIC DOCUMENT DIGITIZER - HANDLES ANY DOCUMENT TYPE
===============================================================================

PURPOSE: Automatically classify and extract data from ANY document image
- First classifies the document type
- Then extracts relevant data based on the type
- Saves to Excel with appropriate structure

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
# DOCUMENT CLASSIFICATION
# ============================================================================

def classify_document(image_path):
    """
    Classify the document type from image.
    
    Args:
        image_path (str): Path to image file
    
    Returns:
        str: Document type (e.g., 'invoice', 'receipt', 'claim', 'id_card')
    """
    
    prompt = """
Identify the type of document shown in this image.

Return ONLY a JSON object with this structure:
{
  "document_type": "one of: invoice, receipt, insurance_claim, medical_report, id_card, passport, contract, business_card, bank_statement, tax_form, delivery_note, purchase_order, other",
  "confidence": "high/medium/low",
  "description": "brief 1-sentence description of what you see"
}

Be precise and confident. Return ONLY valid JSON.
"""
    
    response = get_completion_with_image(prompt, image_path)
    
    try:
        # Clean and parse JSON
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        result = json.loads(cleaned.strip())
        return result
    except json.JSONDecodeError as e:
        print(f"⚠️  Classification JSON Error: {e}")
        return {
            "document_type": "unknown",
            "confidence": "low",
            "description": "Failed to classify"
        }


# ============================================================================
# DYNAMIC SCHEMA DEFINITIONS
# ============================================================================

SCHEMA_MAP = {
    "invoice": {
        "fields": [
            "invoice_number", "invoice_date", "due_date", "vendor_name",
            "vendor_address", "customer_name", "customer_address",
            "subtotal", "tax_amount", "total_amount", "currency",
            "payment_terms", "items"
        ]
    },
    "receipt": {
        "fields": [
            "merchant_name", "merchant_address", "date", "time",
            "transaction_id", "items", "subtotal", "tax", "total",
            "payment_method", "card_last_digits"
        ]
    },
    "insurance_claim": {
        "fields": [
            "insurance_company", "claim_number", "policy_number",
            "claim_date", "incident_date", "claimant_name",
            "total_claim_amount", "injury_claim", "property_claim",
            "vehicle_claim", "police_report_available", "status"
        ]
    },
    "medical_report": {
        "fields": [
            "patient_name", "patient_id", "date_of_birth", "report_date",
            "doctor_name", "diagnosis", "medications", "test_results",
            "hospital_name", "department"
        ]
    },
    "id_card": {
        "fields": [
            "full_name", "id_number", "date_of_birth", "issue_date",
            "expiry_date", "nationality", "gender", "address"
        ]
    },
    "bank_statement": {
        "fields": [
            "bank_name", "account_holder", "account_number", "statement_period",
            "opening_balance", "closing_balance", "total_credits",
            "total_debits", "statement_date"
        ]
    },
    "contract": {
        "fields": [
            "contract_title", "contract_number", "parties", "effective_date",
            "expiry_date", "contract_value", "payment_terms", "termination_clause"
        ]
    },
    "business_card": {
        "fields": [
            "person_name", "job_title", "company_name", "email",
            "phone", "mobile", "address", "website"
        ]
    }
}


# ============================================================================
# DYNAMIC EXTRACTION FUNCTION
# ============================================================================

def extract_dynamic_data(image_path):
    """
    Dynamically extract data from any document type.
    
    Args:
        image_path (str): Path to image file
    
    Returns:
        dict: Document metadata + extracted data
    """
    
    # Step 1: Classify document
    print("📋 Step 1: Classifying document...")
    classification = classify_document(image_path)
    
    doc_type = classification.get("document_type", "other")
    print(f"   ✓ Document Type: {doc_type}")
    print(f"   ✓ Confidence: {classification.get('confidence', 'unknown')}")
    print(f"   ✓ Description: {classification.get('description', 'N/A')}")
    
    # Step 2: Get appropriate schema
    schema = SCHEMA_MAP.get(doc_type, {
        "fields": ["all_text", "key_information", "date", "amount", "parties"]
    })
    
    # Step 3: Extract data based on schema
    print(f"\n📊 Step 2: Extracting {len(schema['fields'])} fields...")
    
    fields_list = ", ".join(schema['fields'])
    
    prompt = f"""
Extract information from this {doc_type} document.

Extract these fields: {fields_list}

Return ONLY valid JSON. Use null for missing fields.
For fields that have multiple items (like 'items' in invoices), use arrays.
Convert amounts to numbers (remove currency symbols and commas).
Use ISO format for dates (YYYY-MM-DD).

Example structure:
{{
  "field_name_1": "value",
  "field_name_2": 123.45,
  "field_name_3": ["item1", "item2"],
  "extraction_timestamp": "ISO timestamp"
}}

Be thorough and extract EXACTLY what you see.
"""
    
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
        
        extracted_data = json.loads(cleaned.strip())
        
        # Add metadata
        result = {
            "document_type": doc_type,
            "classification_confidence": classification.get("confidence"),
            "image_file": os.path.basename(image_path),
            **extracted_data
        }
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"⚠️  Extraction JSON Error: {e}")
        return {
            "document_type": doc_type,
            "error": "Extraction failed",
            "raw_response": response
        }


# ============================================================================
# EXCEL EXPORT - DYNAMIC SHEETS
# ============================================================================

def export_to_excel(documents_data, output_file="documents_extracted.xlsx"):
    """
    Export extracted data to Excel - creates separate sheets per document type.
    
    Args:
        documents_data (list): List of document dictionaries
        output_file (str): Output file path
    """
    
    # Group by document type
    grouped = {}
    for doc in documents_data:
        doc_type = doc.get("document_type", "other")
        if doc_type not in grouped:
            grouped[doc_type] = []
        grouped[doc_type].append(doc)
    
    print(f"\n📊 Creating Excel with {len(grouped)} sheets...")
    
    # Create Excel with multiple sheets
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        for doc_type, docs in grouped.items():
            df = pd.DataFrame(docs)
            
            sheet_name = doc_type.replace("_", " ").title()[:31]  # Excel limit
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"   ✓ Sheet '{sheet_name}': {len(docs)} documents")
            
            # Auto-adjust column widths
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)
            
            # Format header
            from openpyxl.styles import Font, PatternFill
            for cell in worksheet[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    print(f"\n✅ Excel created: {output_file}")


# ============================================================================
# MAIN TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("DYNAMIC DOCUMENT DIGITIZER - HANDLES ANY DOCUMENT TYPE")
    print("="*70)
    
    # Auto-detect images in directory
    image_files = []
    for ext in [".png", ".jpg", ".jpeg"]:
        image_files.extend([f for f in os.listdir(".") if f.lower().endswith(ext)])
    
    if not image_files:
        print("\n❌ ERROR: No image files found!")
        print("   Please add .png, .jpg, or .jpeg files to process")
        exit(1)
    
    print(f"\n📸 Found {len(image_files)} image(s) to process")
    
    all_extracted = []
    
    for idx, image_file in enumerate(image_files, 1):
        print(f"\n{'='*70}")
        print(f"Processing {idx}/{len(image_files)}: {image_file}")
        print(f"{'='*70}")
        
        extracted = extract_dynamic_data(image_file)
        all_extracted.append(extracted)
        
        print(f"\n📊 EXTRACTED DATA:")
        print(json.dumps(extracted, indent=2))
    
    # Export all to Excel
    print(f"\n{'='*70}")
    print("📤 Exporting all documents to Excel...")
    export_to_excel(all_extracted, "documents_extracted.xlsx")
    
    print("\n✅ DONE! Check 'documents_extracted.xlsx'")
    print("="*70)
