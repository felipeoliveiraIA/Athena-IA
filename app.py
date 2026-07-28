from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__)

# Memória global da IA
NGROK_URL = None
chat_history = [
    {"role": "system", "content": "Você é a Athena, uma inteligência artificial brilhante, prestativa e objetiva. Você roda localmente no HD do usuário. Responda sempre em Português com clareza."}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global NGROK_URL, chat_history
    
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'})

    # Intercepta o comando de sincronização do Ngrok com limpeza automática de URL
    if user_message.startswith('/sync '):
        raw_url = user_message.split(' ', 1)[1].strip()
        
        # Extrai apenas o endereço HTTP/HTTPS válido usando Regex (remove colchetes, parênteses e lixo)
        url_match = re.search(r'https?://[^\s<>\]\)]+', raw_url)
        if url_match:
            url = url_match.group(0)
        else:
            url = raw_url
            
        if url.endswith('/'): 
            url = url[:-1]
            
        NGROK_URL = url
        return jsonify({'response': f"✅ **Sincronização Concluída!**\n\nConexão estabelecida com o HD em: `{NGROK_URL}`.\nComo posso te ajudar agora, Luiz?"})

    # Trava de segurança se não houver link
    if not NGROK_URL:
        return jsonify({'response': "⚠️ **Atenção:** Eu ainda estou desconectada do seu HD. Por favor, envie o comando `/sync SEU_LINK_NGROK` para estabelecermos a ponte."})

    # Adiciona a mensagem do usuário na memória
    chat_history.append({"role": "user", "content": user_message})

    # Prepara o pacote para enviar ao LM Studio
    payload = {
        "model": "local-model",
        "messages": chat_history,
        "temperature": 0.7
    }

    try:
        # Dispara para o LM Studio através do Ngrok
        response = requests.post(f"{NGROK_URL}/v1/chat/completions", json=payload, timeout=120)
        response.raise_for_status()
        
        # Extrai a resposta da IA
        ai_reply = response.json()['choices'][0]['message']['content']
        
        # Salva a resposta na memória
        chat_history.append({"role": "assistant", "content": ai_reply})
        
        return jsonify({'response': ai_reply})

    except requests.exceptions.RequestException as e:
        chat_history.pop()
        return jsonify({'response': f"❌ **Falha na conexão com o Qwen2.5.**\n\nVerifique se a tela preta do Ngrok está aberta e se o Local API do LM Studio está 'Running'.\n\n*Detalhe técnico: {str(e)}*"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
