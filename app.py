from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Athena - IA</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --panel-bg: #1e293b;
            --text-color: #f8fafc;
            --accent-color: #3b82f6;
            --accent-hover: #2563eb;
            --border-color: #334155;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        header {
            background-color: var(--panel-bg);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
        }
        h1 {
            margin: 0;
            font-size: 1.25rem;
            color: var(--accent-color);
        }
        .status-badge {
            background: #059669;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
        }
        .message {
            padding: 1rem;
            border-radius: 0.5rem;
            max-width: 80%;
            line-height: 1.5;
            word-wrap: break-word;
        }
        .message.user {
            background-color: #2563eb;
            align-self: flex-end;
        }
        .message.bot {
            background-color: var(--panel-bg);
            border: 1px solid var(--border-color);
            align-self: flex-start;
        }
        .input-area {
            background-color: var(--panel-bg);
            padding: 1rem 2rem;
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: center;
        }
        .input-wrapper {
            max-width: 800px;
            width: 100%;
            display: flex;
            gap: 0.5rem;
        }
        input[type="text"] {
            flex: 1;
            padding: 0.75rem 1rem;
            border-radius: 0.375rem;
            border: 1px solid var(--border-color);
            background-color: #0f172a;
            color: white;
            font-size: 1rem;
            outline: none;
        }
        input[type="text"]:focus {
            border-color: var(--accent-color);
        }
        button {
            background-color: var(--accent-color);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.375rem;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        }
        button:hover {
            background-color: var(--accent-hover);
        }
        .live-btn {
            background-color: #7c3aed;
        }
        .live-btn:hover {
            background-color: #6d28d9;
        }
    </style>
</head>
<body>
    <header>
        <h1>Athena-IA</h1>
        <div style="display: flex; gap: 10px; align-items: center;">
            <button class="live-btn" id="liveBtn" onclick="toggleLiveMode()">Modo Live: OFF</button>
            <span class="status-badge">Online</span>
        </div>
    </header>

    <div class="chat-container" id="chatContainer">
        <div class="message bot">Olá! Eu sou a Athena. Sistema atualizado e totalmente operacional. Como posso te ajudar hoje?</div>
    </div>

    <div class="input-area">
        <div class="input-wrapper">
            <input type="text" id="userInput" placeholder="Digite sua mensagem aqui..." autofocus>
            <button onclick="sendMessage()">Enviar</button>
        </div>
    </div>

    <script>
        let liveMode = false;

        function toggleLiveMode() {
            liveMode = !liveMode;
            const btn = document.getElementById('liveBtn');
            if (liveMode) {
                btn.style.backgroundColor = '#059669';
                btn.innerText = 'Modo Live: ON';
                appendMessage('Modo Live ativado com sucesso!', 'bot');
            } else {
                btn.style.backgroundColor = '#7c3aed';
                btn.innerText = 'Modo Live: OFF';
                appendMessage('Modo Live desativado.', 'bot');
            }
        }

        document.getElementById('userInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        function appendMessage(text, sender) {
            const container = document.getElementById('chatContainer');
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${sender}`;
            msgDiv.innerText = text;
            container.appendChild(msgDiv);
            container.scrollTop = container.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if (!text) return;

            appendMessage(text, 'user');
            input.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, live: liveMode })
                });
                const data = await response.json();
                appendMessage(data.reply, 'bot');
            } catch (error) {
                appendMessage('Erro de conexão com o servidor.', 'bot');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    is_live = data.get('live', False)
    
    if is_live:
        reply = f"[Modo Live Ativo] Processado em tempo real: '{user_message}'."
    else:
        reply = f"Athena recebeu sua mensagem: '{user_message}'."
        
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
