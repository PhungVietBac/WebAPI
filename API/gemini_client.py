from google import genai
from schemas.result import TripPlan
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("api_key")

client = genai.Client(api_key=api_key)

def get_trip_plan(prompt: str) -> TripPlan:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": TripPlan
        }
    )
    
    return response.parsed