import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Busca a chave de API de forma segura nas variáveis de ambiente do Render/OS
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "SUA_CHAVE_AQUI_SE_TESTAR_LOCAL")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    model_provider = data.get('provider', 'openrouter') # 'openrouter' ou 'local'
    model_name = data.get('model', 'google/gemini-2.0-flash-exp:free')
    messages = data.get('messages', [])
    system_prompt = data.get('system_prompt', '')

    # Injeta o System Prompt com o Perfil e Gamificação do usuário
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    if model_provider == 'openrouter':
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://athena-os.com",
            "X-Title": "ATHENA OS v5.3"
        }
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 2000 # Aumentado para suportar respostas clínicas completas
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return jsonify({"reply": result['choices'][0]['message']['content']})
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro API OpenRouter ({response.status_code if hasattr(response, 'status_code') else 'Rede'}): {str(e)}"
            if hasattr(response, 'text'):
                error_msg += f" Detalhes: {response.text}"
            return jsonify({"error": error_msg}), 500

    elif model_provider == 'local':
        # Conexão com LM Studio local na porta 1234
        url = "http://127.0.0.1:1234/v1/chat/completions"
        try:
            response = requests.post(url, json={"messages": messages, "temperature": 0.7})
            response.raise_for_status()
            result = response.json()
            return jsonify({"reply": result['choices'][0]['message']['content']})
        except requests.exceptions.ConnectionError:
            return jsonify({"error": "Falha no LM Studio Local: Certifique-se de que o servidor local está rodando na porta 1234."}), 503

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
