from fastapi import HTTPException
from pydantic import BaseModel
import json
import google.generativeai as genai
from app.core.config import GOOGLE_API_KEY

# Configure the SDK
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')



def analyze_ticket(title,
                   description):
    prompt = f"""
    Analyze the following customer support ticket and categorize it.
    
    Ticket Title: {title}
    Ticket Description: {description}
    
    Return strictly a JSON object with these keys:
    - "category": (choose from: technical_bug, billing, feature_request, other)
    - "priority": (choose from: Low, Medium, High)
    
    JSON Output:
    """

    try:
        # Generate content with JSON constraint and a reasonable timeout
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
            request_options={"timeout": 20}  # Set a 20-second timeout
        )

        # Parse the string response into a Python dictionary
        result = json.loads(response.text)
        return result

    except Exception as e:
        print(f"Gemini API Error: {e}. Falling back to default categorization.")
        # Instead of raising an HTTPException that stops the process,
        # return a default object so ticket creation can continue.
        return {
            "category": "other",
            "priority": "low"
        }
    