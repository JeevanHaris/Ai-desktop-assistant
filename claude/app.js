/* ══════════════════════════════════════════════════════
   ARIA — AI Desktop Assistant · app.js
   Connects to Claude API (or Python backend proxy)
══════════════════════════════════════════════════════ */

// ─── State ───────────────────────────────────────────
const state = {
  history: [],          // {role, content}[]
  memories: [],
  msgCount: 0,
  isLoading: false,
  currentTool: null,
  settings: {
    model: 'claude-sonnet-4-20250514',
    maxTokens: 1024,
    assistantName: 'ARIA',
    systemPrompt: 'You are ARIA (Adaptive Reasoning Intelligence Assistant), a helpful, precise and thoughtful AI desktop assistant. You provide clear, well-structured responses. You are concise but thorough. You use markdown formatting when appropriate.',
    accent: '#00e5ff',
    fontSize: '15px',
  }
};

// ─── API Configuration ────────────────────────────────
// Supports two modes:
//   1. Direct Claude API (browser)  — set USE_BACKEND = false, set CLAUDE_API_KEY
//   2. Python backend proxy         — set USE_BACKEND = true, set BACKEND_URL
const USE_BACKEND = true;
const BACKEND_URL = 'http://localhost:5000/api/chat';  // Python Flask backend
const CLAUDE_API_KEY = '';                              // Direct mode API key

// ─── Init ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadSettings();
  loadMemories();
  document.getElementById('user-input').focus();
});

// ─── Tab Switching ────────────────────────────────────
function switchTab(id, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  btn.classList.add('active');
}

// ─── Chat: Send Message ───────────────────────────────
async function sendMessage() {
  const input = document.getElementById('user-input');
  const text = input.value.trim();
  if (!text || state.isLoading) return;

  // Clear welcome screen
  const welcome = document.querySelector('.chat-welcome');
  if (welcome) welcome.remove();

  // Add user message
  appendMessage('user', text);
  state.history.push({ role: 'user', content: text });
  input.value = '';
  autoResize(input);

  // Show typing indicator
  const typingId = showTyping();
  setLoading(true);

  try {
    const reply = await callClaude(state.history);
    removeTyping(typingId);
    appendMessage('assistant', reply);
    state.history.push({ role: 'assistant', content: reply });
    autoExtractMemory(text, reply);
    updateMsgCount();
  } catch (err) {
    removeTyping(typingId);
    appendMessage('assistant', `⚠ Error: ${err.message}`);
  } finally {
    setLoading(false);
  }
}

function sendQuick(text) {
  document.getElementById('user-input').value = text;
  sendMessage();
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}

// ─── Call Claude API ──────────────────────────────────
async function callClaude(messages) {
  if (USE_BACKEND) {
    return await callBackend(messages);
  } else {
    return await callDirectAPI(messages);
  }
}

