import os
import google.generativeai as genai

# Configure the LLM for this agent
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_safety_label_from_llm(text: str) -> str:
    """Sends text to an LLM for safety analysis."""
    # New prompt for safety analysis.
    prompt = f"Analyze the following chat message for safety. Classify its content as 'safe' or 'unsafe'. Respond with only the label. Message: '{text}'"
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.0})
        return response.text.strip().lower()
    except Exception as e:
        print(f"LLM safety analysis failed: {e}")
        return "safe"
