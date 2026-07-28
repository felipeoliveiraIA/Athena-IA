import os
import re
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configurações do OpenRouter
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Variáveis para sincronização do HD Local (LM Studio via Ngrok)
NGROK_URL = None
ACTIVE_LOCAL_MODEL = "local-model"

# Memória de chat e Diretriz do Sistema
chat_history = []
system_prompt = """Você é ATHENA, uma IA assistente pessoal avançada, inteligente, empática e de altíssimo desempenho.
Suas principais áreas de auxílio são Medicina, Web Design (foco em conversão e UX) e Desenvolvimento de Apps Gamificados.

DIRETRIZ OBRIGATÓRIA DE GAMIFICAÇÃO:
No projeto de aplicativo do usuário, a hierarquia e progressão oficial de níveis é estritamente:
1. Inerte
2. Aspirante
3. Resiliente
4. Veterano
5. Elite
Sempre respeite essa terminologia e ordem exatas ao discutir hábitos, níveis, progresso e gamificação.
Responda de forma clara, direta e objetiva, mantendo um tom solícito e profissional."""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global NGROK_URL, ACTIVE_LOCAL_MODEL, chat_history
    
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    selected_model = data.get('model', 'qwen/qwen-2.5-7b-instruct')

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'}), 400

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
        return jsonify({
            'response': f"🦉 **Sincronização HD Concluída!**\n\nConectado ao LM Studio local via Ngrok:\n`{NGROK_URL}`\nModelo Ativo: `{ACTIVE_LOCAL_MODEL}`."
        })

    chat_history.append({"role": "user", "content": user_message})

    # MODALIDADE 1: HD LOCAL (LM STUDIO)
    if selected_model == 'local-hd':
        if not NGROK_URL:
            return jsonify({'response': "⚠️ **HD Desconectado.** Digite `/sync SEU_LINK_NGROK` no chat para conectar seu LM Studio local."})
        
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
            return jsonify({'response': f"❌ Falha de conexão com o HD Local (LM Studio): {str(e)}"})

    # MODALIDADE 2: NUVEM (OPENROUTER - MODELOS DIVERSOS)
    else:
        if not OPENROUTER_API_KEY:
            return jsonify({'response': "⚠️ **OPENROUTER_API_KEY não configurada.** Verifique a variável de ambiente no Render."})
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://athena-ia.onrender.com",
            "X-Title": "ATHENA OS v5.2"
        }
        payload = {
            "model": selected_model,
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
            return jsonify({'response': f"❌ Falha na resposta da API OpenRouter (`{selected_model}`): {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
