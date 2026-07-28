import os
import re
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuração do OpenRouter na Nuvem
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# Modelo padrão na nuvem via OpenRouter (ex: Qwen Coder ou outro de sua preferência)
CLOUD_MODEL = "qwen/qwen-2.5-7b-instruct"

# Variáveis do HD Local (LM Studio)
NGROK_URL = None
ACTIVE_LOCAL_MODEL = "local-model"

# Memória unificada e diretrizes de projeto
chat_history = []
system_prompt = """Você é a Athena, uma IA assistente avançada. 
Sua função é auxiliar em medicina, web design (foco em conversão) e desenvolvimento de apps.
Diretriz de Projeto: No app gamificado do usuário, a progressão oficial de níveis é estritamente: Inerte, Aspirante, Resiliente, Veterano, Elite. Use essa estrutura sempre que debater gamificação."""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global NGROK_URL, ACTIVE_LOCAL_MODEL, chat_history
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    target_mode = data.get('mode', 'cloud') # 'cloud' ou 'local'

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'})

    # Comando de sincronização do HD via Ngrok
    if user_message.startswith('/sync '):
        raw_url = user_message.split(' ', 1)[1].strip()
        url_match = re.search(r'https?://[^\s<>\]\)]+', raw_url)
        url = url_match.group(0) if url_match else raw_url
        NGROK_URL = url.rstrip('/')
        
        try:
            res = requests.get(f"{NGROK_URL}/v1/models", timeout=5)
            if res.status_code == 200 and res.json().get('data'):
                ACTIVE_LOCAL_MODEL = res.json()['data'][0].get('id', 'local-model')
        except Exception:
            pass
        return jsonify({'response': f"🦉 **Sincronização HD Concluída!**\nConectado em: `{NGROK_URL}`.\nModelo: `{ACTIVE_LOCAL_MODEL}`."})

    chat_history.append({"role": "user", "content": user_message})

    # ROTEAMENTO: NUVEM (VIA OPENROUTER)
    if target_mode == 'cloud':
        if not OPENROUTER_API_KEY:
            return jsonify({'response': "⚠️ Chave API do OpenRouter ausente no Render (Configure a Environment Variable: OPENROUTER_API_KEY)."})
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://athena-ia.onrender.com", 
            "X-Title": "Athena-IA"
        }
        payload = {
            "model": CLOUD_MODEL,
            "messages": [{"role": "system", "content": system_prompt}] + chat_history,
            "temperature": 0.7
        }
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            ai_reply = response.json()['choices'][0]['message']['content']
            chat_history.append({"role": "assistant", "content": ai_reply})
            return jsonify({'response': ai_reply})
        except Exception as e:
            return jsonify({'response': f"❌ Erro na Nuvem (OpenRouter): {str(e)}"})

    # ROTEAMENTO: HD LOCAL (LM STUDIO / QWEN)
    elif target_mode == 'local':
        if not NGROK_URL:
            return jsonify({'response': "⚠️ **HD Desconectado.** Envie o comando `/sync SEU_LINK_NGROK` primeiro."})
        
        payload = {
            "model": ACTIVE_LOCAL_MODEL,
            "messages": [{"role": "system", "content": system_prompt}] + chat_history,
            "temperature": 0.7
        }
        try:
            response = requests.post(f"{NGROK_URL}/v1/chat/completions", json=payload, timeout=120)
            response.raise_for_status()
            ai_reply = response.json()['choices'][0]['message']['content']
            chat_history.append({"role": "assistant", "content": ai_reply})
            return jsonify({'response': ai_reply})
        except Exception as e:
            return jsonify({'response': f"❌ Falha de conexão com o HD. Verifique se o LM Studio está rodando e o Ngrok ativo. Erro: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
