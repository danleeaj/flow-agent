from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

# import dotenv
# dotenv.load_dotenv()

from agent.agent import process_city_weather

app = FastAPI()

# Pydantic model for the request body
class WeatherRequest(BaseModel):
    city: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/weather")
def get_weather_report(request: WeatherRequest):
    """Trigger a weather report for the specified city."""
    try:
        if not request.city or not request.city.strip():
            raise HTTPException(status_code=400, detail="City name cannot be empty")
        
        # Capture the output from the agent
        import io
        from contextlib import redirect_stdout
        
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            process_city_weather(request.city.strip())
        
        output = captured_output.getvalue()
        
        return {
            "success": True,
            "city": request.city,
            "message": "Weather report generated successfully",
            "output": output
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weather report: {str(e)}")

@app.get("/weather/{city}")
def get_weather_report_get(city: str):
    """Alternative GET endpoint to trigger a weather report."""
    try:
        if not city or not city.strip():
            raise HTTPException(status_code=400, detail="City name cannot be empty")
        
        # Capture the output from the agent
        import io
        from contextlib import redirect_stdout
        
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            process_city_weather(city.strip())
        
        output = captured_output.getvalue()
        
        return {
            "success": True,
            "city": city,
            "message": "Weather report generated successfully",
            "output": output
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weather report: {str(e)}")