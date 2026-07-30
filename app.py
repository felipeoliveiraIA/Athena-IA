import os
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Busca a chave de forma segura nas variáveis de ambiente do Render
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    model_provider = data.get('model', 'cloud') # 'cloud' ou 'local'
    system_prompt = data.get('system_prompt', 'Você é a ATHENA IA. Responda em Markdown limpo.')

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'}), 400

    try:
        if model_provider == 'cloud':
            if not OPENROUTER_API_KEY:
                return jsonify({'error': 'Chave da API OpenRouter não configurada no servidor.'}), 500
            
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "qwen/qwen-2.5-coder-32b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 2000
            }
            
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            
            if response.status_code == 402:
                return jsonify({'error': 'Erro 402: Fundos esgotados no OpenRouter.'}), 402
            
            response.raise_for_status()
            ai_reply = response.json()['choices'][0]['message']['content']
            return jsonify({'reply': ai_reply})

        elif model_provider == 'local':
            # LM Studio Local Bridge
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json=payload, timeout=30)
            response.raise_for_status()
            ai_reply = response.json()['choices'][0]['message']['content']
            return jsonify({'reply': ai_reply})

    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Falha de Conexão. Se estiver usando o HD Local, verifique se o LM Studio está rodando na porta 1234.'}), 503
    except Exception as e:
        return jsonify({'error': f'Erro no servidor: {str(e)}'}), 500

if __name__ == '__main__':
    # Bind para Cloud (Render) e Local
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
