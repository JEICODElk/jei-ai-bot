import os
import json
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="JEI AI Customer & Product Management Suite")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "jei@2026")

DB_FILE = "products_db.json"
LEADS_DB = []

# Default Starter Products if DB doesn't exist
DEFAULT_PRODUCTS = [
    {
        "id": "1",
        "name": "Small Scale Rice Mill Machine (කුඩා පරිමාණ වී මෝල)",
        "category": "Rice Mill Machines",
        "price": "Rs. 450,000 සිට ඉහළට (ධාරිතාව අනුව)",
        "image": "https://images.unsplash.com/photo-1586771107445-d3ca888129ff?w=600&q=80",
        "specs": "ධාරිතාව: 500kg - 1000kg/hr | විදුලිය: Single/Three Phase | කැඩීම අවමයි (<5%)",
        "description": "කුඩා පරිමාණ ව්‍යාපාර සහ ගොවිපල සඳහා ඉතා සුදුසුයි. අඩු විදුලි පරිභෝජනයකින් ඉහළ අස්වැන්නක් ලබා දේ."
    },
    {
        "id": "2",
        "name": "Medium & Large Industrial Rice Mill Lines (කාර්මික වී මෝල් පද්ධති)",
        "category": "Commercial Plants",
        "price": "මිල ගණන් සඳහා අමතන්න (Quotation)",
        "image": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=600&q=80",
        "specs": "ධාරිතාව: ටොන් 2 සිට 20/hr | Destoner, Huller, Separator, Polisher, Grader සහිතයි",
        "description": "සම්පූර්ණ ස්වයංක්‍රීය උසස් තත්ත්වයේ වාණිජ සහල් සැකසුම් පද්ධති."
    },
    {
        "id": "3",
        "name": "Optical CCD Color Sorter & Auto Packing (වර්ණ තේරීමේ යන්ත්‍ර)",
        "category": "Color Sorter",
        "price": "විමසීම් අනුව (Contact Sales)",
        "image": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600&q=80",
        "specs": "64 - 384 Channels | 99.9% නිරවද්‍යතාව | Auto weighing & vacuum bagging",
        "description": "කළු, කහ, සුදු සහල් සහ ගල් කැට වෙන්කර උසස්ම තත්ත්වයේ ඇසුරුම් සකස් කරයි."
    }
]

def load_products():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_PRODUCTS
    return DEFAULT_PRODUCTS

def save_products(prods):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(prods, f, ensure_ascii=False, indent=2)

def build_dynamic_system_prompt():
    products = load_products()
    catalog_text = ""
    for idx, p in enumerate(products, 1):
        catalog_text += f"""
{idx}. PRODUCT: {p.get('name')}
   - Category: {p.get('category')}
   - Price / Estimate: {p.get('price')}
   - Specifications: {p.get('specs')}
   - Details: {p.get('description')}
   - Image Link: {p.get('image', '')}
"""

    prompt = f"""
You are the Chief Technical Sales AI Assistant for "Janaka Engineering Industries (Pvt) Ltd" (JEI) - Sri Lanka.
HOTLINE: +94 77 123 4567 | EMAIL: info@jei.lk | WEB: https://www.jei.lk

CURRENT OFFICIAL PRODUCTS IN STOCK & SERVICES:
{catalog_text}

SERVICES: Custom mill layout design, islandwide delivery & installation, genuine spare parts, operator training.

CRITICAL INSTRUCTIONS:
1. TRILINGUAL SUPPORT:
   - If user asks in Sinhala or Singlish -> Reply ONLY in proper SINHALA SCRIPT (පිරිසිදු සිංහලෙන්).
   - If user asks in Tamil -> Reply ONLY in TAMIL SCRIPT (தமிழ்).
   - If user asks in English -> Reply ONLY in professional ENGLISH.
2. DOMAIN BOUNDARY:
   - Only answer questions related to JEI products and engineering machinery listed above.
   - If asked about outside topics (politics, general knowledge, movies, homework), politely decline.
3. PRODUCT RECOMMENDATION & IMAGES:
   - When describing a specific product, if an Image Link is available, you can mention it or it will be formatted cleanly.
   - Use bold titles, clean bullet points (•), and clear price/capacity details.
"""
    return prompt

