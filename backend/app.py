from fastapi import FastAPI, UploadFile, File, Form
import json
import os
import re
from typing import Optional

from backend.kb import KnowledgeBase
from backend.llm_agent import LLMAgent

app = FastAPI()

kb = KnowledgeBase()
llm = LLMAgent()

HTML_DIR = "data/html"
os.makedirs(HTML_DIR, exist_ok=True)

# Keep track of the last uploaded HTML filename so script generation uses it automatically
LAST_HTML_FILE: Optional[str] = None


# ---------------------------------------------------
# CLEAN JSON / CODE-FENCE OUTPUT (remove ```json and ``` blocks)
# ---------------------------------------------------
def clean_json_output(text: str) -> str:
    """
    Removes ```json, ```python, and all ``` code fences.
    Ensures the model output becomes valid JSON or raw python script.
    """
    if not isinstance(text, str):
        return text
    # Remove triple backtick opening like ```json or ```python or ```
    text = re.sub(r"```[a-zA-Z0-9_-]*", "", text)
    # Remove stray ```
    text = text.replace("```", "")
    # Trim whitespace
    return text.strip()


# ---------------------------------------------------
# DOCUMENT INGESTION
# ---------------------------------------------------
@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingest support documents (md, txt, json, pdf-as-text, etc.)
    """
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except Exception:
        # Fallback: try latin-1
        text = raw.decode("latin-1", errors="ignore")

    kb.add_document(text, source=file.filename)
    return {"message": f"{file.filename} ingested.", "source": file.filename}


@app.post("/ingest_html")
async def ingest_html(file: UploadFile = File(...)):
    """
    Ingest and store an HTML file. The endpoint will save the HTML to data/html/{filename},
    index it into the KB, and set LAST_HTML_FILE so generate_script uses it automatically.
    """
    global LAST_HTML_FILE

    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except Exception:
        text = raw.decode("latin-1", errors="ignore")

    # Save HTML to disk
    safe_name = file.filename
    path = os.path.join(HTML_DIR, safe_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    # Add HTML content to knowledge base as well
    kb.add_document(text, source=file.filename)

    # Track last uploaded HTML file
    LAST_HTML_FILE = safe_name

    return {"message": "HTML file stored and ingested.", "html_file": LAST_HTML_FILE}


# ---------------------------------------------------
# GENERATE TEST CASES (RAG -> LLM)
# ---------------------------------------------------
@app.post("/generate_testcases")
async def generate_testcases(query: str = Form(...)):
    """
    Generate grounded test cases from uploaded documents.
    Returns parsed JSON test cases when possible; otherwise returns raw model output and error.
    """
    docs = kb.query(query, top_k=6)

    context = ""
    for d in docs:
        # include short source header and the text chunk
        context += f"[{d['source']}]\n{d['text']}\n\n"

    prompt = f"""
You are a senior QA engineer. Use ONLY the context below to generate STRICT JSON test cases.

CONTEXT:
{context}

USER REQUEST:
{query}

REQUIREMENTS:
- Output MUST be ONLY valid JSON.
- JSON must be a list: [ {{...}}, {{...}} ]
- Use double quotes for keys and values.
- NO backticks, NO code fences (```), NO explanations, NO commentary.
- Each test case must contain exactly these fields:
  "Test_ID", "Feature", "Scenario", "Steps", "Expected_Result", "Grounded_In"

RETURN ONLY THE JSON (do not wrap in markdown/code fences):
"""

    # Query the LLM
    output = llm.generate(prompt)

    # Clean output from possible code-fences
    cleaned = clean_json_output(output)

    try:
        parsed = json.loads(cleaned)
        return {"ok": True, "testcases": parsed}
    except Exception as e:
        # Return the cleaned raw text and the parsing error for debugging
        return {"ok": False, "error": str(e), "raw": cleaned}

@app.post("/generate_script")
async def generate_script(test_case: str = Form(...)):
    """
    Generate a Python Selenium script for the provided test case JSON.
    Uses the most recently uploaded HTML file (LAST_HTML_FILE) to derive selectors.
    Ensures PASS / FAIL messages always appear.
    """
    global LAST_HTML_FILE

    if LAST_HTML_FILE is None:
        return {"ok": False, "error": "No HTML file has been uploaded yet."}

    # Build the full absolute path to the HTML file on disk
    html_path = os.path.abspath(os.path.join(HTML_DIR, LAST_HTML_FILE))

    if not os.path.exists(html_path):
        return {"ok": False, "error": f"HTML file not found at: {html_path}"}

    # Convert path for Selenium (file:/// format)
    selenium_path = "file:///" + html_path.replace("\\", "/")

    # Load HTML content
    with open(html_path, "r", encoding="utf-8") as f:
        html_text = f.read()

    # Parse test case JSON
    try:
        test_case_obj = json.loads(test_case)
    except Exception as e:
        return {"ok": False, "error": f"Invalid test_case JSON: {e}"}

    # -------------------------------
    # Prompt that forces PASS/FAIL printing
    # -------------------------------
    prompt = f"""
You are a Python Selenium automation engineer.

Generate a complete Python Selenium test script for this test case:
{json.dumps(test_case_obj, indent=2)}

The HTML file is located at this exact path:
{selenium_path}

Insert this EXACT line in the script:
html_file_path = "{selenium_path}"

HTML content for selectors:
{html_text}

STRICT RULES:
- Use Selenium with webdriver.Chrome().
- Use WebDriverWait for all interactions.
- Use ONLY selectors that exist in the HTML.
- DO NOT invent selectors.
- The script MUST have this structure:

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

html_file_path = "{selenium_path}"

driver = webdriver.Chrome()
driver.get(html_file_path)
wait = WebDriverWait(driver, 10)

try:
    # steps...
    print("TEST PASSED: <reason>")
except Exception as e:
    print("TEST FAILED:", e)
finally:
    print("Test completed.")
    input("Press ENTER to close browser...")
    driver.quit()

- DO NOT wrap code in backticks.
- RETURN ONLY RAW PYTHON CODE.
"""

    # Ask LLM for script
    script_output = llm.generate(prompt, max_length=2048)

    # Clean script (remove ``` if present)
    cleaned_script = clean_json_output(script_output)

    return {
        "ok": True,
        "script": cleaned_script,
        "html_used": LAST_HTML_FILE,
        "selenium_path": selenium_path
    }
