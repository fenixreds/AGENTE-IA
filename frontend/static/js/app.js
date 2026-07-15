const chatContainer = document.getElementById('chat-container');
const messagesEl = document.getElementById('messages');
const emptyState = document.getElementById('empty-state');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const mobileNewChat = document.getElementById('mobile-new-chat');
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebar-overlay');
const historyList = document.getElementById('chat-history-list');

let isLoading = false;

(function () {
  const root = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');
  toggle.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
  });
})();

sidebarToggle?.addEventListener('click', () => {
  sidebar.classList.toggle('open');
  overlay.classList.toggle('visible');
});

overlay?.addEventListener('click', () => {
  sidebar.classList.remove('open');
  overlay.classList.remove('visible');
});

function startNewChat() {
  messagesEl.innerHTML = '';
  emptyState.style.display = '';
  chatInput.value = '';
  autoResize();
  sendBtn.disabled = true;
}

newChatBtn?.addEventListener('click', startNewChat);
mobileNewChat?.addEventListener('click', startNewChat);

document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    chatInput.value = chip.dataset.prompt;
    autoResize();
    sendBtn.disabled = false;
    chatInput.focus();
  });
});

chatInput.addEventListener('input', () => {
  autoResize();
  sendBtn.disabled = chatInput.value.trim().length === 0;
});

function autoResize() {
  chatInput.style.height = 'auto';
  chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + 'px';
}

chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled && !isLoading) sendMessage();
  }
});

sendBtn.addEventListener('click', () => {
  if (!isLoading) sendMessage();
});

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text || isLoading) return;

  emptyState.style.display = 'none';
  appendMessage('user', escapeHtml(text));
  chatInput.value = '';
  autoResize();
  sendBtn.disabled = true;
  isLoading = true;

  const typingId = appendTyping();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    removeTyping(typingId);
    appendMessage('ai', formatAnswer(data.answer), data.sources || []);
  } catch (err) {
    removeTyping(typingId);
    appendMessage('ai', `<p>Error al conectar con el agente: ${escapeHtml(err.message)}</p>`, []);
  }

  isLoading = false;
  chatInput.focus();
}

function appendMessage(role, html, sources = []) {
  const isUser = role === 'user';
  const div = document.createElement('div');
  div.className = `message ${role}`;

  const avatarHtml = isUser
    ? `<div class="avatar user-avatar">Tú</div>`
    : `<div class="avatar ai-avatar">IA</div>`;

  const sourcesHtml = sources.length ? buildSourcesHtml(sources) : '';

  div.innerHTML = `
    <div class="message-inner">
      ${avatarHtml}
      <div class="message-content">
        ${isUser ? `<p>${html}</p>` : html}
        ${sourcesHtml}
      </div>
    </div>
  `;

  const toggle = div.querySelector('.sources-toggle');
  const list = div.querySelector('.sources-list');

  if (toggle && list) {
    toggle.addEventListener('click', () => {
      list.classList.toggle('visible');
    });
  }

  messagesEl.appendChild(div);
  scrollToBottom();
}

function buildSourcesHtml(sources) {
  const items = sources.map(s => `
    <div class="source-item">
      <p><strong>Página:</strong> ${s.page}</p>
      <p><strong>Fuente:</strong> ${escapeHtml(s.source)}</p>
      <p>${escapeHtml(s.content)}...</p>
    </div>
  `).join('');

  return `
    <div class="sources">
      <button class="sources-toggle">${sources.length} fuente(s) consultada(s)</button>
      <div class="sources-list">${items}</div>
    </div>
  `;
}

function appendTyping() {
  const id = 'typing-' + Date.now();
  const div = document.createElement('div');
  div.className = 'message ai';
  div.id = id;
  div.innerHTML = `
    <div class="message-inner">
      <div class="avatar ai-avatar">IA</div>
      <div class="message-content">
        <p>Escribiendo...</p>
      </div>
    </div>
  `;
  messagesEl.appendChild(div);
  scrollToBottom();
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function formatAnswer(text) {
  const safe = escapeHtml(text);
  return safe
    .split(/\n\n+/)
    .map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`)
    .join('');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function scrollToBottom() {
  chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
}