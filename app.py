import os
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# --- INÍCIO DA SOLUÇÃO DEFINITIVA (Caminhos Absolutos) ---
# Calcula o caminho real do arquivo atual para não depender do terminal
diretorio_base = os.path.dirname(os.path.abspath(__file__))
# Força o Flask a olhar estritamente para a pasta 'templates' dentro deste diretório
pasta_templates = os.path.join(diretorio_base, 'templates')

app = Flask(__name__, template_folder=pasta_templates)
# --- FIM DA SOLUÇÃO DEFINITIVA ---
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
    images = data.get('images', []) 
    selected_model = data.get('model', 'google/gemini-2.0-flash-exp:free')
    system_prompt = data.get('system_prompt', 'Você é a ATHENA IA. Responda em Markdown limpo.')

    if not user_message and not images:
        return jsonify({'error': 'Mensagem vazia.'}), 400

    try:
        # Montagem Estrutural Multimodal Exigida pelo OpenRouter
        message_content = []
        if user_message:
            message_content.append({"type": "text", "text": user_message})
        
        for img_base64 in images:
            message_content.append({"type": "image_url", "image_url": {"url": img_base64}})
            
        final_content = message_content if images else user_message

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
                    {"role": "user", "content": final_content}
                ],
                "max_tokens": 2000,
                "stream": True # Ativa o Streaming no OpenRouter
            }

            def generate():
                nonlocal selected_model 
                
                fallback_models = [
                    selected_model,
                    'qwen/qwen-2.5-coder-32b-instruct:free',
                    'meta-llama/llama-3.3-70b-instruct:free',
                    'google/gemini-2.0-pro-exp-02-05:free'
                ]
                
                for model_to_try in fallback_models:
                    if not model_to_try:
                        continue
                    payload["model"] = model_to_try
                    try:
                        resp = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers=headers,
                            json=payload,
                            stream=True,
                            timeout=30
                        )
                        if resp.status_code == 200:
                            for line in resp.iter_lines():
                                if line:
                                    decoded = line.decode('utf-8')
                                    if decoded.startswith('data: '):
                                        data_sub = decoded[6:].strip()
                                        if data_sub == '[DONE]':
                                            break
                                        try:
                                            json_data = json.loads(data_sub)
                                            delta = json_data['choices'][0]['delta'].get('content', '')
                                            if delta:
                                                yield delta
                                        except:
                                            pass
                            return
                        elif resp.status_code == 402:
                            yield f"\n\n**Erro 402:** Saldo esgotado no modelo {model_to_try}. Tentando fallback..."
                            continue
                        else:
                            yield f"\n\n**Erro {resp.status_code} no OpenRouter ({model_to_try}).** Tentando fallback..."
                            continue
                    except Exception as e:
                        continue
                yield "\n\n**Erro Crítico:** Todos os modelos de nuvem falharam."
            
            # --- CORREÇÃO ATHENA: ESSA LINHA FALTAVA! ELA DEVOLVE O TEXTO PARA A TELA ---
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
