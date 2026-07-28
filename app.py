import os
import re
import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

NGROK_URL = None
ACTIVE_LOCAL_MODEL = "local-model"
MEMORY_FILE = "athena_memory.json"

def carregar_memoria():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salvar_memoria(hist):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

def get_system_prompt(is_medical_mode=False):
    base_prompt = """Você é ATHENA, uma IA assistente pessoal avançada, inteligente e empática.
Áreas de expertise: Web Design focado em conversão e UX, e Desenvolvimento de Apps Gamificados.

DIRETRIZ DE GAMIFICAÇÃO (APP DO USUÁRIO):
A hierarquia e progressão oficial de níveis é estritamente: 1. Inerte, 2. Aspirante, 3. Resiliente, 4. Veterano, 5. Elite.
Jamais altere essa ordem ou nomenclatura. Responda com clareza, formatação impecável em Markdown e proatividade."""

    medical_prompt = """\n\nDIRETRIZ DE MODO CLÍNICO E SEMIOLÓGICO ATIVADA:
O usuário solicitou análise de um caso ou tema médico. Estruture OBRIGATORIAMENTE sua resposta na seguinte ordem lógica:
1. Etiologia
2. Fisiopatologia
3. Critérios de Diferenciação Diagnóstica
4. Conduta / Manobras
Seja preciso, técnico e focado em raciocínio clínico de alto nível."""

    return base_prompt + (medical_prompt if is_medical_mode else "")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global NGROK_URL, ACTIVE_LOCAL_MODEL
    
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    selected_model = data.get('model', 'qwen/qwen-2.5-coder-32b-instruct')
    is_medical_mode = data.get('medical_mode', False)

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'}), 400

    if user_message.startswith('/sync '):
        raw_url = user_message.split(' ', 1)[1].strip()
        url_match = re.search(r'https?://[^\s<>\]\)]+', raw_url)
        url = url_match.group(0) if url_match else raw_url
        NGROK_URL = url.rstrip('/')
        return jsonify({'response': f"🦉 **Sincronização HD Concluída!**\nConectado via Ngrok: `{NGROK_URL}`. Memória sincronizada."})

    chat_history = carregar_memoria()
    chat_history.append({"role": "user", "content": user_message})
    current_prompt = get_system_prompt(is_medical_mode)

    if selected_model == 'local-hd':
        if not NGROK_URL:
            return jsonify({'response': "⚠️ **HD Desconectado.** Digite `/sync SEU_LINK_NGROK`."})
        payload = {
            "model": ACTIVE_LOCAL_MODEL,
            "messages": [{"role": "system", "content": current_prompt}] + chat_history,
            "temperature": 0.7
        }
        try:
            response = requests.post(f"{NGROK_URL}/v1/chat/completions", json=payload, timeout=120)
            response.raise_for_status()
            ai_reply = response.json()['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as errh:
            return jsonify({'response': f"❌ **Erro de Conexão (HD Local):** Verifique se o Ngrok foi iniciado com `ngrok http 1234` e se o Servidor do LM Studio está ligado. Detalhe técnico: {errh}"})
        except Exception as e:
            return jsonify({'response': f"❌ Erro HD Local: {str(e)}"})
    else:
        if not OPENROUTER_API_KEY:
            return jsonify({'response': "⚠️ **OPENROUTER_API_KEY ausente.**"})
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://athena-ia.onrender.com",
            "X-Title": "ATHENA OS v5.2"
        }
        payload = {
            "model": selected_model,
            "messages": [{"role": "system", "content": current_prompt}] + chat_history,
            "temperature": 0.7
        }
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            ai_reply = response.json()['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as errh:
            if response.status_code == 402:
                return jsonify({'response': "❌ **Erro Nuvem (402):** Saldo insuficiente no OpenRouter. Adicione créditos ou troque para um modelo gratuito na plataforma."})
            return jsonify({'response': f"❌ Erro HTTP (Nuvem): {errh}"})
        except Exception as e:
            return jsonify({'response': f"❌ Erro Nuvem OpenRouter: {str(e)}"})

    chat_history.append({"role": "assistant", "content": ai_reply})
    salvar_memoria(chat_history)
    
    return jsonify({'response': ai_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
