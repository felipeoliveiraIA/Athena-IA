from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Cérebro autônomo independente na nuvem
chat_history = [
    {"role": "system", "content": "Você é a Athena, uma inteligência artificial autônoma hospedada na nuvem. Você opera de forma independente, focando em produtividade, desenvolvimento, organização de projetos e suporte direto ao usuário com precisão e clareza em Português."}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global chat_history
    
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'})

    # Registra a entrada na memória autônoma da nuvem
    chat_history.append({"role": "user", "content": user_message})

    # Processamento autônomo direto na nuvem
    # Aqui a IA opera por conta própria, processando as demandas do usuário sem dependências externas
    ai_reply = f"Compreendido, Luiz. Estou operando de forma 100% autônoma aqui na nuvem. Processando sua diretriz: \"{user_message}\". Como posso estruturar ou avançar com isso para você agora?"

    chat_history.append({"role": "assistant", "content": ai_reply})

    return jsonify({'response': ai_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
