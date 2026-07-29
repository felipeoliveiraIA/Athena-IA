import os
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Chave API configurada no ambiente do Render ou terminal
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

SYSTEM_PROMPT_BASE = """
Você é a A.T.H.E.N.A. OS (v5.2 Prime), uma inteligência artificial de alta performance para arquitetura de software, vibe-coding, semiologia médica e investimentos.

### DIRETRIZES DE MEMÓRIA E PERSONALIZAÇÃO DO USUÁRIO:
Abaixo estão as informações permanentes sobre quem é o usuário, sua mentalidade, forma de pensar e preferências em projetos.
USE ESSAS INFORMAÇÕES para personalizar cada resposta, adotando o tom, nível técnico e estilo ideais para ele:
{user_profile}

### DIRETRIZES DE COMPORTAMENTO:
- Seja direta, pragmática, analítica e elegante.
- Se o usuário pedir para "repetir a última resposta em voz alta", confirme brevemente e repita o ponto fundamental.
- Mantenha precisão técnica absoluta em programação e medicina.
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    model_choice = data.get('model', 'qwen')
    user_profile = data.get('userProfile', 'Nenhuma informação de perfil cadastrada ainda.')
    history = data.get('history', [])

    # Montagem do prompt do sistema com a Memória Aditiva do Usuário
    system_content = SYSTEM_PROMPT_BASE.format(user_profile=user_profile)

    # Constrói o array de mensagens respeitando o histórico recente
    messages = [{"role": "system", "content": system_content}]
    for msg in history[-10:]:  # Mantém as últimas 10 interações como contexto
        messages.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })
    messages.append({"role": "user", "content": user_message})

    # 1. ROTEAMENTO PARA HD LOCAL (LM Studio)
    if model_choice == 'local':
        try:
            response = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={"model": "local-model", "messages": messages, "temperature": 0.7, "max_tokens": 1500},
                timeout=30
            )
            return jsonify({"reply": response.json()['choices'][0]['message']['content']})
        except Exception:
            return jsonify({"error": "Falha ao conectar com o HD Local (LM Studio). Verifique se o servidor na porta 1234 está ativo."}), 500

    # 2. ROTEAMENTO NUVEM (OpenRouter com Modelos Gratuitos/Ilimitados)
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "Chave API não detectada. Configure a variável 'OPENROUTER_API_KEY' no Render."}), 500

    # Mapeamento para modelos 100% gratuitos e modernos no OpenRouter
    model_id_map = {
        "qwen": "qwen/qwen-2.5-coder-32b-instruct:free",
        "gemini": "google/gemini-2.0-flash-lite-preview-02-05:free"
    }
    selected_model = model_id_map.get(model_choice, "qwen/qwen-2.5-coder-32b-instruct:free")

    payload = {
        "model": selected_model,
        "messages": messages,
        "max_tokens": 1500,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://athena-os.local",
        "X-Title": "ATHENA OS v5.2"
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        response_data = response.json()

        if "error" in response_data:
            error_code = response_data['error'].get('code', 'Desconhecido')
            error_msg = response_data['error'].get('message', 'Erro sem descrição')
            if error_code == 402:
                return jsonify({"error": "Erro 402: Limite pago atingido. Tente novamente, pois o modelo foi ajustado para a rota gratuita (:free)."}), 402
            return jsonify({"error": f"Erro API OpenRouter ({error_code}): {error_msg}"}), 400

        reply_text = response_data['choices'][0]['message']['content']
        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"error": f"Falha interna ao contatar o servidor OpenRouter: {str(e)}"}), 500


@app.route('/api/learn', methods=['POST'])
def learn_profile():
    """Endpoint para IA avaliar a conversa e gerar aditivamente novos dados sobre o usuário."""
    data = request.json
    current_profile = data.get('currentProfile', '')
    last_messages = data.get('messages', [])
    model_choice = data.get('model', 'qwen')

    if not OPENROUTER_API_KEY and model_choice != 'local':
        return jsonify({"error": "Chave API ausente."}), 500

    prompt_learn = f"""
    Avalie o texto atual de perfil do usuário e as últimas mensagens desta conversa.
    Seu objetivo é EXCLUSIVAMENTE extrair NOVOS APRENDIZADOS sobre o estilo, gostos, mentalidade, psicologia ou preferências técnicas do usuário que ainda NÃO estejam escritos.
    
    Perfil Atual do Usuário:
    {current_profile}
    
    Gere APENAS um parágrafo curto ou bullet points com os NOVOS TRAÇOS descobertos para serem ADICIONADOS ao perfil. Não repita o que já está escrito.
    """

    messages = [
        {"role": "system", "content": "Você é um analisador comportamental aditivo. Responda apenas com os novos dados a serem acrescentados."},
        {"role": "user", "content": prompt_learn}
    ]

    try:
        model_id = "qwen/qwen-2.5-coder-32b-instruct:free" if model_choice == 'qwen' else "google/gemini-2.0-flash-lite-preview-02-05:free"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": model_id, "messages": messages, "max_tokens": 400}, timeout=40)
        new_insights = res.json()['choices'][0]['message']['content']
        return jsonify({"new_insights": new_insights.strip()})
    except Exception as e:
        return jsonify({"error": "Não foi possível extrair novos aprendizados no momento."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
