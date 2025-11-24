# 🤖 Autonomous QA Agent  
### _AI-Powered Test Case Generator + Selenium Script Generator_  
### _FastAPI · Streamlit · Gemini AI · Python Selenium_

---

## 📌 Overview

**Autonomous QA Agent** is a complete AI-driven testing system designed to assist QA engineers by automating the core testing workflow:

- 📄 Ingest requirement/specification documents (MD, TXT, JSON)  
- 🌐 Ingest HTML UI files to extract real DOM selectors  
- 🧠 Generate context-aware test cases grounded strictly in uploaded documents  
- 📝 Auto-generate **real Selenium Python scripts** using actual DOM selectors  
- 🧪 Verify UI changes using explicit waits and element assertions  
- ⏳ Keep browser open after execution for manual inspection  
- 🖥️ Provide an intuitive Streamlit user interface  

This system automates the QA lifecycle:  
**Requirements → Test Cases → Automated Selenium Scripts → Execution.**

---


Each component works together to create a fully autonomous testing workflow.

---

# ⚙️ Features & How They Work

---

## ✅ **1. Document Ingestion (Knowledge Base)**

You can upload multiple supporting files:  
✔ Product specs  
✔ UI/UX guidelines  
✔ Technical notes  
✔ JSON config rules  
✔ Error documentation  

**How it works internally:**
- FastAPI receives and decodes the uploaded file  
- The file content is stored in memory + persisted in a vector directory  
- The KnowledgeBase (`kb.py`) uses simple document storage (text chunks + metadata)  
- When generating test cases, the system retrieves the most relevant documents  

Stores MD/TXT/JSON documents.

---

## ✅ **2. HTML UI Ingestion (DOM Source for Selenium Script Generator)**

Upload the **actual HTML file** that the Selenium script should automate (“checkout.html” or any UI).

**Why this matters:**
- The AI reads the structure of the HTML  
- Extracts real selectors (IDs, names, classes)  
- Prevents hallucinated selectors  
- Ensures Selenium scripts are *actually runnable*  


Also, the backend remembers:
So script generation always uses the *latest* HTML.

---

## ✅ **3. Test Case Generation (Gemini AI)**

You type any QA prompt, for example:


The system also:
- Removes backticks with regex  
- Ensures JSON loads successfully  
- Stores test cases inside Streamlit session  

---

## 📄 Example Output (Generated Test Case)

```json
{
  "Test_ID": "TC_DISCOUNT_001",
  "Feature": "Discount Code",
  "Scenario": "Apply valid discount code",
  "Steps": [
    "Add Item A to cart",
    "Enter 'SAVE15' in the discount input field",
    "Click 'Apply'"
  ],
  "Expected_Result": "Green success message appears and total reduces by 15%",
  "Grounded_In": ["specs.md", "checkout.html"]
}

## 📄 Example Selenium Script (Generated)

{
  from selenium import webdriver
  from selenium.webdriver.common.by import By
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC
  
  html_file_path = "file:///D:/.../checkout.html"
  
  driver = webdriver.Chrome()
  driver.get(html_file_path)
  
  wait = WebDriverWait(driver, 10)
  
  try:
      add_item1_button = wait.until(EC.element_to_be_clickable((By.ID, "add-item1")))
      add_item1_button.click()
  
      discount_input = wait.until(EC.presence_of_element_located((By.ID, "discount-code")))
      discount_input.send_keys("SAVE15")
  
      apply_button = wait.until(EC.element_to_be_clickable((By.ID, "apply-discount")))
      apply_button.click()
  
      msg = wait.until(EC.visibility_of_element_located((By.ID, "discount-msg")))
      assert msg.text == "Discount applied!"
      
      total = wait.until(EC.visibility_of_element_located((By.ID, "total")))
      assert total.text == "17.00"
  
      print("Test passed successfully!")
  
  except Exception as e:
      print("Test failed:", e)
  
  finally:
      print("Test complete. Browser will remain open...")
      input("Press ENTER to close browser...")
      driver.quit()
}


