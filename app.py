import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# O CORS agora será carregado com sucesso graças ao requirements.txt
CORS(app)

# Proteção de chaves via variável de ambiente (Segurança)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

MODELS = {
    "gemini": "google/gemini-2.0-flash-exp:free",
    "qwen": "qwen/qwen-2.5-coder-32b-instruct",
    "llama": "meta-llama/llama-3.3-70b-instruct:free"
}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    model_choice = data.get('model', 'gemini')
    system_prompt = data.get('system_prompt', 'Você é ATHENA IA. Responda com formatação Markdown rigorosa.')
    
    # Roteamento: HD Local (LM Studio) vs Nuvem (OpenRouter)
    if model_choice == 'local':
        api_url = "http://localhost:1234/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        model_id = "local-model" 
    else:
        if not OPENROUTER_API_KEY:
            return jsonify({"error": "Chave da API OpenRouter não configurada no Render."}), 500
            
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        model_id = MODELS.get(model_choice, MODELS["gemini"])

    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 1000 # Prevenção de esgotamento de tokens
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=90)
        
        # Tratamento de erro específico para saldo/tokens (402)
        if response.status_code == 402:
            return jsonify({"error": "Erro 402: Limite de tokens ou saldo esgotado na API."}), 402
            
        response.raise_for_status()
        
        response_data = response.json()
        ai_reply = response_data['choices'][0]['message']['content']
        return jsonify({"reply": ai_reply})

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Falha de Conexão: Servidor local não responde. Verifique se o LM Studio está rodando na porta 1234."}), 503
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": f"Erro na API ({response.status_code}): {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

if __name__ == '__main__':
    # Bind universal para funcionar perfeitamente no Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