def send_telegram_alert(text: str):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=5)
        except Exception:
            pass

# ==========================================
# 🎨 FRONTEND CHAT UI (WITH RICH PHOTO CARDS)
# ==========================================
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
      max-width: 480px;
      height: 90vh;
      max-height: 760px;
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
    }
    .header-text h1 { font-size: 16px; font-weight: 700; }
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
    }
    .form-group input:focus { border-color: var(--primary); }
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
    }

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
      gap: 14px;
    }
    .msg { display: flex; flex-direction: column; max-width: 88%; }
    .user { align-self: flex-end; }
    .bot { align-self: flex-start; }
    .bubble {
      padding: 12px 16px;
      font-size: 13.5px;
      line-height: 1.6;
      border-radius: 18px;
    }
    .user .bubble { background: linear-gradient(135deg, #0284c7, #0369a1); color: white; border-bottom-right-radius: 4px; }
    .bot .bubble { background: white; color: #1e293b; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; }
    
    .product-card-preview {
      margin-top: 10px;
      background: #f1f5f9;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid #e2e8f0;
    }
    .product-card-preview img {
      width: 100%;
      height: 160px;
      object-fit: cover;
      display: block;
    }
    .product-card-preview .p-info {
      padding: 10px 12px;
    }
    .product-card-preview h4 { font-size: 13px; color: #0f172a; margin-bottom: 2px; }
    .product-card-preview p { font-size: 11.5px; color: #0284c7; font-weight: 600; }

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
    }
    .chip:hover { background: #0284c7; color: white; }
    
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
    }
  </style>
</head>
<body>

  <div class="app-card">
    <div class="header">
      <div class="brand-icon">J</div>
      <div class="header-text">
        <h1>Janaka Engineering (JEI)</h1>
        <p><span class="pulse-dot"></span> Live AI | සිංහල · English · தமிழ்</p>
      </div>
    </div>

    <!-- Registration Gate -->
    <div class="view-gate" id="gateView">
      <h2>Welcome to JEI Support</h2>
      <p>අපගේ ඉංජිනේරු නිෂ්පාදන, ඡායාරූප සහ මිල ගණන් විමසීමට පෙර කරුණාකර ඔබගේ විස්තර ඇතුළත් කරන්න.</p>
      
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
          <input type="text" id="custLocation" placeholder="උදා: පොළොන්නරුව / කුරුණෑගල" required>
        </div>
        <button type="submit" class="btn-submit">Start Consultation →</button>
      </form>
    </div>

    <!-- Chat View -->
    <div class="view-chat" id="chatView">
      <div class="chat-messages" id="chatBox">
        <div class="msg bot">
          <div class="bubble" id="welcomeMsg">
            <strong>ආයුබෝවන්! / வணக்கம்! / Welcome!</strong><br><br>
            ජනක ඉංජිනේරු සමාගමේ (JEI) වී මෝල් යන්ත්‍ර සූත්‍ර, ඡායාරූප, සහ මිල ගණන් පිළිබඳව ඕනෑම විස්තරයක් විමසන්න.
          </div>
        </div>
      </div>
      
      <div class="quick-chips" id="quickChips">
        <button class="chip" onclick="quickSend('කුඩා පරිමාණ වී මෝල් වල විස්තර සහ මිල කියන්න')">🌾 කුඩා වී මෝල්</button>
        <button class="chip" onclick="quickSend('Color Sorter යන්ත්‍ර වල විස්තර සහ photos මොනවාද?')">📦 Color Sorter</button>
        <button class="chip" onclick="quickSend('ඔබ සතුව ඇති සියලුම නිෂ්පාදන මොනවාද?')">📋 All Products</button>
      </div>

      <form class="chat-input-bar" onsubmit="handleSend(event)">
        <input type="text" id="userInput" placeholder="ඔබට දැනගැනීමට අවශ්‍ය දේ ලියන්න..." autocomplete="off" required>
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
      document.getElementById('welcomeMsg').innerHTML = `<strong>ආයුබෝවන් ${name} මහත්මයා/මිය!</strong><br><br>ජනක ඉංජිනේරු සමාගමට (JEI) ඔබව සාදරයෙන් පිළිගනිමු. අපගේ යන්ත්‍ර සූත්‍ර, මිල ගණන් සහ තාක්ෂණික තොරතුරු පිළිබඳව ඔබට අවශ්‍ය ඕනෑම විස්තරයක් විමසන්න.`;
    }

    function formatText(text) {
      // Find URLs matching image patterns
      let formatted = text
        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\n/g, '<br>');
      return formatted;
    }

    function appendMsg(role, text, matchedProducts = []) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `msg ${role}`;
      
      let cardHtml = '';
      if (matchedProducts && matchedProducts.length > 0) {
        matchedProducts.forEach(p => {
          if (p.image) {
            cardHtml += `
              <div class="product-card-preview">
                <img src="${p.image}" alt="${p.name}" onerror="this.style.display='none'">
                <div class="p-info">
                  <h4>${p.name}</h4>
                  <p>${p.price || ''}</p>
                </div>
              </div>
            `;
          }
        });
      }

      msgDiv.innerHTML = `<div class="bubble">${formatText(text)}${cardHtml}</div>`;
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
        appendMsg('bot', botReply, data.matched_products || []);
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

# ==========================================
# 🛠️ ADMIN DASHBOARD HTML (PRODUCTS & LEADS)
# ==========================================
ADMIN_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>JEI Master Admin Panel</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
    body { background: #f1f5f9; padding: 30px 20px; color: #1e293b; }
    .container { max-width: 1050px; margin: auto; }
    .header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .header-bar h1 { font-size: 22px; color: #0f172a; font-weight: 700; }
    .card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); margin-bottom: 24px; }
    h2 { font-size: 16px; color: #0284c7; margin-bottom: 16px; font-weight: 600; }
    
    /* Product Form */
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
    .form-full { grid-column: span 2; }
    label { display: block; font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 4px; }
    input, textarea, select { width: 100%; padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 10px; font-size: 13.5px; outline: none; }
    input:focus, textarea:focus { border-color: #0284c7; }
    .btn-add { background: #0284c7; color: white; border: none; padding: 12px 24px; border-radius: 10px; font-weight: 600; cursor: pointer; }
    .btn-add:hover { background: #0369a1; }
    
    /* Product List Grid */
    .prod-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-top: 14px; }
    .prod-card { border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: #fafafa; display: flex; flex-direction: column; }
    .prod-card img { width: 100%; height: 140px; object-fit: cover; background: #e2e8f0; }
    .prod-details { padding: 12px; flex: 1; display: flex; flex-direction: column; }
    .prod-details h3 { font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
    .prod-details .cat { font-size: 11px; background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 12px; display: inline-block; margin-bottom: 6px; }
    .prod-details .price { font-size: 12px; font-weight: 600; color: #16a34a; margin-bottom: 6px; }
    .prod-details p { font-size: 11.5px; color: #64748b; line-height: 1.4; flex: 1; }
    .btn-del { background: #fee2e2; color: #ef4444; border: none; padding: 6px 12px; border-radius: 8px; font-size: 11px; font-weight: 600; cursor: pointer; margin-top: 10px; align-self: flex-start; }
    .btn-del:hover { background: #fecaca; }

    /* Leads Table */
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 13.5px; }
    th { background: #f8fafc; color: #475569; }
    .badge { background: #dcfce7; color: #15803d; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header-bar">
      <h1>⚙️ JEI Control Panel (Products & Customer Leads)</h1>
      <span style="font-size: 12px; color: #64748b;">Logged in as Admin</span>
    </div>

    <!-- Product Creation Form -->
    <div class="card">
      <h2>➕ Add New Product / Machine with Photos</h2>
      <form onsubmit="addProduct(event)">
        <div class="form-grid">
          <div>
            <label>Product Name (යන්ත්‍රයේ නම) *</label>
            <input type="text" id="pName" placeholder="උදා: Silky Water Mist Polisher" required>
          </div>
          <div>
            <label>Category (කාණ්ඩය) *</label>
            <input type="text" id="pCategory" placeholder="උදා: Polishers / Rice Mill" required>
          </div>
          <div>
            <label>Price / Estimated Cost (මිල) *</label>
            <input type="text" id="pPrice" placeholder="උදා: Rs. 650,000 / Contact Sales" required>
          </div>
          <div>
            <label>Photo Image URL (ඡායාරූප Link එක) *</label>
            <input type="url" id="pImage" placeholder="https://example.com/image.jpg" required>
          </div>
          <div class="form-full">
            <label>Specifications / Features (තාක්ෂණික විස්තර) *</label>
            <input type="text" id="pSpecs" placeholder="උදා: ධාරිතාව: 2 Ton/hr | 15HP Motor | High Gloss Polish" required>
          </div>
          <div class="form-full">
            <label>Description & Customer Pitch (සම්පූර්ණ විස්තරය) *</label>
            <textarea id="pDesc" rows="2" placeholder="යන්ත්‍රයේ භාවිතය සහ වාසි විස්තර කරන්න..." required></textarea>
          </div>
        </div>
        <button type="submit" class="btn-add">Save & Train AI Assistant →</button>
      </form>
    </div>

    <!-- Current Products Grid -->
    <div class="card">
      <h2>📦 Active Products Catalog in AI Knowledge Base ({PROD_COUNT})</h2>
      <div class="prod-grid">
        {PRODUCT_CARDS}
      </div>
    </div>

    <!-- Customer Leads Table -->
    <div class="card">
      <h2>🎯 Customer Leads & Inquiries Recorded</h2>
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
          {LEAD_ROWS}
        </tbody>
      </table>
    </div>
  </div>

  <script>
    const urlParams = new URLSearchParams(window.location.search);
    const key = urlParams.get('key') || '';

    async function addProduct(e) {
      e.preventDefault();
      const payload = {
        name: document.getElementById('pName').value.trim(),
        category: document.getElementById('pCategory').value.trim(),
        price: document.getElementById('pPrice').value.trim(),
        image: document.getElementById('pImage').value.trim(),
        specs: document.getElementById('pSpecs').value.trim(),
        description: document.getElementById('pDesc').value.trim()
      };

      const res = await fetch(`/api/admin/products?key=${key}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        alert('✅ Product added successfully and AI is retrained!');
        window.location.reload();
      } else {
        alert('❌ Error adding product.');
      }
    }

    async function deleteProduct(id) {
      if (!confirm('මෙම නිෂ්පාදනය ඉවත් කිරීමට අවශ්‍ය බව තහවුරු කරන්නද?')) return;
      const res = await fetch(`/api/admin/products/${id}?key=${key}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        window.location.reload();
      } else {
        alert('❌ Error deleting product.');
      }
    }
  </script>
</body>
</html>
"""

# ==========================================
# 🚀 API ENDPOINTS & LOGIC
# ==========================================
class RegisterPayload(BaseModel):
    name: str
    phone: str
    location: str

class ChatPayload(BaseModel):
    customer: dict
    message: str
    history: list[dict] = []

class ProductCreatePayload(BaseModel):
    name: str
    category: str
    price: str
    image: str
    specs: str
    description: str

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

    alert_msg = f"🔥 <b>New Customer Lead!</b>\n👤 <b>Name:</b> {payload.name}\n📞 <b>Phone:</b> <code>{payload.phone}</code>\n📍 <b>Location:</b> {payload.location}"
    send_telegram_alert(alert_msg)

    return {"status": "success"}

@app.post("/api/chat")
async def chat(payload: ChatPayload):
    if not GEMINI_API_KEY:
        return JSONResponse(status_code=500, content={"reply": "GEMINI_API_KEY Render එකේ සකසා නැත."})

    current_prompt = build_dynamic_system_prompt()
    products = load_products()

    # Match user query keywords to product names for rich photo attachment
    matched_products = []
    user_q_lower = payload.message.lower()
    for p in products:
        p_name_words = p["name"].lower().split()
        if any(w in user_q_lower for w in p_name_words if len(w) > 3) or p["category"].lower() in user_q_lower:
            matched_products.append(p)

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

    endpoints_to_try = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    ]

    body = {
        "system_instruction": {
            "parts": [{"text": current_prompt}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2
        }
    }

    for url in endpoints_to_try:
        try:
            res = requests.post(url, json=body, timeout=25)
            if res.status_code == 200:
                data = res.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                
                cust_name = payload.customer.get('name', 'User')
                cust_phone = payload.customer.get('phone', 'N/A')
                send_telegram_alert(f"💬 <b>Chat:</b> {cust_name} ({cust_phone})\n<b>Q:</b> {payload.message}")
                
                return {
                    "reply": reply,
                    "matched_products": matched_products[:2] # Top matching photos
                }
        except Exception:
            continue

    return JSONResponse(status_code=500, content={"reply": "තාක්ෂණික දෝෂයක්. කරුණාකර මොහොතකින් නැවත විමසන්න."})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(key: str = ""):
    if key != ADMIN_PASSWORD:
        return HTMLResponse(content="<h2>🔒 Unauthorized Access. Please visit with ?key=YOUR_PASSWORD</h2>", status_code=403)
    
    products = load_products()
    
    # Render product cards
    prod_cards_html = ""
    for p in products:
        prod_cards_html += f"""
        <div class="prod-card">
          <img src="{p.get('image', '')}" alt="{p.get('name')}" onerror="this.src='https://placehold.co/400x200?text=No+Photo'">
          <div class="prod-details">
            <span class="cat">{p.get('category')}</span>
            <h3>{p.get('name')}</h3>
            <div class="price">{p.get('price')}</div>
            <p>{p.get('specs')}</p>
            <button class="btn-del" onclick="deleteProduct('{p.get('id')}')">🗑️ Delete Product</button>
          </div>
        </div>
        """
    if not prod_cards_html:
        prod_cards_html = "<p style='color:#94a3b8; font-size:13px;'>No products added yet.</p>"

    # Render lead rows
    lead_rows = ""
    for lead in reversed(LEADS_DB):
        lead_rows += f"<tr><td>{lead['time']}</td><td><b>{lead['name']}</b></td><td><span class='badge'>{lead['phone']}</span></td><td>{lead['location']}</td></tr>"
    
    if not lead_rows:
        lead_rows = "<tr><td colspan='4' style='text-align:center; color:#94a3b8;'>No customer leads recorded yet.</td></tr>"

    html = ADMIN_HTML.replace("{PRODUCT_CARDS}", prod_cards_html)
    html = html.replace("{LEAD_ROWS}", lead_rows)
    html = html.replace("{PROD_COUNT}", str(len(products)))

    return HTMLResponse(content=html)

@app.post("/api/admin/products")
async def add_product(payload: ProductCreatePayload, key: str = ""):
    if key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    products = load_products()
    new_item = {
        "id": str(int(datetime.now().timestamp())),
        "name": payload.name,
        "category": payload.category,
        "price": payload.price,
        "image": payload.image,
        "specs": payload.specs,
        "description": payload.description
    }
    products.append(new_item)
    save_products(products)
    return {"status": "success"}

@app.delete("/api/admin/products/{prod_id}")
async def delete_product(prod_id: str, key: str = ""):
    if key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    products = load_products()
    products = [p for p in products if p.get("id") != prod_id]
    save_products(products)
    return {"status": "success"}
