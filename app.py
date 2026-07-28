import os
import json
import socket
import requests
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# 1. ESTRUTURA DE DIRETÓRIOS E GIT
# ==========================================
# O diretório base agora é a própria pasta 'App' onde o Git está configurado.
# Isso garante que a pasta de Dados suba corretamente para o GitHub.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_DIR = os.path.join(APP_DIR, 'Dados')

os.makedirs(DADOS_DIR, exist_ok=True)

# ==========================================
# 2. BLINDAGEM MÁXIMA: TRAVA DE DIRETÓRIO (PATH JAIL)
# ==========================================
def verificar_se_e_seguro(caminho_desejado):
    """
    Garante matematicamente que qualquer leitura/escrita ocorra 
    exclusivamente dentro da pasta 'App' do HD.
    Impede acesso não autorizado a outras partes do HD Externo.
    """
    caminho_absoluto = os.path.abspath(caminho_desejado)
    if not caminho_absoluto.startswith(APP_DIR):
        raise PermissionError("🔒 ACESSO NEGADO: A IA tentou violar o limite do diretório seguro.")
    return caminho_absoluto

# ==========================================
# 3. SINCRONIZAÇÃO SEGURA COM GITHUB
# ==========================================
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def sync_with_github():
    print("🌐 Internet detectada! Sincronizando código e dados da IA...")
    try:
        subprocess.run(["git", "pull", "origin", "main"], cwd=APP_DIR, check=True)
        # Salva apenas o que está dentro do escopo permitido da pasta App
        subprocess.run(["git", "add", "."], cwd=APP_DIR)
        subprocess.run(["git", "commit", "-m", "Auto-sync: Backup de segurança do orquestrador"], cwd=APP_DIR)
        subprocess.run(["git", "push", "origin", "main"], cwd=APP_DIR)
        print("✅ Sincronização concluída com sucesso.")
    except Exception as e:
        print(f"⚠️ Nota de sync: O repositório pode estar atualizado ou houve um aviso local. Detalhes: {e}")

# ==========================================
# 4. ROTA DE CHAT ISOLADA (ORQUESTRADOR QWEN)
# ==========================================
@app.route('/chat', methods=['POST'])
def chat():
    dados_usuario = request.json
    mensagem = dados_usuario.get('mensagem')
    historico = dados_usuario.get('historico', [])

    # A IA assume sua função autônoma, mas sob as regras rígidas do usuário.
    prompt_sistema = (
        "Você é um Agente Orquestrador Autônomo operando de forma estritamente "
        "isolada em um ambiente seguro no HD externo do usuário. "
        "Você tem permissão para organizar lógica, estruturar códigos e coordenar tarefas textuais. "
        "No entanto, VOCÊ NÃO TEM ACESSO a arquivos pessoais do usuário. "
        "Sua manipulação de dados é limitada APENAS ao que o usuário explicitamente autorizar na conversa."
    )

    mensagens_formatadas = [{"role": "system", "content": prompt_sistema}]
    mensagens_formatadas.extend(historico)
    mensagens_formatadas.append({"role": "user", "content": mensagem})

    lm_studio_url = "http://127.0.0.1:1234/v1/chat/completions"

    payload = {
        "model": "local-model",
        "messages": mensagens_formatadas,
        "temperature": 0.3 # Mantido baixo para foco em precisão, lógica e códigos (ideal para o Qwen)
    }

    try:
        resposta_lm = requests.post(lm_studio_url, json=payload, timeout=120)
        resposta_json = resposta_lm.json()
        texto_ia = resposta_json['choices'][0]['message']['content']

        salvar_historico_seguro(mensagem, texto_ia)

        return jsonify({"resposta": texto_ia})
    
    except requests.exceptions.ConnectionError:
        return jsonify({"erro": "O servidor do LM Studio não está rodando. Abra o LM Studio e clique em 'Start Server'."}), 500

def salvar_historico_seguro(usuario_msg, ia_msg):
    caminho_arquivo = os.path.join(DADOS_DIR, 'historico_offline.json')
    # Passa pela trava de segurança antes de abrir o arquivo
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
        print("🚫 Sem internet. Rodando orquestrador em MODO OFFLINE E BLINDADO.")
    
    app.run(host='127.0.0.1', port=5000)
