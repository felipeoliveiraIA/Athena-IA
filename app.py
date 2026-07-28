import os
import json
import socket
import requests
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# BLINDAGEM MÁXIMA: TRAVA DE DIRETÓRIO (PATH JAIL)
# ==========================================
HD_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DADOS_DIR = os.path.join(HD_ROOT, 'Dados')
APP_DIR = os.path.join(HD_ROOT, 'App')

os.makedirs(DADOS_DIR, exist_ok=True)

def verificar_se_e_seguro(caminho_desejado):
    """Garante matematicamente que o caminho está dentro da pasta do projeto."""
    caminho_absoluto = os.path.abspath(caminho_desejado)
    if not caminho_absoluto.startswith(HD_ROOT):
        raise PermissionError("ACESSO NEGADO: A IA tentou sair da pasta permitida!")
    return caminho_absoluto

# ==========================================
# SINCRONIZAÇÃO SEGURA COM GITHUB
# ==========================================
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def sync_with_github():
    print("🌐 Internet detectada! Sincronizando apenas o código e dados permitidos...")
    try:
        subprocess.run(["git", "pull", "origin", "main"], cwd=APP_DIR, check=True)
        subprocess.run(["git", "add", "../Dados/*"], cwd=APP_DIR)
        subprocess.run(["git", "commit", "-m", "Auto-sync seguro"], cwd=APP_DIR)
        subprocess.run(["git", "push", "origin", "main"], cwd=APP_DIR)
        print("✅ Sincronização segura concluída.")
    except Exception as e:
        print(f"⚠️ Nota de sync: {e}")

# ==========================================
# ROTA DE CHAT ISOLADA
# ==========================================
@app.route('/chat', methods=['POST'])
def chat():
    dados_usuario = request.json
    mensagem = dados_usuario.get('mensagem')
    historico = dados_usuario.get('historico', [])

    mensagens_formatadas = [
        {"role": "system", "content": "Você é um assistente estritamente isolado em ambiente seguro no HD externo. Você não tem acesso a arquivos pessoais do usuário."}
    ]
    mensagens_formatadas.extend(historico)
    mensagens_formatadas.append({"role": "user", "content": mensagem})

    lm_studio_url = "http://127.0.0.1:1234/v1/chat/completions"

    payload = {
        "model": "local-model",
        "messages": mensagens_formatadas,
        "temperature": 0.7
    }

    try:
        resposta_lm = requests.post(lm_studio_url, json=payload, timeout=120)
        resposta_json = resposta_lm.json()
        texto_ia = resposta_json['choices'][0]['message']['content']

        salvar_historico_seguro(mensagem, texto_ia)

        return jsonify({"resposta": texto_ia})
    
    except requests.exceptions.ConnectionError:
        return jsonify({"erro": "O LM Studio não está rodando. Abra o LM Studio no HD e clique em Start Server."}), 500

def salvar_historico_seguro(usuario_msg, ia_msg):
    caminho_arquivo = os.path.join(DADOS_DIR, 'historico_offline.json')
    caminho_seguro = verificar_se_e_seguro(caminho_arquivo)
    
    historico = []
    if os.path.exists(caminho_seguro):
        with open(caminho_seguro, 'r', encoding='utf-8') as f:
            historico = json.load(f)
            
    historico.append({"user": usuario_msg, "ia": ia_msg})
    
    with open(caminho_seguro, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    if check_internet():
        sync_with_github()
    else:
        print("🚫 Sem internet. Rodando em MODO TOTALMENTE OFFLINE E SEGURO.")
    
    app.run(host='127.0.0.1', port=5000)
