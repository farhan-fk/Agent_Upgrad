# Invoice Digitizer with Validation
## Teaching Presentation

---

## Slide 1: Overview - The Problem

**Challenge:**
- Manual data entry from PDF invoices → Errors, slow, expensive
- Need automated extraction BUT maintain data quality

**Solution:**
- LLM extracts → Python validates → Route by quality

**Key Insight:**
> Don't trust LLM output blindly. Add a validation layer.

---

## Slide 2: 4-Step Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   STEP 1     │     │   STEP 2     │     │   STEP 3     │     │   STEP 4     │
│   Extract    │ --> │   Validate   │ --> │   Decision   │ --> │   Export     │
│              │     │              │     │              │     │              │
│ PDF → LLM    │     │ Run 6 checks │     │ Valid? Y/N   │     │ Excel        │
│ Returns JSON │     │ Get errors   │     │              │     │ (2 sheets)   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

**Result:**
- ✅ Green Sheet: Validated data (ready to use)
- ⚠️ Red Sheet: Needs human review (with specific errors)

---

## Slide 3: The 6 Validation Checks

| # | Check | Why It Matters | Example Error |
|---|-------|----------------|---------------|
| 1️⃣ | **Required Fields** | Can't process without basics | Missing invoice_number |
| 2️⃣ | **Data Types** | Numbers must be numeric | "₹1,234" instead of 1234 |
| 3️⃣ | **GST Format** | Compliance/legal requirement | 14 chars instead of 15 |
| 4️⃣ | **Math Consistency** | Subtotal+Tax = Total? | Total=1000 but sum=950 |
| 5️⃣ | **Date Logic** | No future dates | Invoice dated 2027 |
| 6️⃣ | **Business Rules** | Total must be positive | Total = -500 or 0 |

**Function:** `validate_invoice_data(invoice_data)` → `(is_valid, errors)`

---

## Slide 4: Code Flow - Decision Point

```python
# After extraction
extracted = extract_invoice_data(pdf_path)

# Run validation
is_valid, validation_errors = validate_invoice_data(extracted)

# Decision: Where does this data go?
if is_valid:
    validated_invoices.append(extracted)
    # → Green sheet (ready for production)
else:
    extracted["validation_errors"] = " | ".join(validation_errors)
    review_invoices.append(extracted)
    # → Red sheet (human must review)
```

**Key:** Data is never lost, just routed appropriately.

---

## Slide 5: Example - Failed Validation

**Extracted Data:**
```json
{
  "invoice_number": "",
  "customer_name": "Acme Corp",
  "total_amount": -500,
  "subtotal": 400,
  "cgst": 50,
  "sgst": 50,
  "company_gst": "ABC123"
}
```

**Validation Result:**
```
⚠️  FAILED - 4 errors:
1. Missing required field: invoice_number
2. total_amount cannot be negative: -500
3. Math error: 400 + 50 + 50 = 500, but Total = -500
4. company_gst must be 15 characters: ABC123
```

**Action:** → Sent to "Needs_Review" sheet with error details

---

## Slide 6: Key Takeaways

1. **Quality Gate Pattern:**
   - LLM outputs → Validation layer → Decision routing
   - Prevents bad data entering production systems

2. **Fail-Open Philosophy:**
   - Failed validation ≠ data discarded
   - Route to human review instead

3. **Error Specificity:**
   - Don't just say "invalid"
   - Tell user EXACTLY what's wrong: "GST must be 15 chars, got 14"

4. **Real-World Impact:**
   - Catches LLM hallucinations
   - Detects OCR errors
   - Enforces business rules automatically

---

## Bonus Slide: Math Validation Deep Dive

**Why floating-point tolerance?**

```python
calculated_total = subtotal + cgst + sgst
if abs(calculated_total - total) > 0.01:  # Not == !
    errors.append(...)
```

**Reason:**
- Floating point: 0.1 + 0.2 ≠ 0.3 in computers
- LLM might round differently than Python
- Allow ±0.01 tolerance = 1 cent

**Bad:** `if calculated_total != total`  
**Good:** `if abs(difference) > 0.01`

---

## Code Reference

**File:** `digitalise_pdf.py`

**Key Functions:**
- `validate_invoice_data()` - Lines 62-137
- `extract_invoice_data()` - Lines 143-222
- `export_to_excel_with_validation()` - Lines 228-336

**Run:** `python digitalise_pdf.py`
**Output:** `invoices_extracted.xlsx` (2 sheets)

---

**Questions?**
