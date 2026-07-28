import os
import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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
    base_prompt = """Você é ATHENA, uma IA assistente pessoal avançada.
Áreas de expertise: Web Design focado em conversão, automação e Desenvolvimento de Apps Gamificados.
DIRETRIZ DE PROGRESSÃO (APP): A hierarquia oficial de níveis é: 1. Inerte, 2. Aspirante, 3. Resiliente, 4. Veterano, 5. Elite.
Use formatação Markdown (negrito, listas) para estruturar suas respostas."""

    medical_prompt = """\n\nDIRETRIZ CLÍNICA/SEMIOLÓGICA:
Estruture respostas médicas na ordem: 1. Etiologia | 2. Fisiopatologia | 3. Critérios Diagnósticos | 4. Conduta."""

    return base_prompt + (medical_prompt if is_medical_mode else "")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    image_base64 = data.get('image', None) # Recebe a imagem se houver
    selected_model = data.get('model', 'google/gemini-2.0-flash-exp:free')
    is_medical_mode = data.get('medical_mode', False)

    if not user_message and not image_base64:
        return jsonify({'error': 'Mensagem e/ou imagem vazia.'}), 400

    chat_history = carregar_memoria()
    
    # Prepara o conteúdo (Texto puro ou Texto + Imagem)
    if image_base64:
        msg_content = [
            {"type": "text", "text": user_message if user_message else "Analise esta imagem."},
            {"type": "image_url", "image_url": {"url": image_base64}}
        ]
    else:
        msg_content = user_message

    chat_history.append({"role": "user", "content": msg_content})
    
    # Monta o payload final
    current_prompt = get_system_prompt(is_medical_mode)
    messages_payload = [{"role": "system", "content": current_prompt}] + chat_history

    try:
        if selected_model == 'local-hd':
            # Roteamento Local (LM Studio na porta 1234)
            response = requests.post("http://127.0.0.1:1234/v1/chat/completions", 
                                     json={"model": "local-model", "messages": messages_payload, "temperature": 0.7}, 
                                     timeout=120)
        else:
            # Roteamento Nuvem (OpenRouter)
            if not OPENROUTER_API_KEY:
                return jsonify({'error': "Chave da API não configurada no servidor."}), 500
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
            response = requests.post(OPENROUTER_URL, headers=headers, 
                                     json={"model": selected_model, "messages": messages_payload, "temperature": 0.7}, 
                                     timeout=60)
            
        response.raise_for_status()
        ai_reply = response.json()['choices'][0]['message']['content']
        
    except Exception as e:
        chat_history.pop() # Remove a mensagem se falhou para não corromper o histórico
        return jsonify({'error': f"Falha de conexão: {str(e)}"}), 500

    # Salva apenas o texto da IA e do usuário (evita salvar a imagem gigante no histórico JSON)
    hist_to_save = chat_history[:-1] + [{"role": "user", "content": user_message or "[Imagem enviada]"}, {"role": "assistant", "content": ai_reply}]
    salvar_memoria(hist_to_save)
    
    return jsonify({'response': ai_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
