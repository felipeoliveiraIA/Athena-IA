import os
import sys
import time
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A.T.H.E.N.A. OS - v5.0 Gold Prime</title>
    <style>
        :root {
            --bg-negro: #09090b;
            --painel-cinza-escuro: #121214;
            --painel-cabecalho: #18181b;
            --borda-cinza: #27272a;
            --texto-claro: #f3f4f6;
            --texto-cinza: #9ca3af;
            --dourado-claro: #fbbf24;
            --dourado-medio: #f59e0b;
            --dourado-escuro: #b45309;
            --dourado-profundo: #92400e;
            --cinza-bala-bot: #1f2937;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Helvetica, Arial, sans-serif; }
        body { background-color: #000000; color: var(--texto-claro); height: 100vh; display: flex; justify-content: center; align-items: center; }
        
        .app-container { width: 100%; max-width: 1350px; height: 96vh; background: var(--bg-negro); display: flex; box-shadow: 0 10px 30px rgba(0,0,0,0.9); border: 1px solid var(--borda-cinza); border-radius: 12px; overflow: hidden; position: relative; }
        
        /* ================= PAINEL LATERAL (SIDEBAR) ================= */
        .sidebar { width: 310px; background: var(--painel-cinza-escuro); border-right: 1px solid var(--borda-cinza); display: flex; flex-direction: column; }
        .sidebar-header { padding: 16px; background: var(--painel-cabecalho); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--borda-cinza); }
        .sidebar-title { font-weight: 700; font-size: 15px; color: var(--dourado-claro); display: flex; align-items: center; gap: 6px; }
        .badge-prime { background: var(--dourado-escuro); color: #fff; font-size: 11px; font-weight: bold; padding: 3px 8px; border-radius: 12px; border: 1px solid var(--dourado-medio); }
        
        .sidebar-actions { padding: 14px; display: flex; flex-direction: column; gap: 10px; border-bottom: 1px solid var(--borda-cinza); }
        .btn-new-chat { background: linear-gradient(135deg, var(--dourado-claro), var(--dourado-medio)); color: #000; font-weight: 700; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-size: 14px; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 10px rgba(245, 158, 11, 0.2); transition: 0.2s; }
        .btn-new-chat:hover { transform: translateY(-1px); box-shadow: 0 6px 15px rgba(245, 158, 11, 0.4); background: linear-gradient(135deg, #fcd34d, var(--dourado-claro)); }
        
        .api-input-box { background: var(--bg-negro); border: 1px solid var(--borda-cinza); padding: 8px 10px; border-radius: 6px; display: flex; align-items: center; }
        .api-input-box input { background: transparent; border: none; color: var(--texto-claro); font-size: 12px; width: 100%; outline: none; }
        .api-input-box input::placeholder { color: #52525b; }

        .chat-list { flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 6px; }
        .chat-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; background: var(--painel-cabecalho); border: 1px solid transparent; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .chat-item:hover { border-color: var(--dourado-escuro); background: #202024; }
        .chat-item.active { border-color: var(--dourado-medio); background: #27272a; box-shadow: inset 3px 0 0 var(--dourado-claro); }
        .chat-item-info { overflow: hidden; flex: 1; }
        .chat-item-title { font-size: 13px; font-weight: 600; color: var(--texto-claro); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .chat-item-sub { font-size: 11px; color: var(--texto-cinza); margin-top: 3px; }
        .btn-delete-chat { background: none; border: none; color: #52525b; font-size: 14px; cursor: pointer; padding: 4px; transition: 0.2s; }
        .btn-delete-chat:hover { color: #ef4444; }

        /* ================= ÁREA DE CHAT PRINCIPAL ================= */
        .chat-main { flex: 1; display: flex; flex-direction: column; background: var(--bg-negro); position: relative; }
        .chat-header { padding: 12px 20px; background: var(--painel-cabecalho); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--borda-cinza); min-height: 65px; }
        .chat-header-user { display: flex; align-items: center; gap: 12px; }
        .avatar { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--dourado-medio), var(--dourado-escuro)); display: flex; align-items: center; justify-content: center; font-weight: 800; color: #000; font-size: 16px; border: 1px solid var(--dourado-claro); }
        .chat-header-info h3 { font-size: 15px; font-weight: 700; color: var(--texto-claro); }
        .chat-header-info span { font-size: 12px; color: var(--dourado-claro); font-weight: 500; }
        
        .header-actions { display: flex; gap: 10px; align-items: center; }
        .select-modern { background: var(--painel-cinza-escuro); color: var(--texto-claro); border: 1px solid var(--borda-cinza); padding: 7px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; outline: none; cursor: pointer; }
        .select-modern option { background: var(--painel-cinza-escuro); color: white; }

        .btn-live { background: var(--painel-cinza-escuro); color: var(--dourado-claro); border: 1px solid var(--dourado-escuro); padding: 7px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: 0.3s; }
        .btn-live:hover { background: var(--dourado-profundo); color: #fff; }
        .btn-live.active { background: var(--dourado-medio); color: #000; border-color: var(--dourado-claro); animation: pulseGold 2s infinite; }
        @keyframes pulseGold { 0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.6); } 70% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); } 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); } }

        .btn-stop-audio { background: #dc2626; color: white; border: none; padding: 7px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer; display: none; align-items: center; gap: 5px; }

        /* Câmera Flutuante (Modo Live) */
        .live-video-box { display: none; position: absolute; top: 80px; right: 25px; width: 180px; height: 135px; background: #000; border: 2px solid var(--dourado-claro); border-radius: 10px; overflow: hidden; z-index: 10; box-shadow: 0 8px 20px rgba(0,0,0,0.8); }
        .live-video-box video { width: 100%; height: 100%; object-fit: cover; }
        .live-status-tag { position: absolute; bottom: 6px; left: 6px; background: rgba(0,0,0,0.8); color: var(--dourado-claro); font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px; border: 1px solid var(--dourado-escuro); }

        /* Mensagens */
        .chat-messages { flex: 1; padding: 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
        .message { max-width: 75%; padding: 14px 18px; border-radius: 10px; font-size: 14px; line-height: 1.6; position: relative; word-wrap: break-word; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
        .message.user { background: linear-gradient(135deg, var(--dourado-escuro), var(--dourado-profundo)); color: #fff; align-self: flex-end; border-top-right-radius: 2px; border: 1px solid var(--dourado-medio); }
        .message.athena { background: var(--cinza-bala-bot); color: var(--texto-claro); align-self: flex-start; border-top-left-radius: 2px; border-left: 4px solid var(--dourado-medio); border-top: 1px solid var(--borda-cinza); border-right: 1px solid var(--borda-cinza); border-bottom: 1px solid var(--borda-cinza); }
        
        .message.pinned { border: 1px solid var(--dourado-claro) !important; box-shadow: 0 0 10px rgba(251, 191, 36, 0.15); }
        
        .msg-footer { display: flex; justify-content: flex-end; align-items: center; gap: 10px; margin-top: 8px; font-size: 11px; }
        .timestamp { color: rgba(255,255,255,0.5); }
        .pin-btn { background: rgba(0,0,0,0.3); border: 1px solid var(--borda-cinza); color: var(--texto-cinza); padding: 3px 8px; border-radius: 12px; cursor: pointer; font-size: 11px; transition: 0.2s; display: flex; align-items: center; gap: 4px; }
        .pin-btn:hover { color: var(--dourado-claro); border-color: var(--dourado-escuro); }
        .pin-btn.active { background: var(--dourado-medio); color: #000; font-weight: bold; border-color: var(--dourado-claro); }

        .typing-indicator { font-style: italic; color: var(--dourado-claro); animation: blink 1.5s infinite; background: #18181b !important; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

        /* Anexos e Barra Inferior */
        .preview-box { padding: 10px 20px; background: var(--painel-cinza-escuro); font-size: 13px; color: var(--dourado-claro); display: none; border-top: 1px solid var(--borda-cinza); align-items: center; justify-content: space-between; }
        .preview-box button { background: #dc2626; color: white; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: bold; }

        .attach-menu { display: none; position: absolute; bottom: 75px; left: 20px; background: var(--painel-cabecalho); border: 1px solid var(--borda-cinza); border-radius: 8px; padding: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.9); z-index: 20; flex-direction: column; gap: 4px; width: 200px; }
        .attach-item { display: flex; align-items: center; gap: 10px; color: var(--texto-claro); cursor: pointer; font-size: 13px; padding: 8px 10px; border-radius: 6px; transition: 0.2s; }
        .attach-item:hover { background: var(--dourado-escuro); color: #fff; }

        .chat-input-area { padding: 14px 20px; background: var(--painel-cabecalho); display: flex; align-items: center; gap: 12px; border-top: 1px solid var(--borda-cinza); position: relative; }
        .chat-input-area input[type="text"] { flex: 1; padding: 14px 16px; background: #27272a; border: 1px solid #3f3f46; border-radius: 8px; color: white; font-size: 14px; outline: none; transition: 0.2s; }
        .chat-input-area input[type="text"]:focus { border-color: var(--dourado-medio); background: #1f1f23; }
        .icon-btn { background: none; border: none; color: #a1a1aa; font-size: 20px; cursor: pointer; padding: 6px; transition: 0.2s; }
        .icon-btn:hover { color: var(--dourado-claro); }
        .icon-btn.recording { color: #ef4444; animation: pulseRed 1s infinite; }
        @keyframes pulseRed { 0% { transform: scale(1); } 50% { transform: scale(1.2); } 100% { transform: scale(1); } }
        
        .send-btn { background: linear-gradient(135deg, var(--dourado-claro), var(--dourado-medio)); border: none; color: #000; width: 44px; height: 44px; border-radius: 8px; cursor: pointer; font-size: 18px; font-weight: bold; display: flex; align-items: center; justify-content: center; transition: 0.2s; box-shadow: 0 4px 10px rgba(245, 158, 11, 0.2); }
        .send-btn:hover { transform: scale(1.05); background: linear-gradient(135deg, #fcd34d, var(--dourado-claro)); }
        
        input[type="file"] { display: none; }
    </style>
</head>
<body>

    <div class="app-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">⚡ A.T.H.E.N.A. OS</div>
                <span class="badge-prime">v5.0 Gold</span>
            </div>
            
            <div class="sidebar-actions">
                <button class="btn-new-chat" onclick="criarNovaConversa()">
                    <span>+ Nova Conversa</span>
                </button>
                <div class="api-input-box">
                    <input type="password" id="apiKeyInput" placeholder="🔑 Chave API OpenRouter...">
                </div>
            </div>

            <div class="chat-list" id="chatList">
                <!-- Lista de conversas preenchida via JS -->
            </div>
        </div>

        <!-- Chat Principal -->
        <div class="chat-main">
            <div class="chat-header">
                <div class="chat-header-user">
                    <div class="avatar">AT</div>
                    <div class="chat-header-info">
                        <h3 id="currentChatTitle">Selecione ou Crie uma Conversa</h3>
                        <span id="statusSubtext">Pronta para uso</span>
                    </div>
                </div>
                
                <div class="header-actions">
                    <select class="select-modern" id="modelSelect" title="Modelo de Inteligência">
                        <option value="auto">⚡ Automática (Gold)</option>
                        <option value="gemini">🧠 Gemini 2.0 Flash</option>
                        <option value="llama">🔥 Llama 3.3 70B</option>
                    </select>
                    
                    <select class="select-modern" id="speechSpeed" title="Velocidade da voz">
                        <option value="0.75">0.75x</option>
                        <option value="1.0" selected>1.0x</option>
                        <option value="1.25">1.25x</option>
                        <option value="1.5">1.5x</option>
                    </select>

                    <button class="btn-stop-audio" id="btnStopAudio" onclick="interromperVoz()">🔇 Parar Voz</button>
                    <button class="btn-live" id="btnLiveToggle" onclick="alternarModoLive()">🟢 Modo Live</button>
                </div>
            </div>

            <div class="live-video-box" id="liveVideoBox">
                <video id="webcamVideo" autoplay playsinline muted></video>
                <div class="live-status-tag" id="liveTag">Pronta</div>
            </div>

            <div class="chat-messages" id="chatMessages">
                <!-- Mensagens da conversa ativa -->
            </div>

            <div class="preview-box" id="previewBox">
                <span id="previewText">✔ Anexo carregado</span>
                <button onclick="removerAnexo()">X Remover</button>
            </div>

            <div class="attach-menu" id="attachMenu">
                <div class="attach-item" onclick="abrirSeletor('image/*')">🖼️ Imagem ou Foto</div>
                <div class="attach-item" onclick="abrirSeletor('video/*')">🎥 Vídeo ou Mídia</div>
                <div class="attach-item" onclick="abrirSeletor('audio/*')">🎵 Áudio ou Música</div>
                <div class="attach-item" onclick="abrirSeletor('.pdf,.doc,.docx,.txt,.xlsx')">📄 Documento / Arquivo</div>
            </div>

            <input type="file" id="fileInputGlobal">

            <div class="chat-input-area">
                <button class="icon-btn" title="Anexar arquivo" onclick="toggleAttachMenu()">📎</button>
                <input type="text" id="chatInput" placeholder="Digite sua mensagem (Ctrl+V para colar prints)..." autofocus>
                <button class="icon-btn" id="btnGravarAudio" title="Gravar áudio" onclick="alternarGravacaoAudio()">🎤</button>
                <button class="send-btn" onclick="enviarMensagem()">➤</button>
            </div>
        </div>
    </div>

    <script>
        const MAX_MESSAGES = 25; // Limite para autolimpeza de mensagens não fixadas
        let conversas = JSON.parse(localStorage.getItem('athena_v5_chats')) || [];
        let activeChatId = localStorage.getItem('athena_v5_active_id') || null;

        const apiKeyInput = document.getElementById('apiKeyInput');
        if (localStorage.getItem('openrouter_key')) apiKeyInput.value = localStorage.getItem('openrouter_key');
        apiKeyInput.addEventListener('input', () => localStorage.setItem('openrouter_key', apiKeyInput.value));

        let anexoAtualBase64 = null;
        let tipoAnexoAtual = null;
        const fileInputGlobal = document.getElementById('fileInputGlobal');
        const previewBox = document.getElementById('previewBox');
        const previewText = document.getElementById('previewText');
        const chatInput = document.getElementById('chatInput');
        const chatMessages = document.getElementById('chatMessages');
        const attachMenu = document.getElementById('attachMenu');

        window.onload = () => {
            if (conversas.length === 0) {
                criarNovaConversa("Nossa 1° conversa (Estudos & Flow)");
            } else {
                if (!activeChatId || !conversas.find(c => c.id === activeChatId)) {
                    activeChatId = conversas[0].id;
                }
                renderizarSidebar();
                renderizarMensagens();
            }
        };

        function salvarDados() {
            localStorage.setItem('athena_v5_chats', JSON.stringify(conversas));
            localStorage.setItem('athena_v5_active_id', activeChatId);
        }

        function criarNovaConversa(tituloCustomizado = null) {
            const num = conversas.length + 1;
            const novoId = "chat-" + Date.now();
            const titulo = tituloCustomizado || `Conversa ${num}`;
            
            const novaConv = {
                id: novoId,
                title: titulo,
                messages: [
                    {
                        id: "msg-" + Date.now(),
                        text: `Sua sessão **${titulo}** foi iniciada sob a interface v5.0 Gold Prime. Todas as mensagens e notas fixadas aqui serão salvas localmente. Como posso ajudar?`,
                        sender: "athena",
                        pinned: true,
                        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    }
                ]
            };
            
            conversas.unshift(novaConv);
            activeChatId = novoId;
            salvarDados();
            renderizarSidebar();
            renderizarMensagens();
        }

        function selecionarConversa(id) {
            activeChatId = id;
            salvarDados();
            renderizarSidebar();
            renderizarMensagens();
        }

        function excluirConversa(e, id) {
            e.stopPropagation();
            if (confirm("Deseja realmente excluir esta conversa?")) {
                conversas = conversas.filter(c => c.id !== id);
                if (conversas.length === 0) {
                    criarNovaConversa();
                } else if (activeChatId === id) {
                    activeChatId = conversas[0].id;
                }
                salvarDados();
                renderizarSidebar();
                renderizarMensagens();
            }
        }

        function renderizarSidebar() {
            const list = document.getElementById('chatList');
            list.innerHTML = "";
            
            conversas.forEach(c => {
                const div = document.createElement('div');
                div.className = `chat-item ${c.id === activeChatId ? 'active' : ''}`;
                div.onclick = () => selecionarConversa(c.id);
                
                const ultimaMsg = c.messages.length > 0 ? c.messages[c.messages.length - 1].text.replace(/[*#]/g, '') : "Sem mensagens";
                
                div.innerHTML = `
                    <div class="chat-item-info">
                        <div class="chat-item-title">${c.title}</div>
                        <div class="chat-item-sub">${ultimaMsg.substring(0, 32)}...</div>
                    </div>
                    <button class="btn-delete-chat" onclick="excluirConversa(event, '${c.id}')" title="Excluir">✕</button>
                `;
                list.appendChild(div);
            });
            
            const atual = conversas.find(c => c.id === activeChatId);
            document.getElementById('currentChatTitle').innerText = atual ? atual.title : "Conversa";
        }

        function renderizarMensagens() {
            chatMessages.innerHTML = "";
            const atual = conversas.find(c => c.id === activeChatId);
            if (!atual) return;

            atual.messages.forEach(msg => {
                const div = document.createElement('div');
                div.className = `message ${msg.sender} ${msg.pinned ? 'pinned' : ''}`;
                
                let conteudo = msg.text.replace(/\\n/g, '<br>');
                if (msg.anexo) {
                    if (msg.anexo.startsWith('data:image')) conteudo += `<img src="${msg.anexo}" style="margin-top:8px; max-width:100%; border-radius:6px;">`;
                    else if (msg.anexo.startsWith('data:audio')) conteudo += `<audio controls src="${msg.anexo}" style="margin-top:8px;"></audio>`;
                    else if (msg.anexo.startsWith('data:video')) conteudo += `<video controls src="${msg.anexo}" style="margin-top:8px; max-width:100%;"></video>`;
                    else conteudo += `<div style="margin-top:8px; background:#121214; padding:6px 10px; border-radius:6px; font-size:12px; border:1px solid #27272a;">📄 Arquivo Anexado</div>`;
                }
                
                const btnPinClass = msg.pinned ? "pin-btn active" : "pin-btn";
                const btnPinText = msg.pinned ? "📌 Fixada" : "📍 Fixar";
                
                conteudo += `
                    <div class="msg-footer">
                        <span class="timestamp">${msg.time}</span>
                        <button class="${btnPinClass}" onclick="alternarFixar('${msg.id}')">${btnPinText}</button>
                    </div>
                `;
                
                div.innerHTML = conteudo;
                chatMessages.appendChild(div);
            });
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function adicionarMensagem(texto, remetente, anexo = null) {
            const atual = conversas.find(c => c.id === activeChatId);
            if (!atual) return;

            // Se for a primeira mensagem real do usuário, renomeia o título da conversa inteligentemente
            if (remetente === "user" && atual.messages.length <= 2 && atual.title.startsWith("Conversa")) {
                atual.title = texto.substring(0, 24) + "...";
            }

            const novaMsg = {
                id: "msg-" + Date.now() + "-" + Math.random().toString(36).substr(2, 4),
                text: texto,
                sender: remetente,
                anexo: anexo,
                pinned: false,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };

            atual.messages.push(novaMsg);

            // Autolimpeza de memória (mantém apenas as últimas MAX_MESSAGES, mas protege as Fixadas)
            while (atual.messages.length > MAX_MESSAGES) {
                const idx = atual.messages.findIndex(m => !m.pinned);
                if (idx !== -1) atual.messages.splice(idx, 1);
                else break;
            }

            salvarDados();
            renderizarSidebar();
            renderizarMensagens();
            return novaMsg;
        }

        function alternarFixar(idMsg) {
            const atual = conversas.find(c => c.id === activeChatId);
            if (!atual) return;
            const msg = atual.messages.find(m => m.id === idMsg);
            if (msg) {
                msg.pinned = !msg.pinned;
                salvarDados();
                renderizarMensagens();
            }
        }

        // ================= SISTEMA DE ARQUIVOS =================
        function toggleAttachMenu() { attachMenu.style.display = attachMenu.style.display === 'flex' ? 'none' : 'flex'; }
        function abrirSeletor(aceitarTipo) { fileInputGlobal.accept = aceitarTipo; fileInputGlobal.click(); attachMenu.style.display = 'none'; }
        
        fileInputGlobal.addEventListener('change', e => { if (e.target.files[0]) processarArquivo(e.target.files[0]); });
        window.addEventListener('paste', e => {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let i in items) {
                if (items[i].kind === 'file') { e.preventDefault(); processarArquivo(items[i].getAsFile()); break; }
            }
        });

        function processarArquivo(file) {
            const reader = new FileReader();
            reader.onload = evt => {
                anexoAtualBase64 = evt.target.result;
                tipoAnexoAtual = file.type;
                previewBox.style.display = 'flex';
                previewText.innerText = `✔ Anexo carregado (${file.name || 'Print capturado'})`;
            };
            reader.readAsDataURL(file);
        }

        function removerAnexo() {
            anexoAtualBase64 = null; tipoAnexoAtual = null; fileInputGlobal.value = ""; previewBox.style.display = 'none';
        }

        // ================= VOZ FEMININA ELEGANTE E LIVE MODE =================
        let vozesNoNavegador = [];
        window.speechSynthesis.onvoiceschanged = () => { vozesNoNavegador = window.speechSynthesis.getVoices(); };

        function getVozFeminina() {
            const vozes = window.speechSynthesis.getVoices();
            const ptVozes = vozes.filter(v => v.lang.includes('pt') || v.lang.includes('BR'));
            const nomesFemininos = ['francisca', 'luciana', 'vitória', 'raquel', 'maria', 'yara', 'fernanda', 'helena', 'camila', 'female', 'natural'];
            for (let voz of ptVozes) {
                for (let nome of nomesFemininos) { if (voz.name.toLowerCase().includes(nome)) return voz; }
            }
            return ptVozes[0] || vozes[0];
        }

        function interromperVoz() {
            if (window.speechSynthesis) window.speechSynthesis.cancel();
            document.getElementById('btnStopAudio').style.display = 'none';
            if (modoLiveAtivo) {
                estadoLive = 'parado';
                document.getElementById('liveTag').innerText = "🎤 Pode falar...";
                iniciarReconhecimentoDeVoz();
            }
        }

        let modoLiveAtivo = false; let streamVideoLive = null; let speechRecognition = null; let estadoLive = 'parado'; let timeoutSilencio = null;

        async function alternarModoLive() {
            const btn = document.getElementById('btnLiveToggle');
            const videoBox = document.getElementById('liveVideoBox');
            const videoElement = document.getElementById('webcamVideo');
            const statusSubtext = document.getElementById('statusSubtext');

            if (!modoLiveAtivo) {
                try {
                    streamVideoLive = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                    videoElement.srcObject = streamVideoLive; videoBox.style.display = 'block';
                    modoLiveAtivo = true; btn.className = "btn-live active"; btn.innerHTML = "🔴 Modo Live ON";
                    statusSubtext.innerText = "⚡ Modo Live Ativo (Voz & Visão)"; statusSubtext.style.color = "#fbbf24";
                    iniciarReconhecimentoDeVoz();
                } catch (err) { alert("Permissão de câmera ou microfone negada."); }
            } else {
                modoLiveAtivo = false; estadoLive = 'parado'; clearTimeout(timeoutSilencio); interromperVoz();
                if (streamVideoLive) streamVideoLive.getTracks().forEach(track => track.stop());
                if (speechRecognition) try { speechRecognition.abort(); } catch(e){}
                videoElement.srcObject = null; videoBox.style.display = 'none'; btn.className = "btn-live"; btn.innerHTML = "🟢 Modo Live";
                statusSubtext.innerText = "Pronta para uso"; statusSubtext.style.color = "#fbbf24";
            }
        }

        function iniciarReconhecimentoDeVoz() {
            if (!modoLiveAtivo || estadoLive !== 'parado') return;
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) return;

            speechRecognition = new SpeechRecognition(); speechRecognition.lang = 'pt-BR'; speechRecognition.continuous = true; speechRecognition.interimResults = true;
            speechRecognition.onstart = () => { estadoLive = 'ouvindo'; document.getElementById('liveTag').innerText = "🎤 Pode falar..."; };

            speechRecognition.onresult = (event) => {
                clearTimeout(timeoutSilencio); let transcricaoAtual = "";
                for (let i = 0; i < event.results.length; ++i) { transcricaoAtual += event.results[i][0].transcript; }

                if (transcricaoAtual.trim().length > 0) {
                    document.getElementById('liveTag').innerText = "👂 Ouvindo...";
                    timeoutSilencio = setTimeout(async () => {
                        if (estadoLive === 'ouvindo' && transcricaoAtual.trim().length > 1) {
                            estadoLive = 'processando'; try { speechRecognition.stop(); } catch(e){}
                            document.getElementById('liveTag').innerText = "🧠 Raciocinando...";
                            
                            const videoElement = document.getElementById('webcamVideo');
                            const canvas = document.createElement('canvas');
                            canvas.width = videoElement.videoWidth || 640; canvas.height = videoElement.videoHeight || 480;
                            canvas.getContext('2d').drawImage(videoElement, 0, 0);
                            const frameBase64 = canvas.toDataURL('image/jpeg');

                            adicionarMensagem(`🎙️ *[Voz]:* ${transcricaoAtual}`, "user", null);
                            const respostaTexto = await enviarParaBackend(transcricaoAtual, frameBase64);
                            if (respostaTexto) falarTexto(respostaTexto);
                            else { estadoLive = 'parado'; if (modoLiveAtivo) iniciarReconhecimentoDeVoz(); }
                        }
                    }, 2500);
                }
            };
            speechRecognition.onerror = () => { clearTimeout(timeoutSilencio); estadoLive = 'parado'; setTimeout(() => { if (modoLiveAtivo && estadoLive === 'parado') iniciarReconhecimentoDeVoz(); }, 1000); };
            speechRecognition.onend = () => { clearTimeout(timeoutSilencio); if (estadoLive === 'ouvindo') estadoLive = 'parado'; if (modoLiveAtivo && estadoLive === 'parado') setTimeout(() => { try { iniciarReconhecimentoDeVoz(); } catch(e){} }, 300); };
            try { speechRecognition.start(); } catch(e){}
        }

        function falarTexto(texto) {
            if (!modoLiveAtivo) return;
            estadoLive = 'falando'; document.getElementById('liveTag').innerText = "🔊 Falando...";
            document.getElementById('btnStopAudio').style.display = 'inline-flex';
            
            const textoLimpo = texto.replace(/[*#_`~]/g, '').replace(/\\n/g, ' ');
            const utterance = new SpeechSynthesisUtterance(textoLimpo);
            utterance.voice = getVozFeminina(); utterance.lang = 'pt-BR';
            utterance.rate = parseFloat(document.getElementById('speechSpeed').value) || 1.0;
            utterance.pitch = 0.95; // Tom sábio, maduro e elegante

            utterance.onend = () => { document.getElementById('btnStopAudio').style.display = 'none'; estadoLive = 'parado'; if (modoLiveAtivo) { document.getElementById('liveTag').innerText = "🎤 Pode falar..."; iniciarReconhecimentoDeVoz(); } };
            utterance.onerror = () => { document.getElementById('btnStopAudio').style.display = 'none'; estadoLive = 'parado'; if (modoLiveAtivo) iniciarReconhecimentoDeVoz(); };
            window.speechSynthesis.speak(utterance);
        }

        // ================= COMUNICAÇÃO COM O SERVIDOR =================
        chatInput.addEventListener('keypress', e => { if (e.key === 'Enter') enviarMensagem(); });

        async function enviarParaBackend(mensagemTexto, anexo) {
            const apiKey = apiKeyInput.value.trim();
            const atual = conversas.find(c => c.id === activeChatId);
            
            const typingDiv = document.createElement('div');
            typingDiv.id = "msgTyping";
            typingDiv.className = "message athena typing-indicator";
            typingDiv.innerHTML = "⚡ <i>Athena raciocinando em modo Gold...</i>";
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            document.getElementById('statusSubtext').innerText = "Processando...";

            const contextoEnvio = atual ? atual.messages.map(m => ({
                sender: m.sender,
                text: m.text,
                pinned: m.pinned
            })) : [];

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        mensagem: mensagemTexto, 
                        api_key: apiKey, 
                        anexo: anexo, 
                        historico: contextoEnvio,
                        modelo_pref: document.getElementById('modelSelect').value 
                    })
                });
                const data = await res.json();
                const t = document.getElementById('msgTyping'); if (t) t.remove();
                document.getElementById('statusSubtext').innerText = modoLiveAtivo ? "⚡ Modo Live Ativo" : "Pronta para uso";

                if (data.status === 'sucesso') {
                    adicionarMensagem(data.resposta, "athena");
                    return data.resposta;
                } else {
                    adicionarMensagem("⚠️ " + data.resposta, "athena");
                    return null;
                }
            } catch (err) {
                const t = document.getElementById('msgTyping'); if (t) t.remove();
                document.getElementById('statusSubtext').innerText = "Pronta para uso";
                adicionarMensagem("⚠️ Erro de conexão com o servidor no Render.", "athena");
                return null;
            }
        }

        function enviarMensagem() {
            const texto = chatInput.value.trim();
            if (!texto && !anexoAtualBase64) return;

            let textoExibicao = texto || (tipoAnexoAtual && tipoAnexoAtual.includes('audio') ? "🎵 Áudio gravado enviado" : "[Anexo enviado]");
            adicionarMensagem(textoExibicao, "user", anexoAtualBase64);

            const envioTexto = texto; const envioAnexo = anexoAtualBase64;
            chatInput.value = ""; removerAnexo();
            enviarParaBackend(envioTexto, envioAnexo);
        }
        
        let mediaRecorder = null; let chunksAudio = []; let gravandoAudio = false;
        async function alternarGravacaoAudio() {
            const btn = document.getElementById('btnGravarAudio');
            if (!gravandoAudio) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream); chunksAudio = [];
                    mediaRecorder.ondataavailable = e => chunksAudio.push(e.data);
                    mediaRecorder.onstop = () => {
                        const blob = new Blob(chunksAudio, { type: 'audio/webm' });
                        const reader = new FileReader();
                        reader.onload = evt => { anexoAtualBase64 = evt.target.result; tipoAnexoAtual = 'audio/webm'; previewBox.style.display = 'flex'; previewText.innerText = "✔ Áudio gravado"; };
                        reader.readAsDataURL(blob); stream.getTracks().forEach(track => track.stop());
                    };
                    mediaRecorder.start(); gravandoAudio = true; btn.classList.add('recording'); chatInput.placeholder = "🔴 Gravando áudio...";
                } catch (err) { alert("Erro ao acessar microfone."); }
            } else {
                mediaRecorder.stop(); gravandoAudio = false; btn.classList.remove('recording'); chatInput.placeholder = "Digite sua mensagem...";
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/chat", methods=["POST"])
def processar_chat():
    dados = request.json or {}
    api_key = dados.get("api_key")
    mensagem = dados.get("mensagem", "")
    anexo = dados.get("anexo")
    historico = dados.get("historico", [])
    modelo_pref = dados.get("modelo_pref", "auto")
    
    if not api_key or api_key.strip() == "" or "sk-or-v1-sua-chave" in api_key:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        
    if not api_key or "sk-or-v1-sua-chave" in api_key:
        return jsonify({
            "status": "erro", 
            "resposta": "Por favor, insira sua chave API válida do OpenRouter no campo da barra lateral esquerda."
        })

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com",
        "X-Title": "A.T.H.E.N.A. OS Gold"
    }
    
    system_prompt = {
        "role": "system",
        "content": (
            "Seu nome é Athena. Você é um sistema operacional IA multimodal avançado rodando na interface v5.0 Gold Prime. "
            "Sua persona é a de uma mulher adulta, intelectual, extremamente sábia, analítica e acolhedora. "
            "Exprese raciocínios estruturados, profundos e precisos, utilizando uma linguagem elegante. "
            "Dê atenção prioritária e absoluta às mensagens que contiverem a tag [NOTA FIXADA PRIORITÁRIA], pois são memórias "
            "fundamentais que o usuário decidiu fixar na sua arquitetura de raciocínio."
        )
    }
    
    messages_payload = [system_prompt]
    
    # Adiciona o histórico recente e notas fixadas
    for item in historico[-12:]:
        role = "user" if item["sender"] == "user" else "assistant"
        prefixo = "[NOTA FIXADA PRIORITÁRIA]: " if item.get("pinned") else ""
        messages_payload.append({"role": role, "content": prefixo + item["text"]})
    
    content_atual = []
    if mensagem:
        content_atual.append({"type": "text", "text": mensagem})
    if anexo:
        if anexo.startswith("data:image"):
            content_atual.append({"type": "image_url", "image_url": {"url": anexo}})
        else:
            content_atual.append({"type": "text", "text": "[O usuário enviou um arquivo em anexo]"})
            
    if not content_atual:
        content_atual = [{"type": "text", "text": "Olá, Athena."}]
        
    messages_payload.append({"role": "user", "content": content_atual if len(content_atual) > 1 else content_atual[0]["text"]})

    # Definição inteligente de modelos com base na sua escolha no topo da tela
    if modelo_pref == "gemini":
        modelos_disponiveis = ["google/gemini-2.0-flash-001", "google/gemini-1.5-flash"]
    elif modelo_pref == "llama":
        modelos_disponiveis = ["meta-llama/llama-3.3-70b-instruct:free", "openrouter/auto"]
    else:
        modelos_disponiveis = [
            "google/gemini-2.0-flash-001",
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemini-1.5-flash",
            "openrouter/auto"
        ]
    
    ultimo_erro = ""
    for modelo in modelos_disponiveis:
        payload = {
            "model": modelo,
            "max_tokens": 1500,
            "temperature": 0.7,
            "messages": messages_payload
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=25)
            res_json = resp.json()
            
            if "choices" in res_json and len(res_json["choices"]) > 0:
                resposta_ia = res_json["choices"][0]["message"]["content"]
                return jsonify({"status": "sucesso", "resposta": resposta_ia})
            elif "error" in res_json:
                ultimo_erro = res_json["error"].get("message", str(res_json["error"]))
        except Exception as e:
            ultimo_erro = str(e)

    return jsonify({"status": "erro", "resposta": f"Falha no OpenRouter: {ultimo_erro}"})

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=porta, debug=False)
