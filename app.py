import os
import requests
import json
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS

# --- INÍCIO DA SOLUÇÃO DEFINITIVA (Caminhos Absolutos) ---
diretorio_base = os.path.dirname(os.path.abspath(__file__))
pasta_templates = os.path.join(diretorio_base, 'templates')

app = Flask(__name__, template_folder=pasta_templates)
# --- FIM DA SOLUÇÃO DEFINITIVA ---

# [CORREÇÃO CRÍTICA]: O CORS precisa permitir requisições globais e especificar a porta
CORS(app, resources={r"/*": {"origins": ["https://athena-ia.onrender.com", "http://localhost:10000", "*"]}})

# Busca a chave de forma segura nas variáveis de ambiente do Render
OMNIROUTER_API_KEY = os.environ.get("OMNIROUTER_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Define o Gateway. Se você configurar a variável GATEWAY_URL no Render, ele usa. 
# Senão, cai no padrão OpenRouter.
GATEWAY_URL = os.environ.get("GATEWAY_URL", "https://omnirouter-gateway-uh97.onrender.com/v1/chat/completions")

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
            if not OMNIROUTER_API_KEY:
                return jsonify({'error': 'Chave do Gateway (Omnirouter/OpenRouter) não configurada.'}), 500
            
            headers = {
                "Authorization": f"Bearer {OMNIROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": SITE_URL,
                "X-Title": "ATHENA IA v5.2 OS"
            }
            
            def generate():
                nonlocal selected_model 
                
                # --- INÍCIO DA LÓGICA DO OMNIROUTER AUTOMÁTICO ---
                if selected_model == 'omnirouter-auto':
                    # Lista blindada para suas necessidades: Gratuitas, Open Source, Vibe Coders, Agentes e 24/7 na nuvem.
                    # O código iterará sobre elas automaticamente: se uma falhar, ele usa a de baixo imediatamente.
                    fallback_models = [
                        'qwen/qwen-2.5-coder-32b-instruct:free',          # A melhor IA Open Source para Vibe Coding atual
                        'meta-llama/llama-3.3-70b-instruct:free',         # Excelente orquestradora autônoma
                        'google/gemini-2.0-flash-lite-preview-02-05:free',# Suporte robusto a visão multimodal contínua
                        'deepseek/deepseek-r1-distill-llama-70b:free',    # Raciocínio profundo open source
                        'mistralai/mistral-nemo:free'                     # Backup leve, ágil e altamente funcional
                    ]
                else:
                    # Roteamento padrão caso você decida clicar em um modelo específico manualmente
                    fallback_models = [
                        selected_model,
                        'google/gemini-2.0-flash-lite-preview-02-05:free',
                        'qwen/qwen-2.5-coder-32b-instruct:free',
                        'meta-llama/llama-3.3-70b-instruct:free'
                    ]
                # --- FIM DA LÓGICA DO OMNIROUTER AUTOMÁTICO ---
                
                for model_to_try in fallback_models:
                    if not model_to_try:
                        continue
                        
                    # CORREÇÃO ABSOLUTA DO ERRO 400: Limpeza estrutural do payload.
                    # Identifica rigorosamente se o modelo aceita visão.
                    is_vision_model = any(kw in model_to_try.lower() for kw in ['gemini', 'vision', 'claude', 'gpt-4o'])
                    
                    if images and is_vision_model:
                        current_content = message_content # Array Multimodal (Texto + Base64)
                    else:
                        current_content = user_message # Força String pura. Salva os modelos Llama e Qwen de darem erro 400.
                        
                    payload = {
                        "model": model_to_try, 
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": current_content}
                        ],
                        "max_tokens": 2000,
                        "stream": True
                    }
                    
                    try:
                        resp = requests.post(GATEWAY_URL, headers=headers, json=payload, stream=True, timeout=30)
                        
                        if resp.status_code == 200:
                            for line in resp.iter_lines():
                                if line:
                                    decoded = line.decode('utf-8')
                                    if decoded.startswith('data: ') and '[DONE]' not in decoded:
                                        try:
                                            json_data = json.loads(decoded[6:].strip())
                                            # Proteção extra na extração do dicionário
                                            delta = json_data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                            if delta:
                                                yield delta
                                        except:
                                            pass
                            return # Sucesso absoluto, encerra o loop
                        else:
                            # Log interno no terminal para você debugar, e aviso visual na tela
                            print(f"[GATEWAY ERRO] Modelo: {model_to_try} | Status: {resp.status_code} | Resposta: {resp.text}")
                            yield f"\n\n*(Aviso: Falha no modelo {model_to_try} [Erro {resp.status_code}]. Roteando pelo gateway...)* "
                            continue
                            
                    except Exception as e:
                        print(f"[GATEWAY TIMEOUT] Erro de conexão: {str(e)}")
                        continue
                        
                yield "\n\n**Erro Crítico de Roteamento:** O Gateway (Omnirouter/OpenRouter) não conseguiu processar os modelos gratuitos disponíveis no momento. Aguarde uns instantes ou rode a IA no modo 'HD Local'."
            
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
