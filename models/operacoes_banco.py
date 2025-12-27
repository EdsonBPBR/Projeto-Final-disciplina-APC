import json

def salvarDados(dados_atualizados, base_dados):
    with open(f'models/{base_dados}.json', 'w') as arquivo:
        json.dump(dados_atualizados, arquivo, indent=4, ensure_ascii=False)

def extrairDados(base_dados):
    with open(f'models/{base_dados}.json', 'r') as arquivo:
        dados = json.load(arquivo)
    return dados
