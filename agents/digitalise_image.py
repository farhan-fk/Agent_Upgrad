"""
===============================================================================
SIMPLIFIED: DOCUMENT DIGITIZER - EXTRACTION ONLY
===============================================================================

PURPOSE: Extract data from documents and save to Excel - NO VALIDATION
Just digitize documents as-is for data entry automation.

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
# EXTRACTION FUNCTION - SIMPLE VERSION
# ============================================================================

def extract_claim_data(image_path, max_retries=2):
    """
    Extract data from claim document image - AS-IS.
    With retry mechanism if JSON parsing fails.
    
    Args:
        image_path (str): Path to image file
        max_retries (int): Maximum retry attempts if parsing fails
    
    Returns:
        dict: Extracted claim data exactly as shown in document
    """
    
    prompt = """
Extract ALL information from this insurance claim document.

Return ONLY valid JSON with these exact fields (use null if not found):

{
  "insurance_company": "company name",
  "police_report_available": "YES/NO/null",
  "total_claim_amount": number,
  "injury_claim": number,
  "property_claim": number,
  "vehicle_claim": number,
  "vehicle_make": "text",
  "vehicle_model": "text",
  "vehicle_year": number,
  "extraction_timestamp": "ISO timestamp"
}

IMPORTANT: 
- Extract text EXACTLY as shown 
- Convert amounts to numbers (remove $, commas)
- Use null for missing fields
- Return only JSON, no extra text
"""
    
    previous_response = None
    
    for attempt in range(max_retries + 1):
        # If this is a retry, modify prompt to include previous failed attempt
        if previous_response:
            retry_prompt = f"""
Your previous response was INVALID and could not be parsed as JSON.

PREVIOUS RESPONSE (INCORRECT):
{previous_response}

Please try again. Extract the information from the insurance claim document and return ONLY valid JSON with the exact schema requested. No markdown, no extra text, just pure JSON.
"""
            response = get_completion_with_image(retry_prompt, image_path)
            print(f"🔄 Retry attempt {attempt}/{max_retries}...")
        else:
            # First attempt
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
            
            # Validate schema (check if required fields exist)
            required_fields = [
                "insurance_company", "police_report_available", 
                "total_claim_amount", "injury_claim", "property_claim",
                "vehicle_claim", "vehicle_make", "vehicle_model", 
                "vehicle_year", "extraction_timestamp"
            ]
            
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields and attempt < max_retries:
                print(f"⚠️  Missing fields: {missing_fields}")
                previous_response = response
                continue  # Try again
            
            if attempt > 0:
                print(f"✅ Success on retry {attempt}!")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON Error: {e}")
            
            if attempt < max_retries:
                # Save failed response for next retry
                previous_response = response
            else:
                # Final attempt failed
                print(f"❌ All {max_retries + 1} attempts failed")
                return {"error": "Parse failed after retries", "raw_response": response}

# ============================================================================
# EXCEL EXPORT - APPEND MODE (UPDATES EXISTING FILE)
# ============================================================================

def export_to_excel(claims_data, output_file="claims_extracted.xlsx"):
    """
    Export extracted data to Excel - APPENDS to existing file if present.
    
    Args:
        claims_data (list): List of claim dictionaries
        output_file (str): Output file path
    """
    # Convert new data to DataFrame
    new_df = pd.DataFrame(claims_data)
    
    # Check if file already exists
    if os.path.exists(output_file):
        print(f"📄 Found existing file: {output_file}")
        print("📝 Appending new data to existing rows...")
        
        try:
            # Read existing data
            existing_df = pd.read_excel(output_file, sheet_name='Claims')
            
            # Combine old + new data
            df = pd.concat([existing_df, new_df], ignore_index=True)
            
            print(f"   Previous rows: {len(existing_df)}")
            print(f"   New rows: {len(new_df)}")
            print(f"   Total rows now: {len(df)}")
        except Exception as e:
            print(f"⚠️  Error reading existing file: {e}")
            print("   Creating new file instead...")
            df = new_df
    else:
        print(f"📄 Creating new file: {output_file}")
        df = new_df
    
    # Rename columns for better readability
    column_mapping = {
        "insurance_company": "Insurance Company",
        "police_report_available": "Police Report",
        "total_claim_amount": "Total Amount",
        "injury_claim": "Injury Claim",
        "property_claim": "Property Claim",
        "vehicle_claim": "Vehicle Claim",
        "vehicle_make": "Vehicle Make",
        "vehicle_model": "Vehicle Model",
        "vehicle_year": "Vehicle Year",
        "extraction_timestamp": "Extracted On"
    }
    
    df = df.rename(columns=column_mapping)
    
    # Export to Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Claims', index=False)
        
        # Basic formatting
        worksheet = writer.sheets['Claims']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 40)
        
        # Format header
        from openpyxl.styles import Font, PatternFill
        
        for cell in worksheet[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
    
    print(f"✅ Excel created: {output_file}")
    print(f"📊 Rows: {len(claims_data)}")

# ============================================================================
# MAIN TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SIMPLE DOCUMENT DIGITIZER - EXTRACTION ONLY")
    print("="*70)
    
    # Auto-detect image
    image_file = None
    for ext in ["sample_claim.png", "sample_claim.jpg", "sample_claim.jpeg"]:
        if os.path.exists(ext):
            image_file = ext
            break
    
    # Extract data
    if not image_file:
        print("\n❌ ERROR: No sample claim image found!")
        print("   Please add a file named: sample_claim.png/jpg/jpeg")
        exit(1)
    
    print(f"\n📸 Processing: {image_file}")
    extracted = extract_claim_data(image_file)
    
    print("\n📊 EXTRACTED DATA:")
    print(json.dumps(extracted, indent=2))
    
    # Export to Excel
    print("\n📤 Exporting to Excel...")
    export_to_excel([extracted], "claims_extracted.xlsx")
    
    print("\n✅ DONE! Check 'claims_extracted.xlsx'")
    print("="*70)
