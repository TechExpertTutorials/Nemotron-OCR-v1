"""
conda create env -n nemotron-ocr python=3.12 requests
conda activate nemotron-ocr
"""


import os
import sys
import base64
import json
import requests
import config # Custom config.py in the same folder
from my_timer import my_timer

# --- 1. CONFIGURATION ---
API_KEY = os.getenv("NGC_API_CLOUD_KEY")
IMAGE_DIR = "images"
OUTPUT_DIR = "output"


# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

if not API_KEY:
    print("❌ ERROR: 'NGC_API_CLOUD_KEY' not found.")
    sys.exit(1)

# --- 2. CORE FUNCTIONS ---

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
    
def get_dual_text_formats(ocr_result):
    """
    Returns two strings:
    1. metadata_text: '0.900 >> word' format
    2. clean_text: Only the 'word' values
    """
    metadata_lines = []
    clean_lines = []
    
    data_items = ocr_result.get("data", [])
    if not data_items:
        return "", ""

    for item in data_items:
        for detection in item.get("text_detections", []):
            prediction = detection.get("text_prediction", {})
            words_list = prediction.get("words", [])
            
            meta_parts = []
            clean_parts = []
            
            # Scenario A: Word-level details available
            if words_list:
                for word_obj in words_list:
                    word = word_obj.get("word", "")
                    conf = word_obj.get("confidence", 0.0)
                    meta_parts.append(f"{conf:.3f} >> {word}")
                    clean_parts.append(word)
            # Scenario B: Fallback to detection-level
            else:
                full_text = prediction.get("text", "")
                conf = prediction.get("confidence", 0.0) 
                if full_text:
                    for word in full_text.split():
                        meta_parts.append(f"{conf:.3f} >> {word}")
                        clean_parts.append(word)
            
            if meta_parts:
                metadata_lines.append("  ".join(meta_parts))
                clean_lines.append(" ".join(clean_parts))
                
    return "\n".join(metadata_lines), "\n".join(clean_lines)

@my_timer
def structure_with_schema(clean_text, user_prompt, schema):
    session = requests.Session()
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": config.MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a professional data parser. Return ONLY valid JSON."},
            {"role": "user", "content": f"{user_prompt}\n\nText:\n{clean_text}"}
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object", "schema": schema}
    }

    try:
        response = session.post(
            config.LLM_ENDPOINT, 
            headers=headers, 
            json=payload,
            timeout=(10,120)
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content'].strip()
        if "```" in content:
            content = content.split("```")[1].replace("json", "", 1).strip()
        return json.loads(content)
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return None

@my_timer
def run_ocr_extract(image_path):
    print(f"🚀 OCR: {image_path}...")
    ocr_headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    ocr_payload = {
        "input": [{"type": "image_url", "url": f"data:image/png;base64,{encode_image(image_path)}"}],
        "merge_levels": ["paragraph"]
    }
    res = requests.post(config.OCR_ENDPOINT, headers=ocr_headers, json=ocr_payload)
    return res


def process_batch(file_pairs):
    for pair in file_pairs:
        test_slug = pair['test_name'].replace(' ', '_')
        print(f"\n--- Processing: {pair['test_name']} ---")

        image_path = os.path.join(IMAGE_DIR, pair['image'])
        if not os.path.exists(image_path):
            print(f"⚠️ File not found: {image_path}. Skipping...")
            continue

        current_schema = pair['output_schema']
        if isinstance(current_schema, str):
            current_schema = getattr(config, current_schema)

        res = run_ocr_extract(image_path)

        if res.status_code == 200:
            ocr_json = res.json()
            # UPDATED: Get both versions of the text
            meta_text, clean_text = get_dual_text_formats(ocr_json)

            if meta_text.strip():
                # SAVE 1: Raw metadata version (confidence >> word)
                meta_filename = os.path.join(OUTPUT_DIR, f"{test_slug}_metadata_raw.txt")
                with open(meta_filename, "w", encoding="utf-8") as f:
                    f.write(meta_text)
                
                # SAVE 2: Clean version (words only)
                clean_filename = os.path.join(OUTPUT_DIR, f"{test_slug}_clean_text.txt")
                with open(clean_filename, "w", encoding="utf-8") as f:
                    f.write(clean_text)
                
                print(f"📄 Saved metadata text to: {meta_filename}")
                print(f"📄 Saved clean text to: {clean_filename}")

                # STEP 2: STRUCTURED EXTRACTION (Using the metadata version for highest accuracy)
                print(f"🧠 Extracting data into JSON...")
                final_json = structure_with_schema(clean_text, pair['prompt'], current_schema)

                if final_json:
                    json_filename = os.path.join(OUTPUT_DIR, f"{test_slug}_structured.json")
                    with open(json_filename, "w", encoding="utf-8") as f:
                        json.dump(final_json, f, indent=4)
                    print(f"✅ Success! Structured data saved to: {json_filename}")
            else:
                print("⚠️ OCR returned no text.")
        else:
            print(f"❌ OCR Request failed: {res.status_code}")


if __name__ == "__main__":
    file_pairs = [
        {
            "test_name": "Detailed Table Extraction",
            "prompt": "Extract all data from this table according to the defined schema. Use the provided confidence scores to resolve any visual ambiguities.",
            "image": "table1.png",
            "output_schema": config.TABLE_SCHEMA
        },
        {
            "test_name": "ID Card OCR and Signature Analysis", 
            "prompt": "Extract all fields from this Driver's License into the requested schema. Pay close attention to the DLN and DOB fields. Use confidence scores to verify critical information.", 
            "image": "dl1.png", 
            "output_schema": config.DRIVERLICENSEMODEL_SCHEMA 
        },
        {
            "test_name": "FAA Medical Form OCR",
            "prompt": "Extract all data from this FAA Medical Certificate as a JSON object. Give dates in MM/DD/YYYY format. Any blank entries should be indicated with 2 double quotes.",
            "image": "Document.jpg",
            "output_schema": config.FAAMEDICALMODEL_SCHEMA
        },
        {
            "test_name": "Invoice OCR",
            "prompt": "Extract all data from this Invoice as a JSON object. Give dates in MM/DD/YYYY format. Any blank entries should be indicated with 2 double quotes.",
            "image": "Invoice1.png",
            "output_schema": config.INVOICE_SCHEMA
        }
    ]

    process_batch(file_pairs)
