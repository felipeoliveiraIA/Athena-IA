import os
import requests
from flask import Flask, render_template, request, jsonify

# Inicialização do aplicativo Flask
app = Flask(__name__, template_folder='templates', static_folder='static')

# Resgate seguro da chave de API via variável de ambiente do Render
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# ==========================================
# 1. ROTA RAIZ (SOLUÇÃO DO ERRO 404)
# ==========================================
@app.route('/')
def index():
    """
    Entrega a interface visual ATHENA OS v5.2 contida em templates/index.html.
    """
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Erro ao carregar o template index.html. Verifique a pasta 'templates/': {str(e)}", 500

# ==========================================
# 2. ROTA DE PROCESSAMENTO DAS IAs
# ==========================================
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    provider = data.get('provider', 'cloud') # 'cloud' (OpenRouter) ou 'local' (LM Studio)
    messages = data.get('messages', [])
    model = data.get('model', 'google/gemini-2.0-flash-001')

    # --- PROCESSAMENTO LOCAL (LM Studio / HD Local) ---
    if provider == 'local':
        try:
            response = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7
                },
                timeout=10
            )
            return jsonify(response.json())
        except requests.exceptions.ConnectionError:
            return jsonify({
                "error": "Servidor local (LM Studio) indisponível. Verifique se o aplicativo está rodando na porta 1234."
            }), 503
        except Exception as e:
            return jsonify({"error": f"Erro no LM Studio: {str(e)}"}), 500

    # --- PROCESSAMENTO NA NUVEM (OpenRouter) ---
    else:
        if not OPENROUTER_API_KEY:
            return jsonify({
                "error": "Chave de API (OPENROUTER_API_KEY) não encontrada nas variáveis de ambiente do Render."
            }), 400

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://athena-ia.onrender.com",
            "X-Title": "ATHENA IA"
        }

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 2000
        }

        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            # Tratamento de saldo / limite de tokens (Erro 402)
            if res.status_code == 402:
                return jsonify({
                    "error": "Erro 402: Créditos insuficientes na conta do OpenRouter."
                }), 402

            return jsonify(res.json()), res.status_code

        except Exception as e:
            return jsonify({"error": f"Falha na comunicação com o OpenRouter: {str(e)}"}), 500

# ==========================================
# 3. CONFIGURAÇÃO DE EXECUÇÃO EM NUVEM (RENDER)
# ==========================================
if __name__ == '__main__':
    # O Render atribui a porta dinamicamente via variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    # Bind em 0.0.0.0 é obrigatório para servidores em nuvem
    app.run(host='0.0.0.0', port=port, debug=False)
