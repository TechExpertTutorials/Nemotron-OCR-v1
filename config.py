# config.py

OCR_ENDPOINT = "https://ai.api.nvidia.com/v1/cv/nvidia/nemotron-ocr-v1"
LLM_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
# MODEL_NAME = "meta/llama-3.1-70b-instruct"
# MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b"
MODEL_NAME = "nvidia/nemotron-3-nano-30b-a3b"

# --- SCHEMA 1: Table People Data ---
TABLE_SCHEMA = {
    "type": "object",
    "properties": {
        "people_data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "age": {"type": "integer"},
                    "country": {"type": "string"},
                    "sex": {"type": "string", "enum": ["M", "F"]},
                    "job_title": {"type": "string"}
                },
                "required": ["first_name", "last_name", "age", "country", "sex", "job_title"]
            }
        }
    },
    "required": ["people_data"]
}

# --- SCHEMA 2: FAA Medical Form ---
FAAMEDICALMODEL_SCHEMA = {
    "type": "object",
    "properties": {
        "certificate_data": {
            "type": "object",
            "properties": {
                "form_number": {"type": "string"},
                "class": {"type": "string"},
                "applicant_last_name": {"type": "string"},
                "applicant_first_name": {"type": "string"},
                "social_security_number": {"type": "string"},
                "address": {"type": "string"},
                "date_of_birth": {"type": "string"},
                "class_of_medical": {"type": "string"},
                "date_of_examination": {"type": "string"},
                "examiner_name": {"type": "string"}
            }
        }
    }
}

# --- NEW SCHEMA 3: Driver's License Data ---
# Custom schema for dl1.png
DRIVERLICENSEMODEL_SCHEMA = {
    "type": "object",
    "properties": {
        "license_data": {
            "type": "object",
            "properties": {
                "jurisdiction": {"type": "string"},
                "dln": {"type": "string"}, # Driver's License Number
                "full_name": {"type": "string"},
                "full_address": {"type": "string"},
                "dob": {"type": "string"}, # Date of Birth
                "sex": {"type": "string"},
                "hgt": {"type": "string"}, # Height
                "class": {"type": "string"},
                "organ_donor": {"type": "boolean"},
                "restr": {"type": "string"} # Restrictions
            }
        }
    }
}

INVOICE_SCHEMA = {
    "type": "object",
    "properties": {
        "invoice_data": {
            "type": "object",
            "properties": {
                # --- DOCUMENT HEADER INFO ---
                "document_header": {
                    "type": "object",
                    "properties": {
                        "vendor_name": {"type": "string", "description": "e.g., GG Mobile company"},
                        "vendor_address": {"type": "string", "description": "Complete vendor address"},
                        "vendor_gst": {"type": "string", "description": "Vendor GST Number"},
                        "bill_to_name": {"type": "string"},
                        "bill_to_address": {"type": "string"},
                        "invoice_number": {"type": "string", "description": "e.g., INV-038"},
                        "invoice_date": {"type": "string", "description": "Date format DD/MM/YYYY, e.g., 07/01/2025"},
                    },
                    "required": ["vendor_name", "invoice_number", "invoice_date"]
                },
                # --- MAIN LINE ITEM TABLE ---
                "line_items": {
                    "type": "array",
                    "description": "A list of all products purchased",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sl_no": {"type": "integer", "description": "Serial Number"},
                            "description": {"type": "string"},
                            "quantity": {"type": "integer"},
                            "rate": {"type": "number", "description": "Rate per unit, excluding commas/dots"},
                            "amount": {"type": "number", "description": "Total amount for item, excluding commas/dots"}
                        },
                        "required": ["sl_no", "description", "quantity", "rate", "amount"]
                    }
                },
                # --- TOTALS AND SUMMARY ---
                "totals_summary": {
                    "type": "object",
                    "properties": {
                        "total_quantity": {"type": "integer"},
                        "subtotal": {"type": "number", "description": "The base amount of $82 978,00"},
                        "discount_percentage": {"type": "number", "description": "The 4% discount value"},
                        "discount_amount": {"type": "number", "description": "The -$3 319,12 value"},
                        "vat_percentage": {"type": "number", "description": "The 2% VAT value"},
                        "vat_amount": {"type": "number", "description": "The $1 593,18 value"},
                        "grand_total": {"type": "number", "description": "The total of $81 252,06"},
                        "total_amount_in_words": {"type": "string", "description": "Textual representation of total amount"},
                        "paid_amount": {"type": "number"},
                        "balance_due": {"type": "number"},
                        "payment_status": {"type": "string", "enum": ["Paid", "Unpaid", "Partial"]}
                    },
                    "required": ["subtotal", "discount_amount", "vat_amount", "grand_total", "total_amount_in_words"]
                },
                # --- SIGNATURE VALIDATION ---
                "signature_check": {
                    "type": "object",
                    "properties": {
                        "signature_present": {"type": "boolean", "description": "Look for handwritten signature in the authorized signatory box"},
                        "signature_name": {"type": "string", "description": "Name of authorized signatory if legible"}
                    }
                }
            },
            "required": ["document_header", "line_items", "totals_summary"]
        }
    }
}
