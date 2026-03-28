"""
ARIA — AI Desktop Assistant · Python Backend
Flask proxy server for Claude API
────────────────────────────────────────────
Setup:
    pip install flask flask-cors anthropic python-dotenv

Run:
    python server.py

Then open index.html in your browser (or serve it via a local server).
The frontend connects to http://localhost:5000/api/chat by default.

Environment:
    Set ANTHROPIC_API_KEY in a .env file or as an environment variable.
    Example .env:
        ANTHROPIC_API_KEY=sk-ant-...
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

try:
    import anthropic
except ImportError:
    print("❌  anthropic not installed. Run: pip install anthropic")
    exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional

# ─── App Setup ────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow all origins for local development

# Prefer env var, fall back to hardcoded key for quick testing
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

if not API_KEY:
    print("⚠️  Warning: ANTHROPIC_API_KEY not set. Set it in .env or as an environment variable.")


# ─── Health Check ─────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ok",
        "service": "ARIA Backend",
        "api_key_set": bool(API_KEY),
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "api_key_set": bool(API_KEY)})


# ─── Main Chat Endpoint ───────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    if not API_KEY:
        return jsonify({"error": "ANTHROPIC_API_KEY is not set on the server."}), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body."}), 400

    messages = data.get("messages", [])
    model = data.get("model", "claude-sonnet-4-20250514")
    max_tokens = int(data.get("max_tokens", 1024))
    system_prompt = data.get("system", "You are ARIA, a helpful AI assistant.")

    if not messages:
        return jsonify({"error": "No messages provided."}), 400

    # Validate messages format
    for msg in messages:
        if "role" not in msg or "content" not in msg:
            return jsonify({"error": "Each message must have 'role' and 'content'."}), 400
        if msg["role"] not in ("user", "assistant"):
            return jsonify({"error": f"Invalid role: {msg['role']}"}), 400

    try:
        client = anthropic.Anthropic(api_key=API_KEY)

        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )

        reply_text = response.content[0].text if response.content else ""

        return jsonify({
            "content": reply_text,
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "stop_reason": response.stop_reason,
        })

    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid API key. Check your ANTHROPIC_API_KEY."}), 401
    except anthropic.RateLimitError:
        return jsonify({"error": "Rate limit reached. Please wait and try again."}), 429
    except anthropic.APIError as e:
        return jsonify({"error": f"Anthropic API error: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# ─── Tool Endpoint (optional direct tool runner) ──────
@app.route("/api/tool", methods=["POST"])
def tool():
    """Run a one-shot tool prompt without history."""
    if not API_KEY:
        return jsonify({"error": "ANTHROPIC_API_KEY is not set on the server."}), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body."}), 400

    prompt = data.get("prompt", "")
    model = data.get("model", "claude-sonnet-4-20250514")
    max_tokens = int(data.get("max_tokens", 1024))

    if not prompt:
        return jsonify({"error": "No prompt provided."}), 400

    try:
        client = anthropic.Anthropic(api_key=API_KEY)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return jsonify({"content": response.content[0].text if response.content else ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Run ──────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"""
╔══════════════════════════════════════════╗
║   ARIA Backend — Python Flask Server     ║
╠══════════════════════════════════════════╣
║  URL:     http://localhost:{port}           ║
║  API Key: {'✅ Set' if API_KEY else '❌ Not set (add to .env)'}               ║
╚══════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=port, debug=True)
