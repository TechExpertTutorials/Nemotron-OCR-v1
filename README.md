# Nemotron-OCR-v1

🚀 Intelligent OCR & Data Structuring Pipeline
Powered by NVIDIA NIM (Nemotron-3)
This repository contains a production-ready Python pipeline for converting raw document images (Invoices, ID Cards, Medical Forms) into validated, hierarchical JSON.
By combining NVIDIA Nemotron OCR with the Nemotron-3-Super-120B LLM, we achieve human-level extraction accuracy while strictly enforcing complex business schemas.
________________________________________
🛠️ Key Features
•	Dual-Stage Processing:
1.	Stage 1 (OCR): Extracts raw text and per-word confidence scores.
2.	Stage 2 (LLM): Structures "Clean Text" into JSON using Pydantic-style schemas.
•	Zero-Temperature Logic: Uses temperature=0.0 for deterministic, repeatable results—critical for financial and medical data.
•	Token Efficiency: Implements a "Clean Text" pass to reduce LLM input tokens by ~60%, preventing gateway timeouts.
•	Hierarchical Schema Support: Handles nested tables, header metadata, and totals from complex invoices.
________________________________________
📂 Project Structure
Plaintext
.
├── images/               # Input: dl1.png, table1.png, Invoice1.png
├── output/               # Output: Raw .txt, Metadata .txt, and Final .json
├── config.py             # API Endpoints & JSON Schema Definitions
├── run_ocr.py            # Main Execution Logic
├── my_timer.py           # Custom Decorator for Performance Benchmarking
└── README.md             # You are here!
________________________________________
🚀 Getting Started
1. Prerequisites
•	Hardware: Optimized for high-performance laptops (Tested on MSI Katana).
•	Environment: Python 3.10+ (Running on WSL2 / Ubuntu recommended).
•	API Key: Obtain your NGC_API_CLOUD_KEY from the NVIDIA API Catalog.
2. Setup
Bash
# Clone the repo
git clone https://github.com/your-username/nemotron-ocr-structuring.git
cd nemotron-ocr-structuring

# Install dependencies
pip install requests
3. Configuration
Export your API key to your environment:
Bash
export NGC_API_CLOUD_KEY="your_actual_key_here"
4. Run the Pipeline
Bash
python3 run_ocr.py
________________________________________
🧠 Supported Models
Task	Model Name	Use Case
OCR	nvidia/nemotron-ocr-v1	High-fidelity text & label detection.
LLM (Fast)	nvidia/nemotron-3-nano-30b-a3b	Rapid extraction for simple IDs and tables.
LLM (Heavy)	nvidia/nemotron-3-super-120b-a12b	Complex reasoning for Invoices & FAA Forms.
________________________________________
💡 Troubleshooting (Boise Lab Notes)
•	The "60-Second Wall": If the 120B model hangs, ensure you are using clean_text instead of metadata_raw to stay under the gateway timeout.
•	Field Duplication: If dates appear twice (e.g., dob_1, dob_2), ensure temperature is set to 0.0 in the run_ocr.py payload.
•	Connection Errors: Using requests.Session() is required to maintain a stable TCP handshake with the NVIDIA NIM endpoints.
________________________________________
📺 Watch the Tutorial
This code is part of the @techexpert series on advanced AI automation.
[Click here to watch the full walkthrough on YouTube]

