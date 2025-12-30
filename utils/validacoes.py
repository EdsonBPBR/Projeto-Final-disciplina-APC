from models.data_utils import extrairDados
from werkzeug.security import check_password_hash

def verificar_matricula_existente(usuarios, matricula_alvo, index=0):
    """
    Função recursiva obrigatória para complemento de nota, percorre linearmente todas as matrículas já cadastradas
    
    :param usuarios: 
    :param matricula_alvo: matricula informada pelo usuário
    :param index: posições dos elementos na lista do dicionário
    """
    if index >= len(usuarios):
        return False 
    if usuarios[index]['matricula'] == matricula_alvo:
        return True  
    return verificar_matricula_existente(usuarios, matricula_alvo, index + 1)

def validar_email(email):
    """
    Validar o e-mail, verificar se o mesmo é institucional ou não
    
    :param email: email informado pelo usuário
    """
    dominios_institucionais = {
        'arapiraca.ufal.br',
        'palmeira.ufal.br',
        'ic.ufal.br',
        'nti.ufal.br',
    }
    
    if not(email[(email.find('@')+1):] in dominios_institucionais):
        return True
    return False

def realiza_login(matricula, senha):
    dados_usuarios = extrairDados('registros')
    for registro in dados_usuarios: # busca linear, queda de desempenho, melhorar futuramente com uma nova estrutura de dados
        if registro['matricula'] == matricula and check_password_hash(registro['senha'], str(senha)):
            return True, registro
    return False, None

def verifica_matricula_cadastrada_retorna_email(matricula):
    dados_registros = extrairDados('registros')
    for registro in dados_registros:
        if registro['matricula'] == matricula:
            return True, registro['email']
    return False, None

def verifica_usuario_logado(session):
    logado = 'usuario' in session
    return not(logado)
    # eu tentei colocar a decisão dentro da funmção mas dá erro, num sei pq