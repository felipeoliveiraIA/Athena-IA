import os
import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Puxa a chave oculta do Render
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
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
    base_prompt = """Você é ATHENA, uma IA assistente pessoal avançada e pragmática.
Áreas de expertise: Web Design focado em conversão e UX, e Desenvolvimento de Apps Gamificados.

DIRETRIZ DE PROGRESSÃO (APP DO USUÁRIO):
A hierarquia oficial de níveis é: 1. Inerte, 2. Aspirante, 3. Resiliente, 4. Veterano, 5. Elite.
Use formatação Markdown (negrito, listas) para deixar a leitura impecável."""

    medical_prompt = """\n\nDIRETRIZ CLÍNICA/SEMIOLÓGICA:
Estruture OBRIGATORIAMENTE respostas médicas na ordem:
1. Etiologia | 2. Fisiopatologia | 3. Critérios Diagnósticos | 4. Conduta.
Seja preciso e técnico."""

    return base_prompt + (medical_prompt if is_medical_mode else "")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    selected_model = data.get('model', 'google/gemini-2.0-flash-exp:free')
    is_medical_mode = data.get('medical_mode', False)

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'}), 400

    chat_history = carregar_memoria()
    chat_history.append({"role": "user", "content": user_message})
    
    current_prompt = get_system_prompt(is_medical_mode)
    messages_payload = [{"role": "system", "content": current_prompt}] + chat_history

    # LÓGICA 100% LOCAL (LM Studio sem Ngrok)
    if selected_model == 'local-hd':
        try:
            # Aponta diretamente para o seu PC (porta 1234 do LM Studio)
            response = requests.post("http://127.0.0.1:1234/v1/chat/completions", 
                                     json={"model": "local-model", "messages": messages_payload, "temperature": 0.7}, 
                                     timeout=120)
            response.raise_for_status()
            ai_reply = response.json()['choices'][0]['message']['content']
        except Exception as e:
            return jsonify({'error': f"Erro no HD Local: Verifique se o LM Studio está ligado na porta 1234. Detalhe: {str(e)}"}), 500

    # LÓGICA NUVEM (OpenRouter)
    else:
        if not OPENROUTER_API_KEY:
            return jsonify({'error': "Chave OPENROUTER_API_KEY não encontrada no Render."}), 500
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, 
                                     json={"model": selected_model, "messages": messages_payload, "temperature": 0.7}, 
                                     timeout=60)
            response.raise_for_status()
            ai_reply = response.json()['choices'][0]['message']['content']
        except Exception as e:
            return jsonify({'error': f"Erro na Nuvem ({response.status_code}): Tente outro modelo ou verifique a API. Detalhe: {str(e)}"}), 500

    chat_history.append({"role": "assistant", "content": ai_reply})
    salvar_memoria(chat_history)
    
    return jsonify({'response': ai_reply})

if __name__ == '__main__':
    # Roda em todas as interfaces para funcionar no Render e Local
    app.run(host='0.0.0.0', port=10000)
