import os
import json
import socket
import requests
import subprocess
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ==========================================
# 1. ESTRUTURA DE DIRETÓRIOS
# ==========================================
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_DIR = os.path.join(APP_DIR, 'Dados')
os.makedirs(DADOS_DIR, exist_ok=True)

# ==========================================
# 2. BLINDAGEM MÁXIMA DO HD (PATH JAIL)
# ==========================================
def verificar_se_e_seguro(caminho_desejado):
    caminho_absoluto = os.path.abspath(caminho_desejado)
    if not caminho_absoluto.startswith(APP_DIR):
        raise PermissionError("🔒 ACESSO NEGADO: A IA tentou violar o limite do diretório seguro.")
    return caminho_absoluto

# ==========================================
# 3. INTERFACE DE CHAT VISUAL (FRONT-END EMBUTIDO)
# ==========================================
HTML_CHAT = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Athena IA - Orquestrador Local</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e2e; color: #cdd6f4; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
        #chat-box { flex-grow: 1; background-color: #313244; padding: 20px; border-radius: 10px; overflow-y: auto; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .mensagem { margin-bottom: 15px; padding: 10px 15px; border-radius: 8px; max-width: 80%; line-height: 1.5; }
        .user { background-color: #89b4fa; color: #11111b; align-self: flex-end; margin-left: auto; }
        .ia { background-color: #45475a; color: #cdd6f4; align-self: flex-start; }
        .input-area { display: flex; gap: 10px; }
        input[type="text"] { flex-grow: 1; padding: 15px; border-radius: 8px; border: none; background-color: #45475a; color: white; outline: none; font-size: 16px; }
        button { padding: 15px 25px; background-color: #89b4fa; color: #11111b; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px; transition: 0.2s; }
        button:hover { background-color: #74c7ec; }
    </style>
</head>
<body>
    <h2 style="text-align: center; margin-top: 0;">🧠 Athena IA (HD Local)</h2>
    <div id="chat-box" style="display: flex; flex-direction: column;"></div>
    
    <div class="input-area">
        <input type="text" id="user-input" placeholder="Digite sua mensagem para o orquestrador..." onkeypress="handleEnter(event)">
        <button onclick="enviarMensagem()">Enviar</button>
    </div>

    <script>
        const historico = [];
        
        function appendMessage(sender, text, isUser) {
            const chatBox = document.getElementById('chat-box');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'mensagem ' + (isUser ? 'user' : 'ia');
            msgDiv.innerHTML = `<strong>${sender}:</strong><br>${text.replace(/\n/g, '<br>')}`;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function enviarMensagem() {
            const inputField = document.getElementById('user-input');
            const mensagem = inputField.value.trim();
            if (!mensagem) return;

            appendMessage('Você', mensagem, true);
            inputField.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensagem: mensagem, historico: historico })
                });
                const data = await response.json();
                
                if(data.erro) {
                    appendMessage('Erro', data.erro, false);
                } else {
                    appendMessage('Athena IA', data.resposta, false);
                    historico.push({ role: "user", content: mensagem });
                    historico.push({ role: "assistant", content: data.resposta });
                }
            } catch (err) {
                appendMessage('Sistema', 'Falha ao conectar com a IA.', false);
            }
        }

        function handleEnter(e) { if (e.key === 'Enter') enviarMensagem(); }
    </script>
</body>
</html>
"""

# ==========================================
# 4. ROTAS DO SERVIDOR
# ==========================================
@app.route('/')
def home():
    # Carrega a interface gráfica do chat direto no navegador
    return render_template_string(HTML_CHAT)

@app.route('/api/chat', methods=['POST'])
def chat():
    dados_usuario = request.json
    mensagem = dados_usuario.get('mensagem')
    historico = dados_usuario.get('historico', [])

    prompt_sistema = (
        "Você é um Agente Orquestrador Autônomo operando em um ambiente isolado. "
        "Você tem capacidade de auxiliar no design de lógica e estruturação, implementando ativamente o "
        "sistema de progresso hierárquico contendo os níveis: Inerte, Aspirante, Resiliente, Veterano e Elite. "
        "Você é blindado e NÃO tem acesso a arquivos pessoais do usuário. Somente interaja com o contexto fornecido."
    )

    mensagens_formatadas = [{"role": "system", "content": prompt_sistema}]
    mensagens_formatadas.extend(historico)
    mensagens_formatadas.append({"role": "user", "content": mensagem})

    lm_studio_url = "http://127.0.0.1:1234/v1/chat/completions"

    payload = {
        "model": "local-model",
        "messages": mensagens_formatadas,
        "temperature": 0.3
    }

    try:
        resposta_lm = requests.post(lm_studio_url, json=payload, timeout=120)
        resposta_json = resposta_lm.json()
        texto_ia = resposta_json['choices'][0]['message']['content']
        
        salvar_historico_seguro(mensagem, texto_ia)
        return jsonify({"resposta": texto_ia})
    
    except requests.exceptions.ConnectionError:
        return jsonify({"erro": "O servidor do LM Studio não está rodando. Abra o LM Studio e clique em 'Start Server'."}), 500

def salvar_historico_seguro(usuario_msg, ia_msg):
    caminho_arquivo = os.path.join(DADOS_DIR, 'historico_offline.json')
    caminho_seguro = verificar_se_e_seguro(caminho_arquivo)
    
    historico = []
    if os.path.exists(caminho_seguro):
        with open(caminho_seguro, 'r', encoding='utf-8') as f:
            historico = json.load(f)
            
    historico.append({"user": usuario_msg, "ia": ia_msg})
    
    with open(caminho_seguro, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    print("🚀 Servidor Local Athena IA Iniciado!")
    print("👉 Acesse a interface no seu navegador: http://127.0.0.1:5000")
    # Roda exclusivamente localmente na porta 5000
    app.run(host='127.0.0.1', port=5000)
