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
import pandas as pd
from datetime import datetime
import pdfplumber

load_dotenv()
client = OpenAI()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber (handles tables well)."""
    text_parts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Extract text
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- Page {page_num} ---")
                text_parts.append(page_text)
            
            # Extract tables as formatted text
            tables = page.extract_tables()
            for table_num, table in enumerate(tables, 1):
                text_parts.append(f"\n[Table {table_num}]")
                for row in table:
                    text_parts.append(" | ".join(str(cell) if cell else "" for cell in row))
    
    return "\n".join(text_parts)

# ============================================================================
# EXTRACTION FUNCTION - INVOICE VERSION
# ============================================================================

def extract_invoice_data(pdf_path):
    """
    Extract data from invoice PDF document.
    
    Args:
        pdf_path (str): Path to PDF file
    
    Returns:
        dict: Extracted invoice data exactly as shown in document
    """
    
    prompt = """
Extract ALL information from this invoice document.

Return ONLY valid JSON with these exact fields (use null if not found):

{
  "company_name": "text",
  "company_gst": "text",
  "invoice_number": "text",
  "invoice_date": "text",
  "po_number": "text",
  "customer_name": "text",
  "customer_gst": "text",
  "subtotal": number,
  "cgst": number,
  "sgst": number,
  "total_amount": number,
  "extraction_timestamp": "ISO timestamp"
}

IMPORTANT: 
- Extract text EXACTLY as shown 
- Convert amounts to numbers (remove ₹, Rs, $, commas)
- Use null for missing fields
- Return only JSON, no extra text
"""
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    # Get response from LLM
    messages = [{"role": "user", "content": prompt + f"\n\nDocument:\n{pdf_text}"}]
    api_response = client.responses.create(
        model="gpt-4o-mini",
        input=messages,
        temperature=0
    )
    response = api_response.output_text
    
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
        return result
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON Error: {e}")
        return {"error": "Parse failed", "raw_response": response}

# ============================================================================
# EXCEL EXPORT - APPEND MODE (UPDATES EXISTING FILE)
# ============================================================================

def export_to_excel(invoice_data, output_file="invoices_extracted.xlsx"):
    """
    Export extracted data to Excel - APPENDS to existing file if present.
    
    Args:
        invoice_data (list): List of invoice dictionaries
        output_file (str): Output file path
    """
    # Column mapping for better readability
    column_mapping = {
        "company_name": "Company Name",
        "company_gst": "Company GST",
        "invoice_number": "Invoice No",
        "invoice_date": "Date",
        "po_number": "PO Number",
        "customer_name": "Customer",
        "customer_gst": "Customer GST",
        "subtotal": "Subtotal",
        "cgst": "CGST",
        "sgst": "SGST",
        "total_amount": "Total Amount",
        "extraction_timestamp": "Extracted On"
    }
    
    # Convert new data to DataFrame
    new_df = pd.DataFrame(invoice_data)
    
    # Check if file already exists
    if os.path.exists(output_file):
        print(f"📄 Found existing file: {output_file}")
        print("📝 Appending new data to existing rows...")
        
        try:
            # Read existing data
            existing_df = pd.read_excel(output_file, sheet_name='Invoices')
            
            # Rename new_df columns to match existing (before concat)
            new_df = new_df.rename(columns=column_mapping)
            
            # Combine old + new data
            df = pd.concat([existing_df, new_df], ignore_index=True)
            
            print(f"   Previous rows: {len(existing_df)}")
            print(f"   New rows: {len(new_df)}")
            print(f"   Total rows now: {len(df)}")
        except Exception as e:
            print(f"⚠️  Error reading existing file: {e}")
            print("   Creating new file instead...")
            df = new_df
            df = df.rename(columns=column_mapping)
    else:
        print(f"📄 Creating new file: {output_file}")
        df = new_df
        df = df.rename(columns=column_mapping)
    
    # Export to Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Invoices', index=False)
        
        # Basic formatting
        worksheet = writer.sheets['Invoices']
        
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
    print(f"📊 Invoices: {len(invoice_data)}")

# ============================================================================
# MAIN TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INVOICE DIGITIZER - PDF ONLY")
    print("="*70)
    
    # Check for PDF
    pdf_file = "sample_invoice.pdf"
    
    if not os.path.exists(pdf_file):
        print("\n⚠️  PDF not found!")
        print(f"   Place '{pdf_file}' in this directory")
        exit(1)
    
    # Extract data
    print(f"\n📄 Processing PDF: {pdf_file}")
    extracted = extract_invoice_data(pdf_path=pdf_file)
    
    print("\n📊 EXTRACTED DATA:")
    print(json.dumps(extracted, indent=2))
    
    # Export to Excel
    print("\n📤 Exporting to Excel...")
    export_to_excel([extracted], "invoices_extracted.xlsx")
    
    print("\n✅ DONE! Check 'invoices_extracted.xlsx'")
    print("="*70)
