import os
import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
# Força a leitura correta de acentos
app.config['JSON_AS_ASCII'] = False

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
    base_prompt = """Você é ATHENA, IA avançada.
DIRETRIZ DE PROGRESSÃO (APP): Hierarquia oficial: 1. Inerte, 2. Aspirante, 3. Resiliente, 4. Veterano, 5. Elite.
Use Markdown para deixar as listas, tabelas e negritos perfeitos."""
    
    medical_prompt = """\nDIRETRIZ SEMIOLÓGICA:
Estruture na ordem: 1. Etiologia | 2. Fisiopatologia | 3. Critérios Diagnósticos | 4. Conduta."""

    return base_prompt + (medical_prompt if is_medical_mode else "")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    image_base64 = data.get('image', None)
    selected_model = data.get('model', 'google/gemini-2.0-flash-exp:free')
    is_medical_mode = data.get('medical_mode', False)

    if not user_message and not image_base64:
        return jsonify({'error': 'Mensagem vazia.'}), 400

    chat_history = carregar_memoria()

    # Formata a mensagem atual (com ou sem imagem)
    if image_base64:
        msg_content = [
            {"type": "text", "text": user_message if user_message else "Analise esta imagem:"},
            {"type": "image_url", "image_url": {"url": image_base64}}
        ]
    else:
        msg_content = user_message

    chat_history.append({"role": "user", "content": msg_content})
    
    # Limpa imagens antigas do histórico para não sobrecarregar a memória da API
    clean_history = []
    for msg in chat_history[-10:]: # Lembra apenas das últimas 10 interações
        if isinstance(msg["content"], list):
            clean_history.append({"role": msg["role"], "content": msg["content"][0]["text"]})
        else:
            clean_history.append(msg)
            
    # Restaura a imagem apenas na mensagem atual
    if image_base64:
        clean_history[-1] = {"role": "user", "content": msg_content}

    messages_payload = [{"role": "system", "content": get_system_prompt(is_medical_mode)}] + clean_history

    try:
        if selected_model == 'local-hd':
            # Comunicação Local (LM Studio)
            resp = requests.post("http://127.0.0.1:1234/v1/chat/completions", 
                                 json={"model": "local-model", "messages": messages_payload, "temperature": 0.7}, 
                                 timeout=120)
        else:
            # Comunicação Nuvem (OpenRouter)
            if not OPENROUTER_API_KEY:
                return jsonify({'error': "Chave da API ausente. Configure OPENROUTER_API_KEY."}), 500
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
            resp = requests.post(OPENROUTER_URL, headers=headers, 
                                 json={"model": selected_model, "messages": messages_payload, "temperature": 0.7}, 
                                 timeout=60)
            
        if resp.status_code != 200:
            return jsonify({'error': f"Erro da API ({resp.status_code}): {resp.text}"}), 500
            
        ai_reply = resp.json()['choices'][0]['message']['content']
        
    except Exception as e:
        chat_history.pop() # Evita salvar mensagem com erro
        return jsonify({'error': f"Falha de conexão: {str(e)}"}), 500

    # Salva no histórico local removendo a imagem gigante para evitar lags
    chat_history[-1] = {"role": "user", "content": user_message or "[Imagem Analisada]"}
    chat_history.append({"role": "assistant", "content": ai_reply})
    salvar_memoria(chat_history)
    
    return jsonify({'response': ai_reply})

if __name__ == '__main__':
    # PORTA 7860 travada para combinar com o seu terminal
    app.run(host='0.0.0.0', port=7860, debug=True)
