# 🤖 Autonomous QA Agent  
### _Test Case Generator + Selenium Script Generator_  
### _FastAPI · Streamlit · Gemini AI · Python Selenium_

---

## 📌 Overview

**Autonomous QA Agent** is an end-to-end AI-powered system that automatically:

- 📄 Ingests requirement documents (MD, TXT, JSON)  
- 🌐 Ingests an HTML UI file for DOM-aware script generation  
- 🧠 Generates grounded QA test cases using **Gemini AI**  
- 📝 Produces fully runnable **Python Selenium** scripts  
- 🧪 Verifies UI behavior using selectors from the actual HTML  
- ⏳ Keeps the browser open until the user closes it manually  
- 🖥️ Provides a clean Streamlit-based web interface  

This project helps testers automate the complete QA lifecycle:  
**requirements → test cases → automation scripts → execution**.

---

## 🛠️ Architecture

project/
│
├── backend/ # FastAPI backend
│ ├── app.py # API routes
│ ├── kb.py # Knowledge base engine
│ ├── llm_agent.py # Gemini LLM wrapper
│
├── frontend/
│ ├── streamlit_app.py # Streamlit web UI
│
├── assets/ # Sample specs + HTML
│
├── data/ # Vector store (auto generated)
│
├── requirements.txt # Python deps
├── .gitignore
└── README.md


---

## ⚙️ Features

### ✅ **1. Document Ingestion**
Upload any number of supporting documents:
- `product specifications`
- `API docs`
- `test guidelines`
- `JSON configs`

FastAPI stores them in a simple in-memory knowledge base.

---

### ✅ **2. HTML UI Ingestion**
Upload the UI file (`checkout.html` or any HTML).

The system:
- Stores the file
- Parses selectors
- Remembers the *last uploaded* HTML  
- Uses that DOM for **accurate Selenium selectors**

---

### ✅ **3. Test Case Generation (Gemini AI)**  
Given a prompt (example: _“Generate test cases for discount code feature”_):

✔ Returns **valid JSON only**  
✔ Each test case contains:
Test_ID
Feature
Scenario
Steps
Expected_Result
Grounded_In
✔ Cleans any invalid characters using regex  
✔ Rejects markdown or code blocks

---

### ✅ **4. Selenium Script Generation**
For any selected test case:

✔ Uses the last uploaded HTML selectors  
✔ Avoids inventing selectors  
✔ Creates a full runnable script:
- Chrome driver
- Explicit waits (WebDriverWait)
- Assertions
- Correct file path (`file:///…/checkout.html`)
- Keeps browser open:  
  ```python
  print("Test complete. Browser will remain open...")
  input("Press ENTER to close browser...")
  driver.quit()
