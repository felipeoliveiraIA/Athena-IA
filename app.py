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

import json
from flask import Response

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    selected_model = data.get('model', 'qwen/qwen-2.5-coder-32b-instruct:free') 
    system_prompt = data.get('system_prompt', 'Você é a ATHENA IA. Responda em Markdown limpo.')

    if not user_message:
        return jsonify({'error': 'Mensagem vazia.'}), 400

    try:
        if selected_model != 'local':
            if not OPENROUTER_API_KEY:
                return jsonify({'error': 'Chave da API OpenRouter não configurada.'}), 500
            
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
                "max_tokens": 2000,
                "stream": True # Ativa o Streaming no OpenRouter
            }

            def generate():
                try:
                    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, stream=True, timeout=40)
                    
                    # NOVA LÓGICA: Se a API recusar, mostre o erro real em Markdown em vez de quebrar
                    if not response.ok:
                        error_text = response.text
                        yield f"\n\n**Erro detalhado da API OpenRouter ({response.status_code}):**\n```json\n{error_text}\n```\n*Diagnóstico da ATHENA: Se for 404, o ID do modelo selecionado foi descontinuado ou alterado na versão Free do OpenRouter. Atualize o value no HTML.*"
                        return

                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith('data: '):
                                data_str = decoded_line[6:]
                                if data_str == '[DONE]':
                                    break
                                try:
                                    data_json = json.loads(data_str)
                                    chunk = data_json['choices'][0]['delta'].get('content', '')
                                    if chunk:
                                        yield chunk
                                except json.JSONDecodeError:
                                    continue
                except Exception as e:
                    yield f"\n\n**Erro de Conexão (Streaming):** {str(e)}"

            return Response(generate(), mimetype='text/event-stream')

        elif selected_model == 'local':
            # LM Studio também suporta streaming
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": True
            }
            
            def generate_local():
                try:
                    response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json=payload, stream=True, timeout=30)
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith('data: '):
                                data_str = decoded_line[6:]
                                if data_str == '[DONE]':
                                    break
                                try:
                                    data_json = json.loads(data_str)
                                    chunk = data_json['choices'][0]['delta'].get('content', '')
                                    if chunk:
                                        yield chunk
                                except json.JSONDecodeError:
                                    continue
                except Exception as e:
                    yield f"\n\n**Erro HD Local:** Verifique se o LM Studio está rodando. {str(e)}"
                    
            return Response(generate_local(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
