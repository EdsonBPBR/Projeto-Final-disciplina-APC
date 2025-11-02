import json
# tá dando erro essa pomba
def salvarDados(dados_atualizados):
    with open('app_biblioteca/registros.json', 'w') as arquivo:
        json.dump(dados_atualizados, arquivo, indent=4, ensure_ascii=False)

def extrairDados():
    with open('app_biblioteca/registros.json', 'r') as arquivo:
        dados = json.load(arquivo)
    return dados
