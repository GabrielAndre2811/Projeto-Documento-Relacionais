import json
import os

CONFIG_FILE = 'config.json'

def carregar_configuracoes():
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    else:
        return {"palavras_chave": {}, "nomes": []}

def salvar_configuracoes(dados_configuracao):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(dados_configuracao, file, indent=4)