async function callBackend(messages) {
  const res = await fetch(BACKEND_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages,
      model: state.settings.model,
      max_tokens: state.settings.maxTokens,
      system: buildSystemPrompt(),
    })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Backend error ${res.status}`);
  }

  const data = await res.json();
  return data.content || data.text || JSON.stringify(data);
}

async function callDirectAPI(messages) {
  if (!CLAUDE_API_KEY) throw new Error('No API key set. Use backend mode or add CLAUDE_API_KEY in app.js.');

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': CLAUDE_API_KEY,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify({
      model: state.settings.model,
      max_tokens: state.settings.maxTokens,
      system: buildSystemPrompt(),
      messages,
    })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || `API error ${res.status}`);
  }

  const data = await res.json();
  return data.content?.[0]?.text || 'No response';
}

function buildSystemPrompt() {
  let prompt = state.settings.systemPrompt;
  if (state.memories.length > 0) {
    prompt += '\n\n## Stored Memories (user context):\n';
    prompt += state.memories.map(m => `- ${m}`).join('\n');
  }
  return prompt;
}

// ─── Render Messages ──────────────────────────────────
function appendMessage(role, content) {
  const win = document.getElementById('chat-window');
  const div = document.createElement('div');
  div.className = `message ${role}`;

  const avatarLabel = role === 'user' ? 'U' : 'AI';
  const label = role === 'user' ? 'You' : state.settings.assistantName;
  const rendered = renderMarkdown(content);

  div.innerHTML = `
    <div class="msg-avatar">${avatarLabel}</div>
    <div class="msg-body">
      <div class="msg-label">${label}</div>
      <div class="msg-bubble">${rendered}</div>
    </div>
  `;

  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}

function renderMarkdown(text) {
  // Very lightweight markdown renderer
  return text
    // Code blocks
    .replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) =>
      `<pre><code class="lang-${lang}">${escHtml(code.trim())}</code></pre>`)
    // Inline code
    .replace(/`([^`]+)`/g, (_, c) => `<code>${escHtml(c)}</code>`)
    // Bold
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // Headings
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Lists
    .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    // Numbered lists
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Line breaks
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/\n/g, '<br>')
    // Wrap in paragraph
    .replace(/^(?!<[hupol])(.+)/gm, (line) =>
      line.startsWith('<') ? line : line);
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ─── Typing Indicator ─────────────────────────────────
let typingCounter = 0;
function showTyping() {
  const id = `typing-${++typingCounter}`;
  const win = document.getElementById('chat-window');
  const div = document.createElement('div');
  div.id = id;
  div.className = 'message assistant';
  div.innerHTML = `
    <div class="msg-avatar">AI</div>
    <div class="msg-body">
      <div class="msg-label">${state.settings.assistantName}</div>
      <div class="msg-bubble">
        <div class="typing-dots"><span></span><span></span><span></span></div>
      </div>
    </div>
  `;
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
  return id;
}

function removeTyping(id) {
  document.getElementById(id)?.remove();
}

// ─── Loading State ────────────────────────────────────
function setLoading(val) {
  state.isLoading = val;
  const btn = document.getElementById('send-btn');
  btn.disabled = val;
  document.getElementById('api-status').textContent = val ? 'Thinking…' : 'Ready';
  document.getElementById('api-status').style.color = val ? 'var(--accent)' : '#34d399';
}

function updateMsgCount() {
  state.msgCount++;
  document.getElementById('msg-count').textContent = state.msgCount;
}

// ─── Clear Chat ───────────────────────────────────────
function clearChat() {
  state.history = [];
  state.msgCount = 0;
  document.getElementById('msg-count').textContent = 0;

  const win = document.getElementById('chat-window');
  win.innerHTML = `
    <div class="chat-welcome">
      <div class="welcome-orb">
        <div class="orb-ring r1"></div>
        <div class="orb-ring r2"></div>
        <div class="orb-ring r3"></div>
        <div class="orb-core"></div>
      </div>
      <h2>Hello, I'm ARIA</h2>
      <p>Your Adaptive Reasoning Intelligence Assistant.<br>Ask me anything — I'm here to help.</p>
      <div class="quick-prompts">
        <button class="quick-btn" onclick="sendQuick('What can you help me with?')">What can you help me with?</button>
        <button class="quick-btn" onclick="sendQuick('Write a Python function to sort a list')">Write Python code</button>
        <button class="quick-btn" onclick="sendQuick('Explain quantum computing in simple terms')">Explain a concept</button>
        <button class="quick-btn" onclick="sendQuick('Help me brainstorm ideas for a mobile app')">Brainstorm ideas</button>
      </div>
    </div>
  `;
}

