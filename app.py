from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__)

NGROK_URL = None
ACTIVE_MODEL = "local-model"
chat_history = [
    {"role": "system", "content": "Você é a Athena, uma inteligência artificial brilhante, prestativa e objetiva. Você roda localmente no HD do usuário. Responda sempre em Português com clareza."}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global NGROK_URL, ACTIVE_MODEL, chat_history
    
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'})

    # Sincronização com limpeza de URL e detecção automática do modelo do LM Studio
    if user_message.startswith('/sync '):
        raw_url = user_message.split(' ', 1)[1].strip()
        url_match = re.search(r'https?://[^\s<>\]\)]+', raw_url)
        url = url_match.group(0) if url_match else raw_url
        if url.endswith('/'): 
            url = url[:-1]
            
        NGROK_URL = url
        
        # Tenta descobrir automaticamente qual modelo está carregado no LM Studio
        try:
            models_res = requests.get(f"{NGROK_URL}/v1/models", timeout=5)
            if models_res.status_code == 200:
                models_data = models_res.json().get('data', [])
                if models_data and len(models_data) > 0:
                    ACTIVE_MODEL = models_data[0].get('id', 'local-model')
        except Exception:
            pass

        return jsonify({'response': f"✅ **Sincronização Concluída!**\n\nConexão estabelecida com o HD em: `{NGROK_URL}`.\nModelo detectado: `{ACTIVE_MODEL}`.\nComo posso te ajudar agora, Luiz?"})

    if not NGROK_URL:
        return jsonify({'response': "⚠️ **Atenção:** Eu ainda estou desconectada do seu HD. Por favor, envie o comando `/sync SEU_LINK_NGROK`."})

    chat_history.append({"role": "user", "content": user_message})

    payload = {
        "model": ACTIVE_MODEL,
        "messages": chat_history,
        "temperature": 0.7
    }

    try:
        response = requests.post(f"{NGROK_URL}/v1/chat/completions", json=payload, timeout=120)
        response.raise_for_status()
        
        ai_reply = response.json()['choices'][0]['message']['content']
        chat_history.append({"role": "assistant", "content": ai_reply})
        
        return jsonify({'response': ai_reply})

    except requests.exceptions.RequestException as e:
        chat_history.pop()
        error_details = f" - Resposta do servidor: {e.response.text}" if e.response is not None else ""
        return jsonify({'response': f"❌ **Falha na comunicação com o Qwen2.5.**\n\nO LM Studio recusou o pedido (Erro 400). Verifique se há um modelo carregado e rodando (Start Model) no LM Studio do seu PC.\n\n*Detalhe técnico: {str(e)}{error_details}*"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
