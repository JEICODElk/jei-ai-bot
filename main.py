import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="JEI AI Chatbot")

# Configure Gemini API Key
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# JEI Official Products Catalog
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
   - Reference Data:
   {JEI_PRODUCTS_KNOWLEDGE}
   - If asked about anything outside (politics, general trivia, weather, homework, other brands), politely decline:
     * Sinhala: "සමාවන්න, මට පිළිතුරු දිය හැක්කේ ජනක ඉංජිනේරු සමාගමේ (JEI) නිෂ්පාදන සහ සේවාවන් පිළිබඳව පමණි."
     * Tamil: "மன்னிக்கவும், ஜனக இன்ஜினியரிங் (JEI) தயாரிப்புகள் மற்றும் சேவைகள் தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் பதிலளிக்க முடியும்."
     * English: "I can only assist with inquiries regarding Janaka Engineering Industries (JEI) products and services."
3. Keep answers polite, accurate, concise, and professional.
"""

# All-in-One HTML Page
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JEI AI Customer Assistant</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f1f5f9;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 12px;
    }
    .chat-wrapper {
      width: 100%;
      max-width: 480px;
      height: 90vh;
      max-height: 700px;
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.1);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .header {
      background: #0f172a;
      color: #ffffff;
      padding: 16px;
      text-align: center;
    }
    .header h2 { font-size: 17px; }
    .header p { font-size: 12px; color: #94a3b8; margin-top: 3px; }
    .chat-box {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: #f8fafc;
    }
    .msg { display: flex; flex-direction: column; max-width: 82%; }
    .user { align-self: flex-end; }
    .bot { align-self: flex-start; }
    .bubble {
      padding: 10px 14px;
      border-radius: 14px;
      font-size: 14px;
      line-height: 1.5;
      word-break: break-word;
    }
    .user .bubble { background: #2563eb; color: #ffffff; border-bottom-right-radius: 2px; }
    .bot .bubble { background: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; border-bottom-left-radius: 2px; }
    .quick-chips {
      display: flex;
      gap: 6px;
      padding: 8px 12px;
      background: #f8fafc;
      border-top: 1px solid #f1f5f9;
      overflow-x: auto;
    }
    .chip {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      font-size: 12px;
      padding: 6px 12px;
      border-radius: 16px;
      cursor: pointer;
      white-space: nowrap;
      color: #334155;
    }
    .chip:hover { background: #2563eb; color: #fff; border-color: #2563eb; }
    form {
      display: flex;
      padding: 12px;
      background: #ffffff;
      border-top: 1px solid #e2e8f0;
      gap: 8px;
    }
    input {
      flex: 1;
      padding: 10px 16px;
      border: 1px solid #cbd5e1;
      border-radius: 24px;
      font-size: 14px;
      outline: none;
    }
    button {
      background: #2563eb;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 24px;
      cursor: pointer;
      font-weight: 600;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="chat-wrapper">
    <header class="header">
      <h2>Janaka Engineering (JEI) AI Assistant</h2>
      <p>Online | සිංහල · English · தமிழ்</p>
    </header>
    <div class="chat-box" id="chatBox">
      <div class="msg bot">
        <div class="bubble">
          <strong>ආයුබෝවන්! / வணக்கம்! / Welcome!</strong><br>
          ජනක ඉංජිනේරු සමාගමේ (JEI) වී මෝල් යන්ත්‍ර සූත්‍ර සහ සේවාවන් පිළිබඳව ඕනෑම විස්තරයක් විමසන්න.
        </div>
      </div>
    </div>
    <div class="quick-chips">
      <button class="chip" onclick="quickAsk('ඔබේ වී මෝල් මැෂින් මොනවාද?')">🌾 වී මෝල් මැෂින්</button>
      <button class="chip" onclick="quickAsk('Color Sorter & Packing Machine details')">📦 Color Sorter</button>
      <button class="chip" onclick="quickAsk('යන්ත්‍ර සවි කිරීම් සහ සේවා')">🛠️ Services</button>
    </div>
    <form id="chatForm" onsubmit="handleSend(event)">
      <input type="text" id="userInput" placeholder="ඔබේ ප්‍රශ්නය සිංහලෙන් හෝ English වලින් අසන්න..." autocomplete="off" required>
      <button type="submit" id="sendBtn">Send</button>
    </form>
  </div>

  <script>
    let chatHistory = [];
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');

    function appendMessage(role, text) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `msg ${role}`;
      msgDiv.innerHTML = `<div class="bubble">${text.replace(/\\n/g, '<br>')}</div>`;
      chatBox.appendChild(msgDiv);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function handleSend(e) {
      if (e) e.preventDefault();
      const text = userInput.value.trim();
      if (!text) return;

      appendMessage('user', text);
      userInput.value = '';
      userInput.disabled = true;
      sendBtn.disabled = true;

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history: chatHistory })
        });
        const data = await res.json();
        const reply = data.reply || "ප්‍රතිචාරයක් නොලැබුණි.";
        appendMessage('bot', reply);
        chatHistory.push({ role: 'user', content: text });
        chatHistory.push({ role: 'model', content: reply });
      } catch (err) {
        appendMessage('bot', 'සමාවන්න, සබඳතාවේ දෝෂයක් සිදු විය.');
      } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
      }
    }

    function quickAsk(q) {
      userInput.value = q;
      handleSend(null);
    }
  </script>
</body>
</html>
"""

class ChatPayload(BaseModel):
    message: str
    history: list[dict] = []

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    return HTMLResponse(content=HTML_PAGE)

@app.post("/api/chat")
async def chat_endpoint(payload: ChatPayload):
    if not API_KEY:
        return JSONResponse(status_code=500, content={"reply": "GEMINI_API_KEY is not set in Render."})
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        chat_session = model.start_chat(history=[
            {"role": "user" if h.get("role") == "user" else "model", "parts": [h.get("content", "")]}
            for h in payload.history
        ])
        
        response = chat_session.send_message(payload.message)
        return {"reply": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"reply": f"තාක්ෂණික දෝෂයක්: {str(e)}"})
