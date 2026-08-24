import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="JEI Chatbot")

# Setup templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# JEI Product Catalog
JEI_PRODUCTS_KNOWLEDGE = """
COMPANY: Janaka Engineering Industries (Pvt) Ltd (JEI) - Since 2000
LOCATION & CONTACT: Sri Lanka | Hotline: +94 77 123 4567 | Email: info@jei.lk | Web: https://www.jei.lk

PRODUCT RANGE (12 MAIN CATEGORIES):
1. Small Scale Rice Mill Machines: For small-scale farmers and mini millers. Low power, high efficiency, minimal broken rice.
2. Medium Scale Rice Mill Lines: Semi-automated lines with destoner, huller, paddy separator, and polisher.
3. Large Scale Industrial Rice Mill Lines: Fully automated high-capacity commercial plants.
4. Color Sorter & Packing Machines: Optical CCD color sorting and automated bagging/packaging.
5. Grader Machines: Classifies head rice, broken rice, and mixed grains.
6. Polisher Machines: Silky water mist and dry polishers.
7. Rice Mill Dryers: Recirculating and batch paddy dryers.
8. Steam Boiler Machines: Biomass/diesel boilers for parboiled rice processing (තැම්බූ සහල්).
9. Motors & Bearings: Heavy-duty electric motors and industrial bearings.
10. Grass Cutting Machines: Field weeders and lawn trimmers.
11. Agriculture Equipment: Advanced farm machinery and sprayers.
12. Solar PV & Inverter Systems: Rooftop solar and hybrid inverters for factories and mills.

SERVICES: Custom mill layout design, islandwide installation, genuine spare parts, and technician training.
"""

SYSTEM_PROMPT = f"""
You are the Official AI Technical Support Assistant for "Janaka Engineering Industries (Pvt) Ltd" (JEI).

RULES:
1. TRILINGUAL SUPPORT:
   - Always reply in the EXACT language used by the customer: Sinhala (සිංහල / Singlish), Tamil (தமிழ்), or English.
2. STRICT PRODUCT BOUNDARY:
   - Only answer questions related to JEI rice mill machinery, engineering equipment, and company services.
   - Data reference:
   {JEI_PRODUCTS_KNOWLEDGE}
   - If asked about anything outside (politics, general trivia, weather, homework, other brands), politely decline:
     * Sinhala: "සමාවන්න, මට පිළිතුරු දිය හැක්කේ ජනක ඉංජිනේරු සමාගමේ (JEI) නිෂ්පාදන සහ සේවාවන් පිළිබඳව පමණි."
     * Tamil: "மன்னிக்கவும், ஜனக இன்ஜினியரிங் (JEI) தயாரிப்புகள் மற்றும் சேவைகள் தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் பதிலளிக்க முடியும்."
     * English: "I can only assist with inquiries regarding Janaka Engineering Industries (JEI) products and services."
3. Keep answers polite, accurate, and professional.
"""

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not client:
        return JSONResponse(status_code=500, content={"reply": "API Key is not configured."})
    
    try:
        contents = []
        for h in req.history:
            role = "user" if h.get("role") == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=h.get("content", ""))]))
        
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=req.message)]))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2
            )
        )
        return {"reply": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"reply": f"දෝෂයක් සිදු විය: {str(e)}"})