let history = [];
const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');

function appendMsg(role, text) {
  const div = document.createElement('div');
  div.className = role === 'user' ? 'user-msg' : 'bot-msg';
  div.innerHTML = `<div class="bubble">${text.replace(/\n/g, '<br>')}</div>`;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(e) {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;

  appendMsg('user', text);
  userInput.value = '';

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history: history })
    });
    const data = await res.json();
    appendMsg('bot', data.reply);
    history.push({ role: 'user', content: text });
    history.push({ role: 'model', content: data.reply });
  } catch (err) {
    appendMsg('bot', 'සමාවන්න, සම්බන්ධතාවයේ දෝෂයක් සිදු විය.');
  }
}