// ─── Tools Tab ────────────────────────────────────────
const TOOL_CONFIG = {
  summarize: {
    title: '📋 Summarize Text',
    placeholder: 'Paste the text you want to summarize...',
    extra: null,
    prompt: (text) => `Summarize the following text concisely:\n\n${text}`,
  },
  translate: {
    title: '🌐 Translate Text',
    placeholder: 'Paste the text you want to translate...',
    extra: 'Target language (e.g. Spanish, French, Japanese)',
    prompt: (text, lang) => `Translate the following text to ${lang || 'Spanish'}:\n\n${text}`,
  },
  codereview: {
    title: '🔍 Code Review',
    placeholder: 'Paste your code here...',
    extra: null,
    prompt: (text) => `Review this code for bugs, performance issues, and best practices. Give actionable feedback:\n\n\`\`\`\n${text}\n\`\`\``,
  },
  grammar: {
    title: '✏️ Grammar Fix',
    placeholder: 'Paste the text you want to fix...',
    extra: null,
    prompt: (text) => `Fix all grammar, spelling, and style issues in the following text. Return only the corrected version:\n\n${text}`,
  },
  explain: {
    title: '💡 Explain',
    placeholder: 'Paste a concept, term, or passage to explain...',
    extra: 'Target audience (e.g. beginner, expert, 10-year-old)',
    prompt: (text, audience) => `Explain the following to a ${audience || 'general audience'} in simple, clear terms:\n\n${text}`,
  },
  brainstorm: {
    title: '⚡ Brainstorm',
    placeholder: 'Describe what you want to brainstorm about...',
    extra: 'Number of ideas (default: 10)',
    prompt: (text, n) => `Generate ${n || 10} creative and diverse ideas for:\n\n${text}\n\nFormat as a numbered list with a brief explanation for each.`,
  },
};

function runTool(toolId) {
  state.currentTool = toolId;
  const config = TOOL_CONFIG[toolId];
  document.getElementById('tool-modal-title').textContent = config.title;
  document.getElementById('tool-input').placeholder = config.placeholder;
  document.getElementById('tool-input').value = '';

  const extraEl = document.getElementById('tool-extra');
  if (config.extra) {
    extraEl.style.display = 'block';
    extraEl.placeholder = config.extra;
    extraEl.value = '';
  } else {
    extraEl.style.display = 'none';
  }

  const outEl = document.getElementById('tool-output');
  outEl.style.display = 'none';
  outEl.textContent = '';

  document.getElementById('tool-modal').style.display = 'flex';
}

function closeToolModal() {
  document.getElementById('tool-modal').style.display = 'none';
  state.currentTool = null;
}

