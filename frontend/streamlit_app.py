import streamlit as st
import requests
import json
from pathlib import Path

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")
st.title("🤖 Autonomous QA Agent for Test Case & Script Generation")

# -------------------------
# Upload: support docs & HTML
# -------------------------
st.header("1) Upload Support Documents & HTML")

uploaded_docs = st.file_uploader("Upload support documents (md, txt, json)", accept_multiple_files=True, type=["md","txt","json"])
uploaded_html = st.file_uploader("Upload checkout.html (or any HTML file)", type=["html"])

if st.button("Build Knowledge Base"):
    if uploaded_docs:
        for f in uploaded_docs:
            files = {"file": (f.name, f.getvalue(), "text/plain")}
            try:
                r = requests.post(f"{API_URL}/ingest", files=files, timeout=60)
                st.success(f"Ingested doc: {f.name}")
            except Exception as e:
                st.error(f"Failed to ingest {f.name}: {e}")

    if uploaded_html:
        files = {"file": (uploaded_html.name, uploaded_html.getvalue(), "text/html")}
        try:
            r = requests.post(f"{API_URL}/ingest_html", files=files, timeout=60)
            jr = r.json()
            st.success(f"HTML ingested: {jr.get('html_file', uploaded_html.name)}")
            st.session_state["last_html"] = jr.get("html_file", uploaded_html.name)
        except Exception as e:
            st.error(f"Failed to ingest HTML: {e}")

# Show which HTML is currently selected (last uploaded)
last_html = st.session_state.get("last_html", None)
if last_html:
    st.info(f"Using HTML: **{last_html}** (last uploaded)")

# -------------------------
# Generate Test Cases
# -------------------------
st.header("2) Generate Test Cases")

default_prompt = "Generate positive and negative test cases for the discount code feature."
user_query = st.text_area("Agent prompt (example):", value=default_prompt, height=120)

if st.button("Generate Test Cases"):
    if not user_query.strip():
        st.warning("Enter a prompt for the agent.")
    else:
        try:
            r = requests.post(f"{API_URL}/generate_testcases", data={"query": user_query}, timeout=120)
            jr = r.json()
            if jr.get("ok"):
                st.success("Test cases generated successfully!")
                st.session_state["testcases"] = jr["testcases"]
                st.json(jr["testcases"])
            else:
                st.error("Model did not return valid JSON. See raw output below.")
                st.code(jr.get("raw", str(jr)), language="text")
        except Exception as e:
            st.error(f"Request failed: {e}")

# -------------------------
# Generate Selenium Script
# -------------------------
st.header("3) Generate Selenium Script")

if "testcases" in st.session_state:
    tcs = st.session_state["testcases"]
    # Format test case display in selectbox
    def tc_label(i):
        tc = tcs[i]
        tid = tc.get("Test_ID") or f"TC-{i}"
        feat = tc.get("Feature", "")
        scen = tc.get("Scenario", "")
        return f"{tid} — {feat}: {scen}"

    idx = st.selectbox("Choose a test case", options=list(range(len(tcs))), format_func=tc_label)

    if st.button("Generate Selenium Script for selected test case"):
        selected_tc = tcs[idx]
        try:
            payload = {"test_case": json.dumps(selected_tc)}
            r = requests.post(f"{API_URL}/generate_script", data=payload, timeout=120)
            jr = r.json()
            if jr.get("ok"):
                st.success(f"Script generated (based on {jr.get('html_used')})")
                st.code(jr["script"], language="python")
                # Optionally allow downloading the script
                script_text = jr["script"]
                script_name = f"{selected_tc.get('Test_ID','test')}.py"
                st.download_button("Download script", data=script_text, file_name=script_name, mime="text/x-python")
            else:
                st.error("Script generation failed.")
                st.text(jr.get("error", str(jr)))
        except Exception as e:
            st.error(f"Request failed: {e}")
else:
    st.info("Generate test cases first (step 2).")
