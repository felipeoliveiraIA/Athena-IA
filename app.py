import os
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Leitura segura da nuvem
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

SYSTEM_PROMPT_BASE = """
Você é a A.T.H.E.N.A. OS.
Diretriz de Memória Aditiva: Você opera acumulando contexto. Jamais descarte preferências antigas do usuário.
Diretriz de Gamificação OBRIGATÓRIA: O ecossistema opera sob uma hierarquia rígida de 5 níveis de progresso, sendo eles:
1. Inerte
2. Aspirante
3. Resiliente
4. Veterano
5. Elite
Reflita essa terminologia de gamificação quando apropriado na conversa.
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
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "Chave API não detectada no Render. Configure 'OPENROUTER_API_KEY' na aba Environment."}), 500

    data = request.json
    user_message = data.get('message', '')
    modo_semiologico = data.get('modoSemiologico', False)
    
    system_content = SYSTEM_PROMPT_BASE
    if modo_semiologico:
        system_content += "\n" + SYSTEM_PROMPT_SEMIOLOGIA

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_message}
    ]

    payload = {
        "model": "qwen/qwen-2.5-coder-32b-instruct", 
        "messages": messages,
        "max_tokens": 1000, 
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Timeout de 60 segundos para evitar que a requisição caia se o Render estiver lento
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        response_data = response.json()

        if "error" in response_data:
            error_code = response_data['error'].get('code', 'Desconhecido')
            error_msg = response_data['error'].get('message', 'Erro da API do OpenRouter')
            if error_code == 402:
                return jsonify({"error": "Erro 402: Seus créditos no OpenRouter acabaram. Recarregue a conta."}), 402
            return jsonify({"error": f"Erro API: {error_msg}"}), 400

        reply = response_data['choices'][0]['message']['content']
        return jsonify({"reply": reply})

    except Exception as e:
        # Erro genérico e real capturado pelo backend
        return jsonify({"error": f"Falha interna do servidor nuvem: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
