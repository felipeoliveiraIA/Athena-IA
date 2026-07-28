import os
import json
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ==========================================
# 1. SINCRONIZADOR NUVEM <-> HD
# ==========================================
CONFIG = {"ngrok_url": ""}

# ==========================================
# 2. INTERFACE DE CHAT VISUAL DA NUVEM
# ==========================================
HTML_CHAT = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Athena IA - Nuvem & HD</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #1e1e2e; color: #cdd6f4; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
        #chat-box { flex-grow: 1; background-color: #313244; padding: 20px; border-radius: 10px; overflow-y: auto; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .mensagem { margin-bottom: 15px; padding: 10px 15px; border-radius: 8px; max-width: 80%; line-height: 1.5; }
        .user { background-color: #89b4fa; color: #11111b; align-self: flex-end; margin-left: auto; }
        .ia { background-color: #45475a; color: #cdd6f4; align-self: flex-start; }
        .sistema { background-color: #f9e2af; color: #11111b; align-self: center; text-align: center; font-weight: bold; width: 100%; }
        .input-area { display: flex; gap: 10px; }
        input[type="text"] { flex-grow: 1; padding: 15px; border-radius: 8px; border: none; background-color: #45475a; color: white; outline: none; font-size: 16px; }
        button { padding: 15px 25px; background-color: #89b4fa; color: #11111b; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px; }
        button:hover { background-color: #74c7ec; }
    </style>
</head>
<body>
    <h2 style="text-align: center; margin-top: 0;">☁️ Athena IA (Conexão Nuvem ↔️ HD)</h2>
    <div id="chat-box" style="display: flex; flex-direction: column;">
        <div class="mensagem sistema">STATUS: Aguardando sincronização. <br>Para conectar ao HD, digite: /sync SEU_LINK_NGROK</div>
    </div>
    
    <div class="input-area">
        <input type="text" id="user-input" placeholder="Digite sua mensagem ou comando /sync..." onkeypress="handleEnter(event)">
        <button onclick="enviarMensagem()">Enviar</button>
    </div>

    <script>
        const historico = [];
        
        function appendMessage(sender, text, tipo) {
            const chatBox = document.getElementById('chat-box');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'mensagem ' + tipo;
            msgDiv.innerHTML = `<strong>${sender}:</strong><br>${text.replace(/\n/g, '<br>')}`;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function enviarMensagem() {
            const inputField = document.getElementById('user-input');
            const mensagem = inputField.value.trim();
            if (!mensagem) return;

            appendMessage('Você', mensagem, 'user');
            inputField.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensagem: mensagem, historico: historico })
                });
                const data = await response.json();
                
                if(data.erro) {
                    appendMessage('Sistema', data.erro, 'sistema');
                } else if(data.sistema) {
                    appendMessage('Sistema', data.sistema, 'sistema');
                } else {
                    appendMessage('Athena IA', data.resposta, 'ia');
                    historico.push({ role: "user", content: mensagem });
                    historico.push({ role: "assistant", content: data.resposta });
                }
            } catch (err) {
                appendMessage('Sistema', 'Falha ao conectar com o servidor Render (Nuvem).', 'sistema');
            }
        }

        function handleEnter(e) { if (e.key === 'Enter') enviarMensagem(); }
    </script>
</body>
</html>
"""

# ==========================================
# 3. ROTAS E LÓGICA DE EXECUÇÃO
# ==========================================
@app.route('/')
def home():
    return render_template_string(HTML_CHAT)

@app.route('/api/chat', methods=['POST'])
def chat():
    dados = request.json
    mensagem = dados.get('mensagem', '')
    historico = dados.get('historico', [])

    # Lógica de sincronização exigida: verifica e atualiza o acesso ao HD
    if mensagem.startswith('/sync '):
        novo_link = mensagem.split(' ', 1)[1].strip()
        if novo_link.endswith('/'):
            novo_link = novo_link[:-1]
        CONFIG["ngrok_url"] = novo_link
        return jsonify({"sistema": f"Sincronização iniciada! A nuvem (Render) agora acessa seu HD via: {novo_link}"})

    if not CONFIG["ngrok_url"]:
        return jsonify({"erro": "HD não sincronizado. Digite /sync [SEU_LINK_NGROK_AQUI] para estabelecer a conexão."})

    # Instruções diretas para a IA
    prompt_sistema = (
        "Você é um Agente Orquestrador Autônomo processando requisições a partir do HD físico do usuário. "
        "Seu foco inclui o desenvolvimento analítico da estrutura do projeto e a manutenção rígida do sistema de "
        "progresso e engajamento hierárquico nos seguintes níveis: Inerte, Aspirante, Resiliente, Veterano e Elite. "
        "Mantenha respostas pragmáticas."
    )

    mensagens_formatadas = [{"role": "system", "content": prompt_sistema}]
    mensagens_formatadas.extend(historico)
    mensagens_formatadas.append({"role": "user", "content": mensagem})

    # A interface na Nuvem dispara a mensagem para o HD físico via Túnel
    url_ia_hd = f"{CONFIG['ngrok_url']}/v1/chat/completions"

    payload = {
        "model": "local-model",
        "messages": mensagens_formatadas,
        "temperature": 0.3
    }

    try:
        # A tentativa rápida de busca de conexão exigida ocorre aqui
        resposta_lm = requests.post(url_ia_hd, json=payload, timeout=45)
        resposta_lm.raise_for_status()
        
        texto_ia = resposta_lm.json()['choices'][0]['message']['content']
        return jsonify({"resposta": texto_ia})
    
    except requests.exceptions.RequestException:
        return jsonify({"erro": "Falha na sincronização imediata. O Render não conseguiu contatar o HD. Verifique se o Ngrok e o LM Studio estão rodando no seu computador."})

if __name__ == '__main__':
    # Libera a porta dinamicamente no Render
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)
