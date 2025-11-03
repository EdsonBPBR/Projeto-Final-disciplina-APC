import json
# resolkvi separa para models, a manipulacao dos arquivos json, já que não decidimos usar um sgbdr já para inserir o conteudo de arquivos
def salvarDados(dados_atualizados, base_dados):
    with open(f'app_biblioteca/{base_dados}.json', 'w') as arquivo:
        json.dump(dados_atualizados, arquivo, indent=4, ensure_ascii=False)

def extrairDados(base_dados):
    with open(f'app_biblioteca/{base_dados}.json', 'r') as arquivo:
        dados = json.load(arquivo)
    return dados
