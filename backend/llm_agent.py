import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class LLMAgent:
    def __init__(self, model="gemini-2.5-flash-lite"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Add it to .env file.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt, max_length=4096):
        response = self.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_length,
                "temperature": 0,   # deterministic JSON output
            }
        )
        return response.text