async function executeTool() {
  const config = TOOL_CONFIG[state.currentTool];
  const text = document.getElementById('tool-input').value.trim();
  const extra = document.getElementById('tool-extra').value.trim();

  if (!text) return;

  const btn = document.querySelector('.run-btn');
  btn.disabled = true;
  btn.textContent = 'Running…';

  const outEl = document.getElementById('tool-output');
  outEl.style.display = 'block';
  outEl.textContent = '…';

  try {
    const prompt = config.prompt(text, extra);
    const result = await callClaude([{ role: 'user', content: prompt }]);
    outEl.textContent = result;
  } catch (err) {
    outEl.textContent = `Error: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Run Tool';
  }
}

// Close modal on backdrop click
document.addEventListener('click', (e) => {
  if (e.target.id === 'tool-modal') closeToolModal();
});

// ─── Memory Tab ───────────────────────────────────────
function addMemory(text) {
  const input = document.getElementById('memory-input');
  const val = text || input.value.trim();
  if (!val) return;

  state.memories.push(val);
  if (!text) input.value = '';
  saveMemories();
  renderMemories();
}

function removeMemory(idx) {
  state.memories.splice(idx, 1);
  saveMemories();
  renderMemories();
}

function clearMemory() {
  state.memories = [];
  saveMemories();
  renderMemories();
}

function renderMemories() {
  const list = document.getElementById('memory-list');
  if (state.memories.length === 0) {
    list.innerHTML = `
      <div class="memory-empty">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
        <p>No memory entries yet.<br>Memories are created from your conversations.</p>
      </div>`;
    return;
  }
  list.innerHTML = state.memories.map((m, i) => `
    <div class="memory-entry">
      <div class="memory-entry-dot"></div>
      <div class="memory-entry-text">${escHtml(m)}</div>
      <button class="memory-entry-del" onclick="removeMemory(${i})">✕</button>
    </div>
  `).join('');
}

function autoExtractMemory(userMsg, reply) {
  // Extract simple name mentions
  const nameMatch = userMsg.match(/(?:my name is|i am|i'm|call me)\s+([A-Z][a-z]+)/i);
  if (nameMatch) {
    const mem = `User's name is ${nameMatch[1]}`;
    if (!state.memories.includes(mem)) addMemory(mem);
  }

  // Extract profession
  const jobMatch = userMsg.match(/(?:i(?:'m| am) a(?:n)?|i work as a(?:n)?)\s+([a-z ]+?)(?:\.|,|$)/i);
  if (jobMatch) {
    const mem = `User works as: ${jobMatch[1].trim()}`;
    if (!state.memories.includes(mem)) addMemory(mem);
  }
}

function saveMemories() {
  try { localStorage.setItem('aria_memories', JSON.stringify(state.memories)); } catch(e){}
}

function loadMemories() {
  try {
    const saved = localStorage.getItem('aria_memories');
    if (saved) { state.memories = JSON.parse(saved); renderMemories(); }
  } catch(e){}
}

// ─── Settings ─────────────────────────────────────────
function saveSettings() {
  state.settings.model = document.getElementById('model-select').value;
  state.settings.maxTokens = parseInt(document.getElementById('max-tokens').value) || 1024;
  state.settings.assistantName = document.getElementById('assistant-name').value || 'ARIA';
  state.settings.systemPrompt = document.getElementById('system-prompt').value;
  try { localStorage.setItem('aria_settings', JSON.stringify(state.settings)); } catch(e){}
}

function loadSettings() {
  try {
    const saved = localStorage.getItem('aria_settings');
    if (saved) {
      const s = JSON.parse(saved);
      Object.assign(state.settings, s);
    }
  } catch(e){}

  document.getElementById('model-select').value = state.settings.model;
  document.getElementById('max-tokens').value = state.settings.maxTokens;
  document.getElementById('assistant-name').value = state.settings.assistantName;
  document.getElementById('system-prompt').value = state.settings.systemPrompt;

  if (state.settings.accent) {
    document.documentElement.style.setProperty('--accent', state.settings.accent);
    // Update glow color
    const hex = state.settings.accent;
    const r = parseInt(hex.slice(1,3),16);
    const g = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);
    document.documentElement.style.setProperty('--accent-dim', `rgba(${r},${g},${b},0.12)`);
    document.documentElement.style.setProperty('--accent-glow', `rgba(${r},${g},${b},0.25)`);
    document.documentElement.style.setProperty('--border-accent', `rgba(${r},${g},${b},0.25)`);
  }

  if (state.settings.fontSize) {
    document.documentElement.style.setProperty('--font-size', state.settings.fontSize);
    document.getElementById('font-size').value = state.settings.fontSize;
  }
}

function setAccent(color, btn) {
  document.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
  btn.classList.add('active');
  state.settings.accent = color;

  document.documentElement.style.setProperty('--accent', color);
  const hex = color;
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  document.documentElement.style.setProperty('--accent-dim', `rgba(${r},${g},${b},0.12)`);
  document.documentElement.style.setProperty('--accent-glow', `rgba(${r},${g},${b},0.25)`);
  document.documentElement.style.setProperty('--border-accent', `rgba(${r},${g},${b},0.25)`);

  saveSettings();
}

function applyFontSize() {
  const size = document.getElementById('font-size').value;
  state.settings.fontSize = size;
  document.documentElement.style.setProperty('--font-size', size);
  saveSettings();
}
