import os
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Busca a chave de forma segura nas variáveis de ambiente do Render
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
# Configuração da URL de Origem para liberação de uso na API gratuita
SITE_URL = os.environ.get("SITE_URL", "https://athena-ia.onrender.com")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    selected_model = data.get('model', 'qwen/qwen-2.5-coder-32b-instruct:free') 
    system_prompt = data.get('system_prompt', 'Você é a ATHENA IA. Responda em Markdown limpo.')

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'}), 400

    try:
        # Se o modelo NÃO for o local, aciona a nuvem do OpenRouter
        if selected_model != 'local':
            if not OPENROUTER_API_KEY:
                return jsonify({'error': 'Chave da API OpenRouter não configurada no servidor.'}), 500
            
            # Cabeçalhos obrigatórios inseridos para evitar bloqueios silenciosos do OpenRouter
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": SITE_URL,
                "X-Title": "ATHENA IA v5.2 OS"
            }
            
            payload = {
                "model": selected_model, 
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 2000
            }
            
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            
            # LÓGICA DE AUTO-RETRY: Se o modelo :free não existir mais (Erro 404), tenta o modelo normal silenciosamente
            if response.status_code == 404 and ':free' in selected_model:
                fallback_model = selected_model.replace(':free', '')
                payload['model'] = fallback_model
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

            # Bloco cirúrgico de tratamento de erros
            if not response.ok:
                if response.status_code == 402:
                    return jsonify({'error': 'Erro 402: Limite de uso gratuito atingido ou modelo pago. Tente usar outro modelo Free da lista.'}), 402
                
                try:
                    # Captura o motivo real da falha
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', f'Status {response.status_code}')
                    return jsonify({'error': f'Recusa do OpenRouter (Erro {response.status_code}): {error_msg}. Tente um modelo Estável.'}), response.status_code
                except Exception:
                    return jsonify({'error': f'Falha externa de API HTTP {response.status_code}.'}), response.status_code
            
            ai_reply = response.json()['choices'][0]['message']['content']
            return jsonify({'reply': ai_reply})

        # Se for HD Local, roda no LM Studio
        elif selected_model == 'local':
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json=payload, timeout=30)
            response.raise_for_status()
            ai_reply = response.json()['choices'][0]['message']['content']
            return jsonify({'reply': ai_reply})

    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Falha de Conexão. Verifique a rede ou certifique-se de que o LM Studio está rodando localmente na porta 1234.'}), 503
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor ATHENA: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
