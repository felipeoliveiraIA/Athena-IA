import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates', static_folder='static')
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

@app.route('/')
def index():
    return render_template('index.html')

# CORREÇÃO DEFINITIVA: Rota exata '/chat' conforme exigido pelo seu frontend
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    provider = data.get('provider', 'Nuvem (Qwen Coder)')
    messages = data.get('messages', [])

    # ==========================================
    # SELEÇÃO DE MODELOS AVANÇADOS (VIBE-CODING)
    # ==========================================
    if "Local" in provider:
        # --- PROCESSAMENTO LOCAL (LM Studio / HD Local na porta 1234) ---
        try:
            res = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={"model": "local-model", "messages": messages, "temperature": 0.7},
                timeout=10
            )
            return jsonify(res.json())
        except requests.exceptions.ConnectionError:
            return jsonify({"error": "Servidor local (LM Studio) indisponível. Verifique a porta 1234."}), 503

    else:
        # --- PROCESSAMENTO NUVEM (OpenRouter) ---
        if not OPENROUTER_API_KEY:
            return jsonify({"error": "Chave OPENROUTER_API_KEY não configurada no Render."}), 400

        # Define os modelos super avançados e autônomos para código e orquestração
        if "Qwen" in provider:
            model_id = "qwen/qwen-2.5-coder-32b-instruct"
        else:
            model_id = "google/gemini-pro-1.5" # Gemini avançado

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://athena-ia.onrender.com",
            "X-Title": "ATHENA IA"
        }

        # Teto de tokens mantido para evitar o Erro 402, conforme Relatório v5.2
        payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7
        }

        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            if res.status_code == 402:
                return jsonify({"error": "Erro 402: Créditos insuficientes no OpenRouter."}), 402
            
            return jsonify(res.json()), res.status_code
        except Exception as e:
            return jsonify({"error": f"Falha na nuvem: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
