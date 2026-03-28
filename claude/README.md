# ARIA — AI Desktop Assistant

A sleek, dark-themed AI assistant powered by **Claude** via a Python Flask backend.

## 📁 Files

```
ai-assistant/
├── index.html     ← Main UI (open in browser)
├── style.css      ← Styling
├── app.js         ← Frontend logic (API calls, chat, tools, memory, settings)
├── server.py      ← Python Flask backend (proxies Claude API)
├── .env           ← Your API key (create this from .env.example)
└── README.md      ← This file
```

---

## 🚀 Quick Start

### 1. Install Python dependencies

```bash
pip install flask flask-cors anthropic python-dotenv
```

### 2. Set your API key

Create a `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your key at: https://console.anthropic.com

### 3. Start the backend

```bash
python server.py
```

You should see:
```
ARIA Backend — Python Flask Server
URL: http://localhost:5000
API Key: ✅ Set
```

### 4. Open the frontend

Open `index.html` in your browser (double-click it, or use a simple server):

```bash
# Option A: just open the file
open index.html   # macOS
start index.html  # Windows

# Option B: serve locally to avoid CORS on some browsers
python -m http.server 8080
# then visit http://localhost:8080
```

---

## ✨ Features

| Feature | Description |
|---|---|
| **Chat** | Full conversation with Claude, with markdown rendering |
| **Quick Tools** | Summarize, Translate, Code Review, Grammar Fix, Explain, Brainstorm |
| **Memory** | Auto-extracts and stores context from conversations |
| **Settings** | Switch Claude models, customize system prompt, accent colors, font size |
| **Responsive** | Adapts to smaller screen widths |

---

## ⚙️ Configuration

Edit the top of `app.js` to switch between backend modes:

```js
// Mode 1: Python backend (default, recommended)
const USE_BACKEND = true;
const BACKEND_URL = 'http://localhost:5000/api/chat';

// Mode 2: Direct Claude API (no backend needed)
const USE_BACKEND = false;
const CLAUDE_API_KEY = 'sk-ant-...';
```

---

## 🔌 API Endpoints (server.py)

| Method | Path | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/api/health` | Health check JSON |
| POST | `/api/chat` | Chat with Claude (full history) |
| POST | `/api/tool` | One-shot tool prompt |

### POST /api/chat body:
```json
{
  "messages": [{"role": "user", "content": "Hello!"}],
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "system": "You are ARIA..."
}
```

---

## 🎨 Customization

- **Accent color** — click color swatches in Settings tab
- **Model** — choose between Sonnet, Opus, Haiku
- **System prompt** — fully customizable in Settings
- **Assistant name** — change from ARIA to anything

---

Built with HTML, CSS, JavaScript + Python (Flask) · Powered by Anthropic Claude
