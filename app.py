import os
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>A.T.H.E.N.A. OS - IA Multimodal Prime</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Helvetica, Arial, sans-serif; }
        body { background-color: #0c1317; color: #e9edef; height: 100vh; display: flex; justify-content: center; align-items: center; }
        .whatsapp-container { width: 100%; max-width: 1250px; height: 96vh; background: #111b21; display: flex; box-shadow: 0 6px 18px rgba(0,0,0,0.6); border-radius: 10px; overflow: hidden; position: relative; }
        .sidebar { width: 30%; background: #111b21; border-right: 1px solid #222d34; display: flex; flex-direction: column; }
        .sidebar-header { padding: 15px; background: #202c33; display: flex; align-items: center; justify-content: space-between; font-weight: 600; font-size: 15px; color: #00a884; }
        .sidebar-actions { padding: 10px; background: #182229; display: flex; gap: 8px; border-bottom: 1px solid #222d34; }
        .btn-new-chat { flex: 1; background: #8b5cf6; color: white; border: none; padding: 8px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center; gap: 6px; font-size: 13px; }
        .btn-new-chat:hover { background: #7c3aed; }
        .expiry-selector { background: #2a3942; color: #e9edef; border: none; padding: 6px; border-radius: 6px; font-size: 11px; outline: none; cursor: pointer; }
        .sidebar-config { padding: 8px 10px; background: #111b21; border-bottom: 1px solid #222d34; }
        .sidebar-config input { width: 100%; padding: 6px 8px; background: #2a3942; border: none; color: white; border-radius: 4px; font-size: 11px; }
        .chat-list { flex: 1; overflow-y: auto; }
        .chat-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 15px; background: #111b21; cursor: pointer; border-bottom: 1px solid #222d34; transition: 0.2s; position: relative; }
        .chat-item:hover { background: #202c33; }
        .chat-item.active { background: #2a3942; border-left: 4px solid #8b5cf6; }
        .chat-item.pinned { background: #1a232a; }
        .chat-info { flex: 1; overflow: hidden; }
        .chat-info h4 { font-size: 14px; color: #e9edef; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px; }
        .chat-info p { font-size: 11px; color: #8696a0; margin-top: 3px; }
        .chat-menu-btn { background: none; border: none; color: #8696a0; cursor: pointer; font-size: 16px; padding: 4px 8px; border-radius: 4px; }
        .chat-menu-btn:hover { background: #374248; color: white; }
        .context-menu { display: none; position: absolute; background: #233138; border: 1px solid #374045; border-radius: 8px; padding: 6px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.6); z-index: 100; width: 180px; }
        .context-item { padding: 8px 15px; font-size: 13px; color: #e9edef; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.2s; }
        .context-item:hover { background: #111b21; color: #8b5cf6; }
        .chat-main { flex: 7; display: flex; flex-direction: column; background: #0b141a; position: relative; }
        .chat-header { padding: 10px 16px; background: #202c33; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #222d34; }
        .chat-header-user { display: flex; align-items: center; }
        .chat-header-user .avatar { width: 40px; height: 40px; margin-right: 12px; background: #8b5cf6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; }
        .chat-header-info h3 { font-size: 16px; color: #e9edef; }
        .chat-header-info span { font-size: 12px; color: #00ff88; }
        .header-actions { display: flex; gap: 8px; align-items: center; }
        .model-selector, .speed-selector { background: #2a3942; color: #e9edef; border: 1px solid #475569; padding: 6px 10px; border-radius: 15px; font-size: 12px; outline: none; cursor: pointer; font-weight: bold; }
        .live-toggle-btn { background: #334155; color: white; border: 1px solid #475569; padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 6px; }
        .live-toggle-btn.active { background: #059669; }
        .stop-audio-btn { background: #ef4444; color: white; border: none; padding: 8px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer; display: none; }
        .live-video-box { display: none; position: absolute; top: 70px; right: 20px; width: 170px; height: 125px; background: black; border: 2px solid #8b5cf6; border-radius: 10px; overflow: hidden; z-index: 10; }
        .live-video-box video { width: 100%; height: 100%; object-fit: cover; }
        .live-status-tag { position: absolute; bottom: 5px; left: 5px; background: rgba(0,0,0,0.7); color: #00ff88; font-size: 10px; padding: 2px 6px; border-radius: 4px; }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
        .message { max-width: 75%; padding: 12px 16px; border-radius: 8px; font-size: 14px; line-height: 22px; position: relative; word-wrap: break-word; }
        .message.user { background: #005c4b; color: #e9edef; align-self: flex-end; }
        .message.athena { background: #202c33; color: #e9edef; align-self: flex-start; border-left: 3px solid #8b5cf6; }
        .timestamp { font-size: 10px; color: rgba(255,255,255,0.6); float: right; margin-left: 10px; margin-top: 5px; }
        .typing-indicator { font-style: italic; color: #a78bfa; background: #1a2228 !important; }
        .preview-box { padding: 8px 16px; background: #182229; font-size: 13px; color: #8b5cf6; display: none; border-top: 1px solid #222d34; align-items: center; justify-content: space-between; }
        .preview-box button { background: #ef4444; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px; }
        .attach-menu { display: none; position: absolute; bottom: 65px; left: 15px; background: #233138; border-radius: 10px; padding: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); z-index: 20; flex-direction: column; gap: 10px; }
        .attach-item { display: flex; align-items: center; gap: 10px; color: white; cursor: pointer; font-size: 14px; padding: 6px 10px; border-radius: 6px; }
        .attach-item:hover { background: #111b21; }
        .chat-input-area { padding: 10px 16px; background: #202c33; display: flex; align-items: center; gap: 10px; position: relative; }
        .chat-input-area input[type="text"] { flex: 1; padding: 12px 14px; background: #2a3942; border: none; border-radius: 8px; color: white; font-size: 15px; outline: none; }
        .icon-btn { background: none; border: none; color: #8696a0; font-size: 22px; cursor: pointer; padding: 5px; }
        .send-btn { background: #8b5cf6; border: none; color: white; padding: 10px; width: 42px; height: 42px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        input[type="file"] { display: none; }
    </style>
</head>
<body>
    <div class="whatsapp-container">
        <div class="sidebar">
            <div class="sidebar-header">
                <span>⚡ A.T.H.E.N.A. OS</span>
                <span style="font-size: 11px; background: #8b5cf6; color: white; padding: 3px 8px; border-radius: 10px;">v5.0 Prime</span>
            </div>
            <div class="sidebar-actions">
                <button class="btn-new-chat" onclick="criarNovoChat()">+ Nova Conversa</button>
                <select class="expiry-selector" id="globalExpiry" onchange="salvarConfiguracaoExclusao()">
                    <option value="15">⏳ 15 dias</option>
                    <option value="30" selected>⏳ 1 mês</option>
                    <option value="60">⏳ 2 meses</option>
                    <option value="180">⏳ 6 meses</option>
                </select>
            </div>
            <div class="sidebar-config">
                <input type="password" id="apiKeyInput" placeholder="Chave OpenRouter (sk-or-v1...)">
            </div>
            <div class="chat-list" id="chatList"></div>
        </div>

        <div class="context-menu" id="contextMenu">
            <div class="context-item" onclick="acaoMenu('fixar')"><span id="txtFixar">📌 Fixar Conversa</span></div>
            <div class="context-item" onclick="acaoMenu('renomear')">✏️ Renomear</div>
            <div class="context-item" onclick="acaoMenu('exportar')">📤 Exportar Nota (MD)</div>
            <div class="context-item" onclick="acaoMenu('excluir')" style="color:#ef4444;">🗑️ Excluir</div>
        </div>

        <div class="chat-main">
            <div class="chat-header">
                <div class="chat-header-user">
                    <div class="avatar">AT</div>
                    <div class="chat-header-info">
                        <h3 id="currentChatTitle">Athena Principal</h3>
                        <span id="statusSubtext">Voz Feminina Ativa • 24/7</span>
                    </div>
                </div>
                <div class="header-actions">
                    <select class="model-selector" id="modelSelector">
                        <option value="openrouter/auto">⚡ Automática</option>
                        <option value="google/gemini-2.0-flash-001">🚀 Gemini 2.0 Flash</option>
                        <option value="meta-llama/llama-3.3-70b-instruct:free">🧠 Llama 3.3 70B</option>
                    </select>
                    <select class="speed-selector" id="speechSpeed" onchange="alterarVelocidadeTempoReal()">
                        <option value="0.75">0.75x</option>
                        <option value="1.0" selected>1.0x</option>
                        <option value="1.25">1.25x</option>
                        <option value="1.5">1.5x</option>
                        <option value="2.0">2.0x (Turbo)</option>
                    </select>
                    <button class="stop-audio-btn" id="btnStopAudio" onclick="interromperVoz()">🔇 Parar</button>
                    <button class="live-toggle-btn" id="btnLiveToggle" onclick="alternarModoLive()">🟢 Modo Live</button>
                </div>
            </div>

            <div class="live-video-box" id="liveVideoBox">
                <video id="webcamVideo" autoplay playsinline muted></video>
                <div class="live-status-tag" id="liveTag">Pronta</div>
            </div>

            <div class="chat-messages" id="chatMessages"></div>

            <div class="preview-box" id="previewBox">
                <span id="previewText">✔ Anexo carregado</span>
                <button onclick="removerAnexo()">X</button>
            </div>

            <div class="attach-menu" id="attachMenu">
                <div class="attach-item" onclick="abrirSeletor('image/*')">🖼️ Imagem</div>
                <div class="attach-item" onclick="abrirSeletor('video/*')">🎥 Vídeo</div>
                <div class="attach-item" onclick="abrirSeletor('audio/*')">🎵 Áudio</div>
                <div class="attach-item" onclick="abrirSeletor('.pdf,.txt')">📄 Documento</div>
            </div>

            <input type="file" id="fileInputGlobal">

            <div class="chat-input-area">
                <button class="icon-btn" onclick="toggleAttachMenu()">📎</button>
                <input type="text" id="chatInput" placeholder="Digite sua mensagem..." autofocus>
                <button class="send-btn" onclick="enviarMensagem()">➤</button>
            </div>
        </div>
    </div>

    <script>
        let chats = JSON.parse(localStorage.getItem('athena_chats')) || [];
        let currentChatId = null; let menuChatId = null;
        const apiKeyInput = document.getElementById('apiKeyInput');
        if (localStorage.getItem('openrouter_key')) apiKeyInput.value = localStorage.getItem('openrouter_key');
        apiKeyInput.addEventListener('input', () => localStorage.setItem('openrouter_key', apiKeyInput.value));

        // Seleção de Voz Feminina (pt-BR)
        let vozAthena = null;
        function carregarVozesFemininas() {
            const vozes = window.speechSynthesis.getVoices();
            vozAthena = vozes.find(v => v.lang.includes('pt') && (v.name.toLowerCase().includes('google') || v.name.toLowerCase().includes('luciana') || v.name.toLowerCase().includes('maria') || v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('helena')))
                     || vozes.find(v => v.lang.startsWith('pt'))
                     || vozes[0];
        }
        if ('speechSynthesis' in window) {
            window.speechSynthesis.onvoiceschanged = carregarVozesFemininas;
            carregarVozesFemininas();
        }

        function salvarConfiguracaoExclusao() {
            localStorage.setItem('athena_expiry', document.getElementById('globalExpiry').value);
            limparChatsExpirados();
        }

        function limparChatsExpirados() {
            const diasRetencao = parseInt(document.getElementById('globalExpiry').value) || 30;
            const agora = new Date().getTime();
            const limiteMS = diasRetencao * 24 * 60 * 60 * 1000;
            chats = chats.filter(c => c.pinned || (agora - (c.timestamp || agora)) < limiteMS);
            salvarChatsStorage();
        }

        function salvarChatsStorage() {
            localStorage.setItem('athena_chats', JSON.stringify(chats));
            renderizarListaChats();
        }

        function criarNovoChat() {
            const novoId = 'chat_' + Date.now();
            chats.unshift({
                id: novoId, title: 'Nova Conversa...', pinned: false, timestamp: Date.now(),
                messages: [{ remetente: 'athena', texto: 'Olá! Sou a **Athena**. Como posso ajudar?', hora: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }]
            });
            salvarChatsStorage(); selecionarChat(novoId);
        }

        function selecionarChat(id) {
            currentChatId = id;
            const chat = chats.find(c => c.id === id);
            if (!chat) return;
            document.getElementById('currentChatTitle').innerText = chat.pinned ? '📌 ' + chat.title : chat.title;
            const box = document.getElementById('chatMessages');
            box.innerHTML = '';
            chat.messages.forEach(m => renderizarMensagemDOM(m.texto, m.remetente, m.anexo, m.hora));
            renderizarListaChats();
        }

        function renderizarListaChats() {
            const list = document.getElementById('chatList');
            list.innerHTML = '';
            chats.sort((a, b) => (a.pinned !== b.pinned ? (b.pinned ? 1 : -1) : b.timestamp - a.timestamp));
            chats.forEach(c => {
                const div = document.createElement('div');
                div.className = `chat-item ${c.id === currentChatId ? 'active' : ''} ${c.pinned ? 'pinned' : ''}`;
                div.onclick = () => selecionarChat(c.id);
                div.innerHTML = `<div class="chat-info"><h4>${c.pinned ? '📌 ' : ''}${c.title}</h4><p>${c.messages[c.messages.length - 1]?.texto.substring(0, 30) || ''}...</p></div><button class="chat-menu-btn" onclick="abrirMenuContexto(event, '${c.id}')">⋮</button>`;
                list.appendChild(div);
            });
        }

        function abrirMenuContexto(e, id) {
            e.stopPropagation(); menuChatId = id;
            const chat = chats.find(c => c.id === id);
            document.getElementById('txtFixar').innerText = chat.pinned ? 'Desfixar' : '📌 Fixar';
            const menu = document.getElementById('contextMenu');
            menu.style.display = 'block'; menu.style.left = (e.clientX - 140) + 'px'; menu.style.top = e.clientY + 'px';
        }
        window.onclick = () => { document.getElementById('contextMenu').style.display = 'none'; };

        function acaoMenu(tipo) {
            const chat = chats.find(c => c.id === menuChatId);
            if (!chat) return;
            if (tipo === 'fixar') chat.pinned = !chat.pinned;
            else if (tipo === 'renomear') {
                const n = prompt("Novo nome:", chat.title);
                if (n) chat.title = n.trim();
            } else if (tipo === 'excluir') {
                if (confirm("Excluir conversa?")) {
                    chats = chats.filter(c => c.id !== menuChatId);
                    if (chats.length > 0) selecionarChat(chats[0].id); else criarNovoChat();
                }
            } else if (tipo === 'exportar') {
                let md = `# ${chat.title}\\n\\n`;
                chat.messages.forEach(m => md += `### ${m.remetente}\\n${m.texto}\\n\\n`);
                const a = document.createElement('a');
                a.href = URL.createObjectURL(new Blob([md], {type: 'text/markdown'}));
                a.download = `${chat.title}.md`; a.click();
            }
            salvarChatsStorage();
            if (currentChatId === menuChatId) selecionarChat(menuChatId);
        }

        limparChatsExpirados();
        if (chats.length === 0) criarNovoChat(); else selecionarChat(chats[0].id);

        let anexoBase64 = null, tipoAnexo = null;
        const fileInput = document.getElementById('fileInputGlobal');
        fileInput.addEventListener('change', e => {
            if (e.target.files[0]) {
                const r = new FileReader();
                r.onload = evt => { anexoBase64 = evt.target.result; tipoAnexo = e.target.files[0].type; document.getElementById('previewBox').style.display = 'flex'; };
                r.readAsDataURL(e.target.files[0]);
            }
        });
        function removerAnexo() { anexoBase64 = null; tipoAnexo = null; fileInput.value = ""; document.getElementById('previewBox').style.display = 'none'; }

        let filaFrases = [], indiceFrase = 0, falando = false;
        function falarTexto(texto) {
            if (!modoLive) return;
            window.speechSynthesis.cancel();
            filaFrases = texto.replace(/[*#_`~]/g, '').match(/[^.!?]+[.!?]+/g) || [texto];
            indiceFrase = 0; falando = true; tocarProxima();
        }
        function tocarProxima() {
            if (!falando || indiceFrase >= filaFrases.length || !modoLive) {
                falando = false; document.getElementById('btnStopAudio').style.display = 'none'; estadoLive = 'parado';
                if (modoLive) { document.getElementById('liveTag').innerText = "🎤 Pode falar..."; iniciarVoz(); }
                return;
            }
            estadoLive = 'falando'; document.getElementById('liveTag').innerText = "🔊 Falando...";
            document.getElementById('btnStopAudio').style.display = 'inline-block';
            const u = new SpeechSynthesisUtterance(filaFrases[indiceFrase]);
            u.lang = 'pt-BR';
            if (vozAthena) u.voice = vozAthena;
            u.rate = parseFloat(document.getElementById('speechSpeed').value) || 1.0;
            u.onend = () => { indiceFrase++; tocarProxima(); };
            window.speechSynthesis.speak(u);
        }
        function alterarVelocidadeTempoReal() {
            if (falando && window.speechSynthesis.speaking) { window.speechSynthesis.cancel(); setTimeout(tocarProxima, 100); }
        }
        function interromperVoz() {
            falando = false; window.speechSynthesis.cancel();
            document.getElementById('btnStopAudio').style.display = 'none';
            if (modoLive) { estadoLive = 'parado'; iniciarVoz(); }
        }

        let modoLive = false, streamLive = null, recognition = null, estadoLive = 'parado', tSilencio = null;
        async function alternarModoLive() {
            const btn = document.getElementById('btnLiveToggle'), box = document.getElementById('liveVideoBox'), video = document.getElementById('webcamVideo');
            if (!modoLive) {
                try {
                    streamLive = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
                    video.srcObject = streamLive; box.style.display = 'block';
                    modoLive = true; btn.className = "live-toggle-btn active"; btn.innerHTML = "🔴 Desligar Live";
                    iniciarVoz();
                } catch(e) { alert("Permissão de câmera/microfone negada."); }
            } else {
                modoLive = false; estadoLive = 'parado'; clearTimeout(tSilencio); interromperVoz();
                if (streamLive) streamLive.getTracks().forEach(t => t.stop());
                if (recognition) try { recognition.abort(); } catch(e){}
                video.srcObject = null; box.style.display = 'none'; btn.className = "live-toggle-btn"; btn.innerHTML = "🟢 Modo Live";
            }
        }
        function iniciarVoz() {
            if (!modoLive || estadoLive !== 'parado') return;
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SR) return;
            recognition = new SR(); recognition.lang = 'pt-BR'; recognition.continuous = true; recognition.interimResults = true;
            recognition.onstart = () => { estadoLive = 'ouvindo'; document.getElementById('liveTag').innerText = "🎤 Ouvindo..."; };
            recognition.onresult = e => {
                clearTimeout(tSilencio); let txt = "";
                for (let i = 0; i < e.results.length; ++i) txt += e.results[i][0].transcript;
                if (txt.trim()) {
                    document.getElementById('liveTag').innerText = "👂 Processando...";
                    tSilencio = setTimeout(async () => {
                        if (estadoLive === 'ouvindo' && txt.trim().length > 1) {
                            estadoLive = 'proc'; try { recognition.stop(); } catch(e){}
                            const video = document.getElementById('webcamVideo'), canvas = document.createElement('canvas');
                            canvas.width = video.videoWidth || 640; canvas.height = video.videoHeight || 480;
                            canvas.getContext('2d').drawImage(video, 0, 0);
                            adicionarMsg(`🎙️ ${txt}`, "user");
                            const resp = await enviarBackend(txt, canvas.toDataURL('image/jpeg'));
                            if (resp) falarTexto(resp);
                        }
                    }, 2200);
                }
            };
            recognition.onerror = () => { estadoLive = 'parado'; if (modoLive) setTimeout(iniciarVoz, 1000); };
            recognition.onend = () => { if (estadoLive === 'ouvindo') estadoLive = 'parado'; if (modoLive && estadoLive === 'parado') setTimeout(iniciarVoz, 300); };
            try { recognition.start(); } catch(e){}
        }

        function renderizarMensagemDOM(t, r, anexo = null, h = null) {
            const div = document.createElement('div'); div.className = `message ${r}`;
            let html = r === 'athena' ? marked.parse(t) : t;
            if (anexo) html += `<img src="${anexo}" style="max-width:100%; margin-top:5px; border-radius:5px;">`;
            html += `<span class="timestamp">${h || new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>`;
            div.innerHTML = html; document.getElementById('chatMessages').appendChild(div);
            document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
        }
        function adicionarMsg(t, r, anexo = null) {
            const h = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
            renderizarMensagemDOM(t, r, anexo, h);
            const chat = chats.find(c => c.id === currentChatId);
            if (chat) {
                if (chat.messages.length <= 1 && r === 'user') {
                    chat.title = t.substring(0, 25).replace(/<[^>]*>?/gm, '') + '...';
                    document.getElementById('currentChatTitle').innerText = chat.pinned ? '📌 ' + chat.title : chat.title;
                }
                chat.messages.push({remetente: r, texto: t, anexo, hora: h});
                chat.timestamp = Date.now(); salvarChatsStorage();
            }
        }
        async function enviarBackend(texto, anexo) {
            const key = apiKeyInput.value.trim(), mod = document.getElementById('modelSelector').value;
            if (!key) {
                adicionarMsg("⚠️ Insira sua chave API do OpenRouter na barra lateral esquerda.", "athena");
                return null;
            }
            const typing = document.createElement('div'); typing.className = "message athena typing-indicator"; typing.innerText = "⚡ Processando...";
            document.getElementById('chatMessages').appendChild(typing);
            try {
                const res = await fetch('/api/chat', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({mensagem: texto, api_key: key, anexo, modelo: mod})});
                const d = await res.json(); typing.remove();
                if (d.status === 'sucesso') { adicionarMsg(d.resposta, "athena"); return d.resposta; }
                else { adicionarMsg("⚠️ " + d.resposta, "athena"); return null; }
            } catch(e) { typing.remove(); adicionarMsg("⚠️ Erro de conexão com o servidor.", "athena"); return null; }
        }
        function enviarMensagem() {
            const input = document.getElementById('chatInput'), txt = input.value.trim();
            if (!txt && !anexoBase64) return;
            adicionarMsg(txt || "[Anexo]", "user", anexoBase64);
            const tEnvio = txt, aEnvio = anexoBase64; input.value = ""; removerAnexo();
            enviarBackend(tEnvio, aEnvio);
        }
        document.getElementById('chatInput').addEventListener('keypress', e => { if (e.key === 'Enter') enviarMensagem(); });
        function toggleAttachMenu() { const m = document.getElementById('attachMenu'); m.style.display = m.style.display === 'flex' ? 'none' : 'flex'; }
        function abrirSeletor(tipo) { fileInput.accept = tipo; fileInput.click(); document.getElementById('attachMenu').style.display = 'none'; }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    key, msg, anexo, mod = data.get("api_key"), data.get("mensagem", ""), data.get("anexo"), data.get("modelo", "openrouter/auto")
    if not key or "sk-or-v1" not in key:
        return jsonify({"status": "erro", "resposta": "Chave OpenRouter inválida ou ausente. Insira no campo da barra lateral."})
    
    headers = {"Authorization": f"Bearer {key.strip()}", "Content-Type": "application/json"}
    content = []
    if msg: content.append({"type": "text", "text": msg})
    if anexo and anexo.startswith("data:image"): content.append({"type": "image_url", "image_url": {"url": anexo}})
    elif anexo: content.append({"type": "text", "text": "[Arquivo enviado]"})
    if not content: content = [{"type": "text", "text": "Olá"}]

    payload = {
        "model": mod if mod != "openrouter/auto" else "google/gemini-2.0-flash-001",
        "messages": [{"role": "system", "content": "Você é a Athena, uma assistente inteligente, analítica, acolhedora e sábia."}, {"role": "user", "content": content if len(content) > 1 else content[0]["text"]}]
    }
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=25).json()
        if "choices" in r: return jsonify({"status": "sucesso", "resposta": r["choices"][0]["message"]["content"]})
        return jsonify({"status": "erro", "resposta": str(r.get("error", "Erro desconhecido na API"))})
    except Exception as e:
        return jsonify({"status": "erro", "resposta": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)