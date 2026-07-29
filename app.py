import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Permite comunicação com o frontend

# Chave de API protegida por variável de ambiente (Render)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "SUA_CHAVE_AQUI_CASO_RODE_LOCAL")

# Modelos gratuitos atualizados e validados
MODELS = {
    "gemini": "google/gemini-2.0-flash-exp:free",
    "llama": "meta-llama/llama-3.3-70b-instruct:free",
    "qwen": "qwen/qwen-vl-plus:free"
}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    model_choice = data.get('model', 'gemini')
    system_prompt = data.get('system_prompt', 'Você é A.T.H.E.N.A. OS. Responda com formatação Markdown rigorosa.')
    
    # Roteamento HD Local vs Nuvem
    if model_choice == 'local':
        api_url = "http://localhost:1234/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        model_id = "local-model" # LM Studio ignora o nome do modelo
    else:
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
        "max_tokens": 2000
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status() # Dispara exceção para erros 4xx e 5xx
        
        response_data = response.json()
        ai_reply = response_data['choices'][0]['message']['content']
        return jsonify({"reply": ai_reply})

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Erro de Conexão: Servidor indisponível. Se estiver usando HD Local, verifique se o LM Studio está rodando na porta 1234."}), 503
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": f"Erro na API OpenRouter ({response.status_code}): {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500

if __name__ == '__main__':
    # Bind para deploy Cloud (Render) ou execução local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
