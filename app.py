import os
import sys
import time
import json
import requests
import urllib.request
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# ================= ARQUITETURA DE SEGURANÇA (SANDBOX DE ARQUIVOS) =================
WORKSPACE_DIR = os.path.abspath("./athena_workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A.T.H.E.N.A. OS - v5.3 Agentic Vibe Prime</title>
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
        
        .app-container { width: 100%; max-width: 1400px; height: 96vh; background: var(--bg-negro); display: flex; box-shadow: 0 10px 30px rgba(0,0,0,0.9); border: 1px solid var(--borda-cinza); border-radius: 12px; overflow: hidden; position: relative; }
        
        /* ================= PAINEL LATERAL (SIDEBAR) ================= */
        .sidebar { width: 310px; background: var(--painel-cinza-escuro); border-right: 1px solid var(--borda-cinza); display: flex; flex-direction: column; }
        .sidebar-header { padding: 16px; background: var(--painel-cabecalho); display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--borda-cinza); }
        .sidebar-title { font-weight: 700; font-size: 15px; color: var(--dourado-claro); display: flex; align-items: center; gap: 6px; }
        .badge-prime { background: var(--dourado-escuro); color: #fff; font-size: 11px; font-weight: bold; padding: 3px 8px; border-radius: 12px; border: 1px solid var(--dourado-medio); }
        
        .sidebar-actions { padding: 14px; display: flex; flex-direction: column; gap: 10px; border-bottom: 1px solid var(--borda-cinza); }
        .btn-new-chat { background: linear-gradient(135deg, var(--dourado-claro), var(--dourado-medio)); color: #000; font-weight: 700; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-size: 14px; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 10px rgba(245, 158, 11, 0.2); transition: 0.2s; }
        .btn-new-chat:hover { transform: translateY(-1px); box-shadow: 0 6px 15px rgba(245, 158, 11, 0.4); background: linear-gradient(135deg, #fcd34d, var(--dourado-claro)); }
        
        .api-input-box { background: var(--bg-negro); border: 1px solid var(--borda-cinza); padding: 8px 10px; border-radius: 6px; display: flex; align-items: center; gap: 6px; }
        .api-input-box span { font-size: 12px; }
        .api-input-box input { background: transparent; border: none; color: var(--texto-claro); font-size: 12px; width: 100%; outline: none; }
        .api-input-box input::placeholder { color: #52525b; }

        .btn-memory { background: #27272a; color: var(--dourado-claro); border: 1px solid var(--borda-cinza); padding: 8px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center; gap: 6px; }
        .btn-memory:hover { border-color: var(--dourado-medio); background: #3f3f46; }

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
        
        .header-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        .select-modern { background: var(--painel-cinza-escuro); color: var(--texto-claro); border: 1px solid var(--borda-cinza); padding: 7px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; outline: none; cursor: pointer; }
        .select-modern option { background: var(--painel-cinza-escuro); color: white; }

        .btn-live { background: var(--painel-cinza-escuro); color: var(--dourado-claro); border: 1px solid var(--dourado-escuro); padding: 7px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 5px; transition: 0.3s; }
        .btn-live:hover { background: var(--dourado-profundo); color: #fff; }
        .btn-live.active { background: var(--dourado-medio); color: #000; border-color: var(--dourado-claro); animation: pulseGold 2s infinite; }
        @keyframes pulseGold { 0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.6); } 70% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); } 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); } }

        .btn-pip { background: #27272a; color: var(--texto-claro); border: 1px solid var(--borda-cinza); padding: 7px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer; display: none; align-items: center; gap: 4px; }
        .btn-pip:hover { border-color: var(--dourado-claro); color: var(--dourado-claro); }
        
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
        
        .msg-footer { display: flex; justify-content: flex-end; align-items: center; gap: 8px; margin-top: 10px; font-size: 11px; }
        .timestamp { color: rgba(255,255,255,0.5); }
        
        .btn-action-msg { background: rgba(0,0,0,0.4); border: 1px solid var(--borda-cinza); color: var(--texto-cinza); padding: 3px 8px; border-radius: 12px; cursor: pointer; font-size: 11px; transition: 0.2s; display: flex; align-items: center; gap: 4px; }
        .btn-action-msg:hover { color: var(--dourado-claro); border-color: var(--dourado-escuro); }
        .btn-action-msg.active { background: var(--dourado-medio); color: #000; font-weight: bold; border-color: var(--dourado-claro); }

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

        /* Modal Memória do Usuário */
        .modal-bg { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 50; justify-content: center; align-items: center; }
        .modal-box { background: var(--painel-cabecalho); width: 500px; padding: 24px; border-radius: 12px; border: 1px solid var(--borda-cinza); display: flex; flex-direction: column; gap: 14px; }
        .modal-box h3 { color: var(--dourado-claro); font-size: 16px; }
        .modal-box p { font-size: 12px; color: var(--texto-cinza); line-height: 1.5; }
        .modal-box textarea { width: 100%; height: 120px; background: #27272a; border: 1px solid #3f3f46; color: white; padding: 10px; border-radius: 6px; font-size: 13px; outline: none; resize: none; }
        .modal-box textarea:focus { border-color: var(--dourado-medio); }
        .modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
        .btn-modal-close { background: #3f3f46; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .btn-modal-save { background: var(--dourado-medio); color: black; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>

    <div class="app-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <!-- LOGO ALTERADA PARA CORUJA 🦉 -->
                <div class="sidebar-title">🦉 A.T.H.E.N.A. OS</div>
                <span class="badge-prime">v5.3 Prime</span>
            </div>
            
            <div class="sidebar-actions">
                <button class="btn-new-chat" onclick="criarNovaConversa()">
                    <span>+ Nova Conversa</span>
                </button>
                <div class="api-input-box" title="Sua chave API conectada">
                    <span>🔑</span>
                    <input type="password" id="apiKeyInput" placeholder="Chave API Ativa...">
                </div>
                <button class="btn-memory" onclick="abrirModalMemoria()" title="Personalizar aprendizado da IA sobre você">
                    🧠 Memória & Perfil (Aprender sobre você)
                </button>
            </div>

            <div class="chat-list" id="chatList"></div>
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
                    <!-- ADIÇÃO ESTRATÉGICA 2: SELETOR DE MODO CLÍNICO / MÉDICO -->
                    <select class="select-modern" id="medicalModeSelect" title="Modo de estruturação de raciocínio médico">
                        <option value="normal">📋 Padrão Flow</option>
                        <option value="semiologia">🩺 Caso Clínico & Semiológico (Etiologia/Fisiopatologia)</option>
                    </select>

                    <select class="select-modern" id="modelSelect">
                        <option value="auto">⚡ Automática (Smart Vibe)</option>
                        <option value="gemini-flash">🧠 Gemini 2.0 Flash (Velocidade Extrema)</option>
                        <option value="deepseek-r1">💡 DeepSeek R1 Free (Lógica & Código)</option>
                        <option value="llama-70b">🔥 Llama 3.3 70B Free (Robusto)</option>
                    </select>
                    
                    <select class="select-modern" id="speechSpeed" title="Velocidade da voz da IA">
                        <option value="0.75">0.75x</option>
                        <option value="1.0" selected>1.0x</option>
                        <option value="1.25">1.25x</option>
                        <option value="1.5">1.5x</option>
                        <option value="2.0">2.0x (Máxima)</option>
                    </select>

                    <button class="btn-pip" id="btnPip" onclick="ativarPiP()" title="Fixar câmera na tela inteira em qualquer aba/app">📌 PiP</button>
                    <button class="btn-stop-audio" id="btnStopAudio" onclick="interromperVoz()">🔇 Parar Voz</button>
                    <button class="btn-live" id="btnLiveToggle" onclick="alternarModoLive()">🟢 Modo Live</button>
                </div>
            </div>

            <div class="live-video-box" id="liveVideoBox">
                <video id="webcamVideo" autoplay playsinline muted></video>
                <div class="live-status-tag" id="liveTag">Pronta</div>
            </div>

            <div class="chat-messages" id="chatMessages"></div>

            <div class="preview-box" id="previewBox">
                <span id="previewText">✔ Anexo carregado</span>
                <button onclick="removerAnexo()">X Remover</button>
            </div>

            <div class="attach-menu" id="attachMenu">
                <div class="attach-item" onclick="abrirSeletor('image/*')">🖼️ Imagem ou Foto</div>
                <div class="attach-item" onclick="abrirSeletor('video/*')">🎥 Vídeo ou Mídia</div>
                <div class="attach-item" onclick="abrirSeletor('audio/*')">🎵 Áudio ou Música</div>
                <div class="attach-item" onclick="abrirSeletor('.pdf,.doc,.docx,.txt,.xlsx,.md')">📄 Documento / Arquivo</div>
            </div>

            <input type="file" id="fileInputGlobal">

            <div class="chat-input-area">
                <button class="icon-btn" title="Anexar arquivo" onclick="toggleAttachMenu()">📎</button>
                <input type="text" id="chatInput" placeholder="Digite sua mensagem, peça para vasculhar a web ou cole prints (Ctrl+V)..." autofocus>
                <button class="icon-btn" id="btnGravarAudio" title="Gravar áudio" onclick="alternarGravacaoAudio()">🎤</button>
                <button class="send-btn" onclick="enviarMensagem()">➤</button>
            </div>
        </div>
    </div>

    <!-- Modal Memória -->
    <div class="modal-bg" id="modalMemoria">
        <div class="modal-box">
            <h3>🧠 Perfil e Memória de Longo Prazo</h3>
            <p>Especifique abaixo quem você é, seus gostos (Vibe Coding, FIRE, estudos médicos) e instruções para seus projetos. A IA consultará isso em todo atendimento:</p>
            <textarea id="memoriaInput" placeholder="Ex: Sou estudante de medicina focado em semiologia. Gosto de resumos em Markdown para o Obsidian. Pratico Vibe Coding no projeto Poder do Flow..."></textarea>
            <div class="modal-actions">
                <button class="btn-modal-close" onclick="fecharModalMemoria()">Cancelar</button>
                <button class="btn-modal-save" onclick="salvarMemoria()">Salvar Perfil</button>
            </div>
        </div>
    </div>

    <script>
        const DEFAULT_API_KEY = "sk-or-v1-sua-chave-padrao-aqui"; 
        const MAX_MESSAGES = 30;
        let conversas = JSON.parse(localStorage.getItem('athena_v5_chats')) || [];
        let activeChatId = localStorage.getItem('athena_v5_active_id') || null;
        let userMemory = localStorage.getItem('athena_user_memory') || "O usuário é estudante de medicina, programador adepto do Vibe Coding e investidor da cultura FIRE.";

        const apiKeyInput = document.getElementById('apiKeyInput');
        let savedKey = localStorage.getItem('openrouter_key') || DEFAULT_API_KEY;
        apiKeyInput.value = savedKey;
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
            if (conversas.length === 0) criarNovaConversa("Nossa 1° conversa (Vibe Coding)");
            else {
                if (!activeChatId || !conversas.find(c => c.id === activeChatId)) activeChatId = conversas[0].id;
                renderizarSidebar(); renderizarMensagens();
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
                id: novoId, title: titulo,
                messages: [{
                    id: "msg-" + Date.now(),
                    text: `Sua sessão **${titulo}** foi iniciada. Conectada à internet, com memória ativa e suporte ao Obsidian (v5.3). Como posso ajudar no seu flow hoje?`,
                    sender: "athena", pinned: true,
                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }]
            };
            conversas.unshift(novaConv); activeChatId = novoId; salvarDados(); renderizarSidebar(); renderizarMensagens();
        }

        function selecionarConversa(id) { activeChatId = id; salvarDados(); renderizarSidebar(); renderizarMensagens(); }

        function excluirConversa(e, id) {
            e.stopPropagation();
            if (confirm("Deseja realmente excluir esta conversa?")) {
                conversas = conversas.filter(c => c.id !== id);
                if (conversas.length === 0) criarNovaConversa();
                else if (activeChatId === id) activeChatId = conversas[0].id;
                salvarDados(); renderizarSidebar(); renderizarMensagens();
            }
        }

        function renderizarSidebar() {
            const list = document.getElementById('chatList'); list.innerHTML = "";
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
                
                const btnPinClass = msg.pinned ? "btn-action-msg active" : "btn-action-msg";
                const btnPinText = msg.pinned ? "📌 Fixada" : "📍 Fixar";
                
                let botoesAcao = "";
                if (msg.sender === 'athena') {
                    botoesAcao += `<button class="btn-action-msg" onclick="reproduzirMensagemPorId('${msg.id}')">🔊 Ouvir</button>`;
                    // ADIÇÃO ESTRATÉGICA 1: BOTÃO DE EXPORTAÇÃO DIRETA PARA OBSIDIAN (.md)
                    botoesAcao += `<button class="btn-action-msg" onclick="exportarParaObsidian('${msg.id}')" title="Baixar nota formatada para o Obsidian">💎 .md</button>`;
                }
                botoesAcao += `<button class="${btnPinClass}" onclick="alternarFixar('${msg.id}')">${btnPinText}</button>`;
                
                conteudo += `
                    <div class="msg-footer">
                        <span class="timestamp">${msg.time}</span>
                        ${botoesAcao}
                    </div>
                `;
                div.innerHTML = conteudo;
                chatMessages.appendChild(div);
            });
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // ADIÇÃO ESTRATÉGICA 1 (FUNÇÃO DE EXPORTAÇÃO OBSIDIAN)
        function exportarParaObsidian(id) {
            const atual = conversas.find(c => c.id === activeChatId);
            if (!atual) return;
            const msg = atual.messages.find(m => m.id === id);
            if (!msg) return;

            const frontmatter = `---\\ndata: ${new Date().toISOString().split('T')[0]}\\ntags: [athena, estudo, semiologia, vibe-coding]\\n---\\n\\n`;
            const conteudoMd = frontmatter + `# Nota Athena\\n\\n` + msg.text;
            const blob = new Blob([conteudoMd], { type: 'text/markdown;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Athena-Nota-${Date.now()}.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        function reproduzirMensagemPorId(id) {
            const atual = conversas.find(c => c.id === activeChatId);
            if (!atual) return;
            const msg = atual.messages.find(m => m.id === id);
            if (msg) falarTexto(msg.text);
        }

        function adicionarMensagem(texto, remetente, anexo = null) {
            const atual = conversas.find(c => c.id === activeChatId);
            if (!atual) return;
            if (remetente === "user" && atual.messages.length <= 2 && atual.title.startsWith("Conversa")) {
                atual.title = texto.substring(0, 24) + "...";
            }
            const novaMsg = {
                id: "msg-" + Date.now() + "-" + Math.random().toString(36).substr(2, 4),
                text: texto, sender: remetente, anexo: anexo, pinned: false,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };
            atual.messages.push(novaMsg);
            while (atual.messages.length > MAX_MESSAGES) {
                const idx = atual.messages.findIndex(m => !m.pinned);
                if (idx !== -1) atual.messages.splice(idx, 1); else break;
            }
            salvarDados(); renderizarSidebar(); renderizarMensagens();
            return novaMsg;
        }

        function alternarFixar(idMsg) {
            const atual = conversas.find(c => c.id === activeChatId);
            if (!atual) return;
            const msg = atual.messages.find(m => m.id === idMsg);
            if (msg) { msg.pinned = !msg.pinned; salvarDados(); renderizarMensagens(); }
        }

        // ================= SISTEMA DE ARQUIVOS =================
        function toggleAttachMenu() { attachMenu.style.display = attachMenu.style.display === 'flex' ? 'none' : 'flex'; }
        function abrirSeletor(aceitarTipo) { fileInputGlobal.accept = aceitarTipo; fileInputGlobal.click(); attachMenu.style.display = 'none'; }
        
        fileInputGlobal.addEventListener('change', e => { if (e.target.files[0]) processarArquivo(e.target.files[0]); });
        window.addEventListener('paste', e => {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let i in items) { if (items[i].kind === 'file') { e.preventDefault(); processarArquivo(items[i].getAsFile()); break; } }
        });

        function processarArquivo(file) {
            const reader = new FileReader();
            reader.onload = evt => {
                anexoAtualBase64 = evt.target.result; tipoAnexoAtual = file.type;
                previewBox.style.display = 'flex'; previewText.innerText = `✔ Anexo carregado (${file.name || 'Print capturado'})`;
            };
            reader.readAsDataURL(file);
        }
        function removerAnexo() { anexoAtualBase64 = null; tipoAnexoAtual = null; fileInputGlobal.value = ""; previewBox.style.display = 'none'; }

        // ================= VOZ & LIVE MODE =================
        function getVozFeminina() {
            const vozes = window.speechSynthesis.getVoices();
            const ptVozes = vozes.filter(v => v.lang.includes('pt') || v.lang.includes('BR'));
            const nomesJovens = ['thalita', 'francisca', 'victoria', 'yara', 'luciana', 'camila', 'natural', 'google português do brasil', 'female'];
            for (let nome of nomesJovens) {
                const vozEncontrada = ptVozes.find(v => v.name.toLowerCase().includes(nome));
                if (vozEncontrada) return vozEncontrada;
            }
            return ptVozes[0] || vozes[0];
        }

        function interromperVoz() {
            if (window.speechSynthesis) window.speechSynthesis.cancel();
            document.getElementById('btnStopAudio').style.display = 'none';
            if (modoLiveAtivo) { estadoLive = 'parado'; document.getElementById('liveTag').innerText = "🎤 Pode falar..."; iniciarReconhecimentoDeVoz(); }
        }

        let modoLiveAtivo = false; let streamVideoLive = null; let speechRecognition = null; let estadoLive = 'parado'; let timeoutSilencio = null;

        async function alternarModoLive() {
            const btn = document.getElementById('btnLiveToggle');
            const videoBox = document.getElementById('liveVideoBox');
            const videoElement = document.getElementById('webcamVideo');
            const statusSubtext = document.getElementById('statusSubtext');
            const btnPip = document.getElementById('btnPip');

            if (!modoLiveAtivo) {
                try {
                    streamVideoLive = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                    videoElement.srcObject = streamVideoLive; videoBox.style.display = 'block';
                    modoLiveAtivo = true; btn.className = "btn-live active"; btn.innerHTML = "🔴 Modo Live ON";
                    btnPip.style.display = "inline-flex";
                    statusSubtext.innerText = "⚡ Modo Live Ativo (Voz & Visão)"; statusSubtext.style.color = "#fbbf24";
                    iniciarReconhecimentoDeVoz();
                } catch (err) { alert("Permissão de câmera ou microfone negada."); }
            } else {
                modoLiveAtivo = false; estadoLive = 'parado'; clearTimeout(timeoutSilencio); interromperVoz();
                if (document.pictureInPictureElement) try { await document.exitPictureInPicture(); } catch(e){}
                if (streamVideoLive) streamVideoLive.getTracks().forEach(track => track.stop());
                if (speechRecognition) try { speechRecognition.abort(); } catch(e){}
                videoElement.srcObject = null; videoBox.style.display = 'none'; btn.className = "btn-live"; btn.innerHTML = "🟢 Modo Live";
                btnPip.style.display = "none";
                statusSubtext.innerText = "Pronta para uso"; statusSubtext.style.color = "#fbbf24";
            }
        }

        async function ativarPiP() {
            const videoElement = document.getElementById('webcamVideo');
            if (document.pictureInPictureElement) {
                await document.exitPictureInPicture();
            } else if (document.pictureInPictureEnabled && videoElement.srcObject) {
                await videoElement.requestPictureInPicture();
            } else {
                alert("Ative o Modo Live primeiro para fixar a janela.");
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
                            
                            const comandoRepetir = /repita.*(última|mensagem|resposta|voz)|fale.*(novamente|de novo)/i;
                            if (comandoRepetir.test(transcricaoAtual)) {
                                document.getElementById('liveTag').innerText = "🔊 Repetindo...";
                                const atual = conversas.find(c => c.id === activeChatId);
                                if (atual) {
                                    const ultimasIA = atual.messages.filter(m => m.sender === 'athena');
                                    if (ultimasIA.length > 0) {
                                        falarTexto(ultimasIA[ultimasIA.length - 1].text);
                                        return;
                                    }
                                }
                            }

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
            interromperVoz();
            estadoLive = 'falando'; document.getElementById('liveTag').innerText = "🔊 Falando...";
            document.getElementById('btnStopAudio').style.display = 'inline-flex';
            
            const textoLimpo = texto.replace(/[*#_`~]/g, '').replace(/\\n/g, ' ');
            const utterance = new SpeechSynthesisUtterance(textoLimpo);
            utterance.voice = getVozFeminina(); utterance.lang = 'pt-BR';
            utterance.rate = parseFloat(document.getElementById('speechSpeed').value) || 1.0;
            utterance.pitch = 1.08;

            utterance.onend = () => { document.getElementById('btnStopAudio').style.display = 'none'; estadoLive = 'parado'; if (modoLiveAtivo) { document.getElementById('liveTag').innerText = "🎤 Pode falar..."; iniciarReconhecimentoDeVoz(); } };
            utterance.onerror = () => { document.getElementById('btnStopAudio').style.display = 'none'; estadoLive = 'parado'; if (modoLiveAtivo) iniciarReconhecimentoDeVoz(); };
            window.speechSynthesis.speak(utterance);
        }

        function abrirModalMemoria() { document.getElementById('memoriaInput').value = userMemory; document.getElementById('modalMemoria').style.display = 'flex'; }
        function fecharModalMemoria() { document.getElementById('modalMemoria').style.display = 'none'; }
        function salvarMemoria() {
            userMemory = document.getElementById('memoriaInput').value.trim();
            localStorage.setItem('athena_user_memory', userMemory);
            fecharModalMemoria();
            alert("🧠 Perfil atualizado! A IA considerará isso em todas as respostas.");
        }

        chatInput.addEventListener('keypress', e => { if (e.key === 'Enter') enviarMensagem(); });

        async function enviarParaBackend(mensagemTexto, anexo) {
            const apiKey = apiKeyInput.value.trim();
            const atual = conversas.find(c => c.id === activeChatId);
            const medicalMode = document.getElementById('medicalModeSelect').value;
            
            const typingDiv = document.createElement('div');
            typingDiv.id = "msgTyping"; typingDiv.className = "message athena typing-indicator";
            typingDiv.innerHTML = "🦉 <i>Athena conectando à internet e raciocinando...</i>";
            chatMessages.appendChild(typingDiv); chatMessages.scrollTop = chatMessages.scrollHeight;
            document.getElementById('statusSubtext').innerText = "Processando...";

            const contextoEnvio = atual ? atual.messages.map(m => ({
                sender: m.sender, text: m.text, pinned: m.pinned
            })) : [];

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        mensagem: mensagemTexto, api_key: apiKey, anexo: anexo, 
                        historico: contextoEnvio, modelo_pref: document.getElementById('modelSelect').value,
                        user_memory: userMemory, medical_mode: medicalMode 
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

def vasculhar_web(url_ou_termo):
    """Lê o texto limpo de uma página web ou faz busca básica de links"""
    try:
        if not url_ou_termo.startswith("http"):
            url_ou_termo = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(url_ou_termo)}"
        req = urllib.request.Request(
            url_ou_termo, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8', errors='ignore')
            import re
            texto = re.sub(r'<[^>]+>', ' ', html)
            texto = re.sub(r'\s+', ' ', texto).strip()
            return f"[Conteúdo extraído da Web ({url_ou_termo[:35]}...)]: " + texto[:2500]
    except Exception as e:
        return f"[Falha ao acessar web: {str(e)}]"

@app.route("/api/chat", methods=["POST"])
def processar_chat():
    dados = request.json or {}
    api_key = dados.get("api_key")
    mensagem = dados.get("mensagem", "")
    anexo = dados.get("anexo")
    historico = dados.get("historico", [])
    modelo_pref = dados.get("modelo_pref", "auto")
    user_memory = dados.get("user_memory", "")
    medical_mode = dados.get("medical_mode", "normal")
    
    if not api_key or api_key.strip() == "" or "sua-chave" in api_key:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        
    if not api_key or "sua-chave" in api_key:
        return jsonify({"status": "erro", "resposta": "Nenhuma chave API configurada. Insira na barra lateral ou no código."})

    contexto_extra = ""
    if "vasculhar" in mensagem.lower() or "acessar" in mensagem.lower() or "http" in mensagem.lower() or "pesquise na web" in mensagem.lower():
        import re
        urls = re.findall(r'(https?://\S+)', mensagem)
        alvo = urls[0] if urls else mensagem
        contexto_extra = "\n\n" + vasculhar_web(alvo)

    # ADIÇÃO ESTRATÉGICA 2: DIRETRIZ DE MODO CLÍNICO / SEMIOLÓGICO NO PROMPT
    instrucao_medica = ""
    if medical_mode == "semiologia":
        instrucao_medica = (
            "\n\n[MODO CLÍNICO & SEMIOLÓGICO ATIVO]: Responda estruturando estritamente o conteúdo nos seguintes tópicos: "
            "1. Etiologia | 2. Fisiopatologia | 3. Critérios de Diferenciação Diagnóstica | 4. Manobras Semiológicas / Conduta Prática."
        )

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com",
        "X-Title": "A.T.H.E.N.A. Vibe Coding"
    }
    
    system_prompt = {
        "role": "system",
        "content": (
            "Seu nome é Athena. Você é um sistema operacional IA multimodal especialista em Vibe Coding, arquitetura de software, "
            "estudos médicos/clínicos (semiologia, patologia) e estratégias de alta performance (Flow, FIRE). "
            "Sua persona é de uma mulher adulta jovem (~30 anos), brilhante, extremamente elegante, pragmática e acolhedora. "
            f"\n\n[MEMÓRIA E PERFIL DO USUÁRIO]: {user_memory}"
            f"{instrucao_medica}"
            "\n\nInstrução: Priorize gerar código limpo, formatação em Markdown (perfeita para o Obsidian) e explicações direto ao ponto."
        )
    }
    
    messages_payload = [system_prompt]
    
    for item in historico[-12:]:
        role = "user" if item["sender"] == "user" else "assistant"
        prefixo = "[NOTA FIXADA PRIORITÁRIA]: " if item.get("pinned") else ""
        messages_payload.append({"role": role, "content": prefixo + item["text"]})
    
    content_atual = []
    texto_final = mensagem + contexto_extra
    if texto_final:
        content_atual.append({"type": "text", "text": texto_final})
    if anexo:
        if anexo.startswith("data:image"):
            content_atual.append({"type": "image_url", "image_url": {"url": anexo}})
        else:
            content_atual.append({"type": "text", "text": "[O usuário enviou um arquivo/áudio em anexo]"})
            
    if not content_atual:
        content_atual = [{"type": "text", "text": "Olá, Athena."}]
        
    messages_payload.append({"role": "user", "content": content_atual if len(content_atual) > 1 else content_atual[0]["text"]})

    if modelo_pref == "gemini-flash": modelos_disponiveis = ["google/gemini-2.0-flash-001", "google/gemini-1.5-flash"]
    elif modelo_pref == "deepseek-r1": modelos_disponiveis = ["deepseek/deepseek-r1:free", "deepseek/deepseek-chat"]
    elif modelo_pref == "llama-70b": modelos_disponiveis = ["meta-llama/llama-3.3-70b-instruct:free", "openrouter/auto"]
    else: modelos_disponiveis = ["google/gemini-2.0-flash-001", "deepseek/deepseek-r1:free", "meta-llama/llama-3.3-70b-instruct:free", "openrouter/auto"]
    
    ultimo_erro = ""
    for modelo in modelos_disponiveis:
        payload = {"model": modelo, "max_tokens": 2500, "temperature": 0.7, "messages": messages_payload}
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=25)
            res_json = resp.json()
            if "choices" in res_json and len(res_json["choices"]) > 0:
                return jsonify({"status": "sucesso", "resposta": res_json["choices"][0]["message"]["content"]})
            elif "error" in res_json:
                ultimo_erro = res_json["error"].get("message", str(res_json["error"]))
        except Exception as e:
            ultimo_erro = str(e)

    return jsonify({"status": "erro", "resposta": f"Falha no OpenRouter: {ultimo_erro}"})

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=porta, debug=False)
