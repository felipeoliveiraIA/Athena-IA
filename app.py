import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Pega a chave de forma segura do ambiente do servidor (Render/Local)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Diretrizes Absolutas Injetadas via System Prompt
SYSTEM_PROMPT_BASE = """
Você é a A.T.H.E.N.A. OS.
Memória de Personalidade Aditiva: Você sempre assimila as preferências do usuário sem esquecer as anteriores.
O aplicativo de progressão/gamificação deste projeto segue estritamente os 5 níveis:
1. Inerte
2. Aspirante
3. Resiliente
4. Veterano
5. Elite
"""

SYSTEM_PROMPT_SEMIOLOGIA = """
Você está operando no Modo Semiológico. Você deve, OBRIGATORIAMENTE, estruturar a resposta médica utilizando a seguinte hierarquia, sem exceções:
1. Etiologia
2. Fisiopatologia
3. Critérios Diagnósticos
4. Conduta
"""

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    modo_semiologico = data.get('modoSemiologico', False)
    
    # Construção do Contexto da IA
    system_content = SYSTEM_PROMPT_BASE
    if modo_semiologico:
        system_content += "\n" + SYSTEM_PROMPT_SEMIOLOGIA

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_message}
    ]

    # Prevenção do Erro 402: Definindo um limite rígido de tokens para acomodar o saldo restrito
    payload = {
        "model": "qwen/qwen-2.5-coder-32b-instruct", # Ou o modelo recebido do front
        "messages": messages,
        "max_tokens": 1000  # <--- ESSA É A CORREÇÃO DO ERRO 402. Limita o gasto.
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        response_data = response.json()

        # Tratamento explícito para exibir erros da API (como o 402) se ainda ocorrerem
        if "error" in response_data:
            error_msg = response_data['error'].get('message', 'Erro desconhecido da API.')
            return jsonify({"error": error_msg}), 400

        reply = response_data['choices'][0]['message']['content']
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
