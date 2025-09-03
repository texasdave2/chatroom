import os
import google.generativeai as genai

# Configure the LLM for this agent
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_mood_from_llm(text: str) -> str:
    """Sends text to an LLM for mood analysis."""
    prompt = f"Analyze the following chat message and classify its mood as either 'happy', 'sad', or 'neutral'. Respond with only the label. Message: '{text}'"
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.0})
        return response.text.strip().lower()
    except Exception as e:
        print(f"LLM analysis failed: {e}")
        return "neutral"

