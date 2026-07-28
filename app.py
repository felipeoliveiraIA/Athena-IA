import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# Inicializa o cliente autônomo da nuvem usando a chave de API segura do Render
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'})

    try:
        # Processamento inteligente e autônomo direto na nuvem
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
        )
        
        ai_reply = response.text
        return jsonify({'response': ai_reply})

    except Exception as e:
        return jsonify({
            'response': f"❌ **Erro no núcleo autônomo da nuvem:** {str(e)}\n\n*Nota técnica: Certifique-se de que a variável de ambiente `GEMINI_API_KEY` foi configurada corretamente no painel do Render.*"
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
