import os
import requests
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="JEI AI Customer Suite")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "jei@2026")

LEADS_DB = []

JEI_KNOWLEDGE = """
COMPANY: Janaka Engineering Industries (Pvt) Ltd (JEI) - Since 2000
HOTLINE: +94 77 123 4567 | EMAIL: info@jei.lk | WEB: https://www.jei.lk
PRODUCTS (12 CATEGORIES):
1. Small Scale Rice Mill: For mini millers. Low power, high efficiency, minimal broken rice.
2. Medium Scale Rice Mill: Semi-auto line (destoner, huller, separator, polisher).
3. Large Scale Industrial Mill: Fully automated commercial milling plants.
4. Color Sorter & Packing Machine: Optical CCD color sorter & auto packaging.
5. Graders: Classifies head rice, broken grains, and impurities.
6. Polishers: Silky water mist and dry polishers.
7. Dryers: Recirculating & batch paddy dryers.
8. Steam Boilers: Biomass/diesel boilers for parboiled rice.
9. Motors & Bearings: Heavy duty motors & industrial bearings.
10. Grass Cutters: Agricultural weeders and trimmers.
11. Farm Equipment: Advanced agriculture machines and tools.
12. Solar PV: Commercial rooftop solar & inverters for factories.

SERVICES: Custom mill layout design, islandwide installation, genuine spare parts, and technician training.
"""

SYSTEM_PROMPT = f"""
You are the Official AI Technical Support Specialist at Janaka Engineering Industries (JEI).
RULES:
1. TRILINGUAL: Reply in the EXACT language of the user (Sinhala, Singlish, Tamil, or English).
2. DOMAIN BOUNDARY: Strictly answer ONLY questions regarding JEI machinery, engineering, and services.
   Reference Data:
   {JEI_KNOWLEDGE}
   If asked about unrelated topics (politics, general trivia, homework, other brands), politely decline:
   - Sinhala: "සමාවන්න, මට පිළිතුරු දිය හැක්කේ ජනක ඉංජිනේරු සමාගමේ (JEI) නිෂ්පාදන සහ සේවාවන් පිළිබඳව පමණි."
   - Tamil: "மன்னிக்கவும், ஜனக இன்ஜினியரிங் (JEI) தயாரிப்புகள் மற்றும் சேவைகள் தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் பதிலளிக்க முடியும்."
   - English: "I can only assist with inquiries regarding Janaka Engineering Industries (JEI) products and services."
3. Keep answers concise, highly professional, polite, and persuasive.
"""

def send_telegram_alert(text: str):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=5)
        except Exception:
            pass

FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Janaka Engineering (JEI) AI Assistant</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #0284c7;
      --primary-dark: #0369a1;
      --bg: #0f172a;
      --surface: #1e293b;
      --card: #ffffff;
      --text-main: #0f172a;
      --text-muted: #64748b;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
    body {
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 16px;
    }
    .app-card {
      width: 100%;
      max-width: 440px;
      height: 90vh;
      max-height: 720px;
      background: rgba(255, 255, 255, 0.98);
      backdrop-filter: blur(12px);
      border-radius: 24px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .header {
      background: linear-gradient(135deg, #0f172a, #1e293b);
      color: white;
      padding: 18px 20px;
      display: flex;
      align-items: center;
      gap: 14px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .brand-icon {
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, #0284c7, #38bdf8);
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 20px;
      color: white;
      box-shadow: 0 4px 10px rgba(2, 132, 199, 0.4);
    }
    .header-text h1 { font-size: 16px; font-weight: 700; letter-spacing: -0.3px; }
    .header-text p { font-size: 11px; color: #38bdf8; display: flex; align-items: center; gap: 6px; }
    .pulse-dot { width: 8px; height: 8px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 8px #22c55e; }
    
    .view-gate {
      flex: 1;
      padding: 28px 24px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    .view-gate h2 { font-size: 20px; color: #0f172a; margin-bottom: 6px; font-weight: 700; }
    .view-gate p { font-size: 13px; color: var(--text-muted); margin-bottom: 22px; line-height: 1.5; }
    .form-group { margin-bottom: 14px; }
    .form-group label { display: block; font-size: 12px; font-weight: 600; color: #334155; margin-bottom: 6px; }
    .form-group input {
      width: 100%;
      padding: 12px 14px;
      border: 1.5px solid #e2e8f0;
      border-radius: 12px;
      font-size: 14px;
      outline: none;
      transition: all 0.2s;
    }
    .form-group input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15); }
    .btn-submit {
      margin-top: 10px;
      width: 100%;
      padding: 14px;
      background: linear-gradient(135deg, #0284c7, #0369a1);
      color: white;
      border: none;
      border-radius: 12px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
      transition: transform 0.1s;
    }
    .btn-submit:active { transform: scale(0.98); }

    .view-chat {
      flex: 1;
      display: none;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
      background: #f8fafc;
    }
    .chat-messages {
      flex: 1;
      padding: 18px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .msg { display: flex; flex-direction: column; max-width: 82%; }
    .user { align-self: flex-end; }
    .bot { align-self: flex-start; }
    .bubble {
      padding: 12px 16px;
      font-size: 13.5px;
      line-height: 1.5;
      border-radius: 18px;
    }
    .user .bubble { background: linear-gradient(135deg, #0284c7, #0369a1); color: white; border-bottom-right-radius: 4px; box-shadow: 0 4px 10px rgba(2, 132, 199, 0.2); }
    .bot .bubble { background: white; color: #1e293b; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
    
    .quick-chips {
      display: flex;
      gap: 6px;
      padding: 8px 14px;
      background: #ffffff;
      border-top: 1px solid #f1f5f9;
      overflow-x: auto;
    }
    .chip {
      background: #f1f5f9;
      border: 1px solid #e2e8f0;
      color: #334155;
      padding: 6px 12px;
      font-size: 11.5px;
      border-radius: 20px;
      white-space: nowrap;
      cursor: pointer;
      font-weight: 500;
    }
    .chip:hover { background: #0284c7; color: white; border-color: #0284c7; }
    
    .chat-input-bar {
      padding: 12px 16px;
      background: white;
      border-top: 1px solid #e2e8f0;
      display: flex;
      gap: 8px;
    }
    .chat-input-bar input {
      flex: 1;
      padding: 12px 18px;
      border: 1px solid #cbd5e1;
      border-radius: 24px;
      outline: none;
      font-size: 13.5px;
    }
    .chat-input-bar input:focus { border-color: #0284c7; }
    .chat-input-bar button {
      background: #0284c7;
      color: white;
      border: none;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
    }
  </style>
</head>
<body>

  <div class="app-card">
    <div class="header">
      <div class="brand-icon">J</div>
      <div class="header-text">
        <h1>Janaka Engineering (JEI)</h1>
        <p><span class="pulse-dot"></span> AI Active | සිංහල · English · தமிழ்</p>
      </div>
    </div>

    <!-- Registration Gate -->
    <div class="view-gate" id="gateView">
      <h2>Welcome to JEI Support</h2>
      <p>අපගේ ඉංජිනේරු නිෂ්පාදන සහ මිල ගණන් විමසීමට පෙර කරුණාකර ඔබගේ විස්තර ඇතුළත් කරන්න.</p>
      
      <form onsubmit="handleRegister(event)">
        <div class="form-group">
          <label>ඔබගේ නම (Full Name) *</label>
          <input type="text" id="custName" placeholder="උදා: කසුන් පෙරේරා" required>
        </div>
        <div class="form-group">
          <label>දුරකථන අංකය (WhatsApp Number) *</label>
          <input type="tel" id="custPhone" placeholder="0771234567" required>
        </div>
        <div class="form-group">
          <label>ප්‍රදේශය / දිස්ත්‍රික්කය (Location) *</label>
          <input type="text" id="custLocation" placeholder="උදා: පොළොන්නරුව / අනුරාධපුර" required>
        </div>
        <button type="submit" class="btn-submit">Start Consultation →</button>
      </form>
    </div>

    <!-- Chat View -->
    <div class="view-chat" id="chatView">
      <div class="chat-messages" id="chatBox">
        <div class="msg bot">
          <div class="bubble" id="welcomeMsg">
            <strong>ආයුබෝවන්! / வணக்கம்!</strong><br>
            ජනක ඉංජිනේරු සමාගමේ (JEI) වී මෝල් යන්ත්‍ර සූත්‍ර, උපකරණ සහ සේවාවන් පිළිබඳව ඕනෑම විස්තරයක් විමසන්න.
          </div>
        </div>
      </div>
      
      <div class="quick-chips">
        <button class="chip" onclick="quickSend('කුඩා හා මධ්‍යම පරිමාණ වී මෝල් ගැන විස්තර ඕන')">🌾 වී මෝල් පද්ධති</button>
        <button class="chip" onclick="quickSend('Color Sorter & Packing Machine details')">📦 Color Sorter</button>
        <button class="chip" onclick="quickSend('Dryers සහ Steam Boilers ගැන කියන්න')">🔥 Dryers & Boilers</button>
      </div>

      <form class="chat-input-bar" onsubmit="handleSend(event)">
        <input type="text" id="userInput" placeholder="ඔබට දැනගැනීමට අවශ්‍ය දේ මෙහි ලියන්න..." autocomplete="off" required>
        <button type="submit">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
      </form>
    </div>
  </div>

  <script>
    let customerData = {};
    let chatHistory = [];
    const gateView = document.getElementById('gateView');
    const chatView = document.getElementById('chatView');
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');

    async function handleRegister(e) {
      e.preventDefault();
      const name = document.getElementById('custName').value.trim();
      const phone = document.getElementById('custPhone').value.trim();
      const location = document.getElementById('custLocation').value.trim();

      if (!name || !phone || !location) return;
      customerData = { name, phone, location };

      fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customerData)
      });

      gateView.style.display = 'none';
      chatView.style.display = 'flex';
      document.getElementById('welcomeMsg').innerHTML = `<strong>ආයුබෝවන් ${name} මහත්මයා/මිය!</strong><br>ජනක ඉංජිනේරු සමාගමට ඔබව සාදරයෙන් පිළිගනිමු. අපගේ වී මෝල් සහ ඉංජිනේරු නිෂ්පාදන පිළිබඳව ඔබට අවශ්‍ය ඕනෑම විස්තරයක් විමසන්න.`;
    }

    function appendMsg(role, text) {
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

      appendMsg('user', text);
      userInput.value = '';

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            customer: customerData,
            message: text,
            history: chatHistory
          })
        });
        const data = await res.json();
        const botReply = data.reply || "ප්‍රතිචාරයක් නොලැබුණි.";
        appendMsg('bot', botReply);
        chatHistory.push({ role: 'user', content: text });
        chatHistory.push({ role: 'model', content: botReply });
      } catch (err) {
        appendMsg('bot', 'සමාවන්න, සම්බන්ධතාවයේ දෝෂයක් සිදු විය.');
      }
    }

    function quickSend(q) {
      userInput.value = q;
      handleSend(null);
    }
  </script>
</body>
</html>
"""

ADMIN_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>JEI Lead Manager</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background: #f8fafc; padding: 30px; }
    .card { background: white; max-width: 900px; margin: auto; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    h1 { font-size: 20px; color: #0f172a; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
    th { background: #f1f5f9; color: #475569; }
    .badge { background: #e0f2fe; color: #0369a1; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🎯 JEI Customer Leads & Inquiries (Admin Panel)</h1>
    <table>
      <thead>
        <tr>
          <th>Time</th>
          <th>Customer Name</th>
          <th>Phone Number</th>
          <th>Location</th>
        </tr>
      </thead>
      <tbody>
        {ROWS}
      </tbody>
    </table>
  </div>
</body>
</html>
"""

class RegisterPayload(BaseModel):
    name: str
    phone: str
    location: str

class ChatPayload(BaseModel):
    customer: dict
    message: str
    history: list[dict] = []

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=FRONTEND_HTML)

@app.post("/api/register")
async def register_lead(payload: RegisterPayload):
    lead = {
        "time": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
        "name": payload.name,
        "phone": payload.phone,
        "location": payload.location
    }
    LEADS_DB.append(lead)

    alert_msg = f"🔥 <b>New Customer Registered!</b>\n👤 <b>Name:</b> {payload.name}\n📞 <b>Phone:</b> <code>{payload.phone}</code>\n📍 <b>Location:</b> {payload.location}"
    send_telegram_alert(alert_msg)

    return {"status": "success"}

@app.post("/api/chat")
async def chat(payload: ChatPayload):
    if not GEMINI_API_KEY:
        return JSONResponse(status_code=500, content={"reply": "GEMINI_API_KEY not configured in Render."})

    contents = []
    for h in payload.history:
        role = "user" if h.get("role") == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": h.get("content", "")}]
        })
    
    contents.append({
        "role": "user",
        "parts": [{"text": payload.message}]
    })

    body = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2
        }
    }

    # Dynamic models priority queue (gemini-3.6-flash, gemini-2.5-flash, gemini-2.0-flash)
    candidate_models = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    
    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            res = requests.post(url, json=body, timeout=25)
            data = res.json()
            if res.status_code == 200:
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                cust_name = payload.customer.get('name', 'User')
                cust_phone = payload.customer.get('phone', 'N/A')
                send_telegram_alert(f"💬 <b>Chat Activity:</b>\n👤 {cust_name} ({cust_phone})\n<b>Q:</b> {payload.message}")
                return {"reply": reply}
        except Exception:
            continue

    return JSONResponse(status_code=500, content={"reply": "AI Engine සම්බන්ධ කරගැනීමේ දෝෂයක්. කරුණාකර නැවත උත්සාහ කරන්න."})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(key: str = ""):
    if key != ADMIN_PASSWORD:
        return HTMLResponse(content="<h2>🔒 Unauthorized Access. Provide valid ?key=YOUR_PASSWORD</h2>", status_code=403)
    
    rows = ""
    for lead in reversed(LEADS_DB):
        rows += f"<tr><td>{lead['time']}</td><td><b>{lead['name']}</b></td><td><span class='badge'>{lead['phone']}</span></td><td>{lead['location']}</td></tr>"
    
    if not rows:
        rows = "<tr><td colspan='4' style='text-align:center; color:#94a3b8;'>No customer leads recorded yet.</td></tr>"

    return HTMLResponse(content=ADMIN_HTML.replace("{ROWS}", rows))
