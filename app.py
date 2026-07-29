import os
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

SYSTEM_PROMPT_BASE = """
Você é a ATHENA IA.
Diretriz de Memória Aditiva: Você opera acumulando contexto. Jamais descarte preferências antigas do usuário.
Diretriz de Gamificação OBRIGATÓRIA: O ecossistema opera sob uma hierarquia rígida de 5 níveis de progresso, sendo eles:
1. Inerte
2. Aspirante
3. Resiliente
4. Veterano
5. Elite
Reflita essa terminologia de gamificação quando apropriado na conversa. Seja concisa, aja como uma parceira de negócios e estudos de alta performance.
"""

SYSTEM_PROMPT_SEMIOLOGIA = """
[MODO SEMIOLÓGICO ATIVADO]
Estruture a resposta médica OBRIGATORIAMENTE nesta exata hierarquia (usando Markdown):
### 1. Etiologia
### 2. Fisiopatologia
### 3. Critérios Diagnósticos
### 4. Conduta
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    modo_semiologico = data.get('modoSemiologico', False)
    model_choice = data.get('model', 'qwen')
    
    system_content = SYSTEM_PROMPT_BASE
    if modo_semiologico:
        system_content += "\n" + SYSTEM_PROMPT_SEMIOLOGIA

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_message}
    ]

    # Roteamento para a IA do HD (LM Studio)
    if model_choice == 'local':
        try:
            response = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={"model": "local-model", "messages": messages, "temperature": 0.7, "max_tokens": 1000},
                timeout=30
            )
            return jsonify({"reply": response.json()['choices'][0]['message']['content']})
        except Exception as e:
            return jsonify({"error": "Falha ao conectar com o HD Local (LM Studio). Verifique se o servidor na porta 1234 está rodando."}), 500

    # Roteamento Nuvem (OpenRouter)
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "Chave API não detectada no Render. Configure 'OPENROUTER_API_KEY'."}), 500

    payload = {
        "model": "qwen/qwen-2.5-coder-32b-instruct" if model_choice == 'qwen' else "google/gemini-pro", 
        "messages": messages,
        "max_tokens": 1000, 
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        response_data = response.json()

        if "error" in response_data:
            error_code = response_data['error'].get('code', 'Desconhecido')
            if error_code == 402:
                return jsonify({"error": "Erro 402: Seus créditos no OpenRouter acabaram. Recarregue a conta."}), 402
            return jsonify({"error": f"Erro API: {response_data['error'].get('message', '')}"}), 400

        return jsonify({"reply": response_data['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({"error": f"Falha interna do servidor nuvem: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
