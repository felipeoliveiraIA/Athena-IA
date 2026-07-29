import os
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Pega a chave da nuvem (Render) invisivelmente. Se não achar, não quebra, mas avisa no erro.
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# ==========================================
# DIRETRIZES DE SISTEMA (MEMÓRIA & REGRAS)
# ==========================================
SYSTEM_PROMPT_BASE = """
Você é a A.T.H.E.N.A. OS.
Diretriz de Memória Aditiva: Você opera acumulando contexto. Jamais descarte preferências antigas do usuário.
Diretriz de Gamificação OBRIGATÓRIA: O ecossistema opera sob uma hierarquia rígida de 5 níveis de progresso, sendo eles (em ordem):
1. Inerte
2. Aspirante
3. Resiliente
4. Veterano
5. Elite
Reflita essa terminologia de gamificação quando apropriado na conversa.
"""

SYSTEM_PROMPT_SEMIOLOGIA = """
[MODO SEMIOLÓGICO ATIVADO]
Você deve estruturar a resposta médica OBRIGATORIAMENTE nesta exata hierarquia e formatação Markdown:
### 1. Etiologia
[Descreva a causa]
### 2. Fisiopatologia
[Descreva o mecanismo]
### 3. Critérios Diagnósticos
[Liste sinais, sintomas e exames]
### 4. Conduta
[Protocolo terapêutico]
"""

@app.route('/')
def home():
    # Renderiza o index.html que está na pasta templates
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    # Verifica se a chave foi configurada no Render
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "Chave API (OPENROUTER_API_KEY) não encontrada nas variáveis de ambiente do Render. Configure-a na aba Environment."}), 500

    data = request.json
    user_message = data.get('message', '')
    image_base64 = data.get('image', None) # Preparado para a Sugestão 1 (Visão)
    modo_semiologico = data.get('modoSemiologico', False)
    
    # Constrói a mentalidade da IA para esta requisição
    system_content = SYSTEM_PROMPT_BASE
    if modo_semiologico:
        system_content += "\n" + SYSTEM_PROMPT_SEMIOLOGIA

    # Estrutura de mensagens
    messages = [
        {"role": "system", "content": system_content}
    ]

    # Se tiver imagem (Base do aprimoramento Multimodal), ajusta o payload
    if image_base64:
        messages.append({
            "role": "user", 
            "content": [
                {"type": "text", "text": user_message if user_message else "Analise esta imagem."},
                {"type": "image_url", "image_url": {"url": image_base64}}
            ]
        })
    else:
        messages.append({"role": "user", "content": user_message})

    # Prevenção do Erro 402: max_tokens travado em 1000 para não estourar os créditos do usuário
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
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        response_data = response.json()

        # Tratamento do erro 402 explícito para aparecer no Front-end de forma legível
        if "error" in response_data:
            error_code = response_data['error'].get('code', 'Desconhecido')
            error_msg = response_data['error'].get('message', 'Erro da API do OpenRouter')
            if error_code == 402:
                return jsonify({"error": f"Erro 402: Créditos insuficientes. A requisição foi limitada, mas seus fundos no OpenRouter acabaram. Recarregue sua conta."}), 402
            return jsonify({"error": f"Erro API ({error_code}): {error_msg}"}), 400

        reply = response_data['choices'][0]['message']['content']
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": f"Falha de conexão com o servidor: {str(e)}"}), 500

if __name__ == '__main__':
    # Necessário para deploy no Render: bind na porta 0.0.0.0
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
