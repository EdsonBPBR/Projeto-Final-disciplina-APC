from main import app 
from datetime import date, timedelta
from flask import render_template, url_for, redirect, request, flash, session
from models import extrairDados, salvarDados

@app.route('/')
def raiz():
    return redirect(url_for('login'))

@app.route('/cadastro', methods = ['GET', 'POST']) # trabalha com os metodos get - para obter a página sem informacoes e post para enviar os dados dor formsm
def cadastro():
    if request.method == 'POST':
        # obter os dadssos da interface web, se o método for post > enviar
        matricula = request.form.get('matricula')
        nome_completo = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        # implementar os tratamentos do tamanho e tipo da matricula
        # tratamento para verificar se o email pertence a ufal
        
        if senha != confirmar_senha:
            flash('Senhas informadas não coincidem', 'warning')
            return redirect(url_for('cadastro'))
        
        dados_usuarios = extrairDados('registros')
        
        def verificar_matricula_existente(usuarios, matricula_alvo, index=0): # funcao recursiva que verifica se a matricual oinformada pelo usuario no ato do cadastro ja existe
            if index >= len(usuarios):
                return False 
            if usuarios[index]['matricula'] == matricula_alvo:
                return True  
            return verificar_matricula_existente(usuarios, matricula_alvo, index + 1)
        
        if verificar_matricula_existente(dados_usuarios, matricula):
            flash('Matrícula ja cadastrada no sistema!', 'warning')
            return redirect(url_for('cadastro'))
        
        dados_usuarios.append({
            "matricula":matricula,
            "nome_completo":nome_completo,
            "email":email,
            "senha":senha}) # dava para usar o hash na senha, furutramente implementar isso para não salvar a senha de forma crua
        salvarDados(dados_usuarios, 'registros')
        flash('Cadastro criado com sucesso! Faça o login!', 'success')
        return redirect(url_for('cadastro'))
        
        # inserir sistema para percorrer os dados já cadastrados para verificar se ja existe uma matricula cdastrada
    return render_template('cadastro.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')
        print(matricula, senha)
        
        # verificar se os dados informados estao cadastrados no aquivo json
        dados_usuarios = extrairDados('registros')
        login_sucesso = False
        for registro in dados_usuarios:
            if registro['matricula'] == matricula and registro['senha'] == senha:
                login_sucesso = True
                usuario = registro
                break
        
        if login_sucesso:
            session['usuario'] = { # o flask, bem como no django, tem o módulo nativo session, que já faz esse tratamento com os cookies utilizados pelo navegador
                'matricula': usuario['matricula'],
                'nome_completo': usuario['nome_completo'],
                'email': usuario['email'],
            }
            # print(session)
            return redirect(url_for('inicio'))
            
        else:
            flash('Matricula ou senha incorreta. Ou usuário não cadastrado!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/biblioteca')
def inicio():
    if verificaUsuarioLogado(session): # se na chave 'usuario' não estiver presente no dicionario sessao
        flash('Faça o login para acessar o sistema!', 'warning')
        return redirect(url_for('login'))

    dados_emprestimos = extrairDados('emprestimos')
    livros_emprestados = []
    
    for emprestimo in dados_emprestimos:
        if session['usuario']['matricula'] == emprestimo['matricula_usuario'] and emprestimo['status'] == 'aberto':
            livros_emprestados.append(emprestimo)
        
    n_livros_emprestados = len(livros_emprestados)

    return render_template('inicio.html', nome_usuario=session['usuario']['nome_completo'],
                                        n_livros_emprestados=n_livros_emprestados,
                                        livros_emprestados=livros_emprestados)
    # quando chegar antes de fazer o deploy pro GitHub, realzar uma série de testes pra verificar se tá tudo ok

@app.route('/biblioteca/acervo_digital')
@app.route('/biblioteca/acervo_digital/<int:pagina>')
def acervo(pagina=1):
    if verificaUsuarioLogado(session):
        flash('Faça o login para acessar o sistema!', 'warning')
        return redirect(url_for('login'))
    
    dados_livros = extrairDados('livros')
    
    # implemetei, pedi ajuda tbm ao chat, como implementar sistema depaginacao com base na matriz montada
    matriz_livros_cadastrados = []
    n_linhas = len(dados_livros) // 10
    resto_livros = len(dados_livros) % 10
    if resto_livros != 0:
        n_linhas += 1
    
    for i in range(n_linhas):
        inicio = i * 10
        fim = inicio + 10
        linha = dados_livros[inicio:fim]
        matriz_livros_cadastrados.append(linha)
    
    # PAGINAÇÃO: 1 linha da matriz por página (10 livros)
    total_paginas = n_linhas  # Cada página é uma linha da matriz
    
    # Ajustar página
    if pagina < 1:
        pagina = 1
    elif pagina > total_paginas:
        pagina = total_paginas
    
    # Pegar APENAS UMA LINHA da matriz para esta página
    matriz_pagina = [matriz_livros_cadastrados[pagina - 1]]  # Apenas a linha da página atual
    
    return render_template('acervo.html',
                         matriz_livros=matriz_pagina,
                         pagina_atual=pagina,
                         total_paginas=total_paginas,
                         total_livros=len(dados_livros))

@app.route('/biblioteca/emprestimo/livro/<string:id>', methods = ['GET', 'POST'])
def emprestimo_livro(id): 
    if verificaUsuarioLogado(session): # se na chave 'usuario' não estiver presente no dicionario sessao 
        flash('Faça o login para acessar o sistema!', 'warning')#  funcao para o emprestimo de somente o livro, o emprestimos to pensando em colocar outra coisa..
        return redirect(url_for('login'))
    
    dados = extrairDados('livros')
    dados_emprestimos = extrairDados('emprestimos')
    
    for registro in dados:
        if registro['cod'] == id:
            livro = registro
            break   
    
    # contar o número de livros que o usuário já pegou emprestado
    n_livros_emprestados = 0
    permissao_emprestimo = True
    for emprestimo in dados_emprestimos:
        if session['usuario']['matricula'] == emprestimo['matricula_usuario']:
           n_livros_emprestados += 1
    
    if n_livros_emprestados > 3:
        permissao_emprestimo = False
    
    if livro['quantidade'] < 2: # basicamente, se a quantidade for menor que 2, atualizar o status pra esgotado e salvar na base de dados. Ficar atento aqui, na ultima vez o erro foi aqui
        livro['status'] = 'esgotado'
        salvarDados(dados, 'livros')
    
    caminho_capa = livro['capa']
    ultimo_nome = caminho_capa.split('/')[-1]
    
    info_livro = {
        'cod': livro['cod'],
        'capa': ultimo_nome,
        'titulo': livro['titulo'],
        'quantidade': livro['quantidade'],
        'autor': livro['autor'],
        'area_conhecimento': livro['area_conhecimento'],
        'status': livro['status'],
        'biblioteca': livro['biblioteca'],
        'permissao_emprestimo': not(permissao_emprestimo)
    }
    
    # EU PARTICULAMENTE ENTENDI O ERRO DE ONTEM, ERA NO STATUS. ELE APARENTEMENTE NÃO ESTAVA SALVANDO ESSA CAMPO NO JS, AÍ O PYTHON TENTAVA ACESSAR E DAVA ERRO.
    # MESMO ASSIM DEIXO PARA FAZER AMANHÃ:
    # * RELACIONAR N LIVROS EMPRESTADOS DO USUÁRIO, SE FOR MAIOR OU IGUAL A 4 ALTERAR MENSAGEM E DESABILITAR BOTÃO PARA EMPRÉSTIMO
    # E CREIO QUE É ISSO
    # * CRIAR A PÁGINA DE EDICAÇÃO DE PERFIL
    # * E ALGO AINDA SOBRE MATRIZES
    
    # implementar o requisito: se o usuário já possui mais de 3 livros cadastrados, a mensagem: 'Você pode obter esse livro! ' tem que alterar conforme o problema do usuário e desativar o botão: 'obter livro'
    
    if request.method == 'POST':
        livro['quantidade'] = livro['quantidade'] - 1 # decrementa uma unidade a cada empréstimo realizado por usuários
        salvarDados(dados, 'livros') # salvar essa alteração, prestar atenção senão vai fazer como na ultima vez kkk

        flash(f'Emprestimo livro: {livro['titulo']} realizado com sucesso! Vá até a BIBLIOTECA UFAL ARAPIRACA SEDE para retirada', 'success')

        data_emprestimo = date.today()
        data_devolucao = data_emprestimo + timedelta(days=15)
        dados_livros = extrairDados('emprestimos')
        
        # estava pensanddo em inserir 3 estágios do livro: "em aberto" (o aluno está com ele), "pendente" (passou da data de entrega e irá começar a acumular multas) e "entregue" (qiando o usuário já tiver entregue o livro)
        livro_emprestado = {
            'matricula_usuario': session['usuario']['matricula'],
            'email_usuario': session['usuario']['email'],
            'cod_livro': info_livro['cod'],
            'titulo': info_livro['titulo'],
            'autor': info_livro['autor'],
            'data_emprestimo': data_emprestimo.strftime('%d/%m/%Y'),
            'data_devolucao': data_devolucao.strftime('%d/%m/%Y'),
            'status': 'aberto' # por padrão, o status vai 'aberto',
        }
        
        dados_livros.append(livro_emprestado) 
        salvarDados(dados_livros, 'emprestimos')
        # ainda inserir sistema para remover o 
        return redirect(url_for('emprestimos'))

    return render_template('emprestimo_livro.html', livro = info_livro)

@app.route('/biblioteca/emprestimos')
def emprestimos():
    if verificaUsuarioLogado(session): # se na chave 'usuario' não estiver presente no dicionario sessao 
        flash('Faça o login para acessar o sistema!', 'warning')#  funcao para o emprestimo de somente o livro, o emprestimos to pensando em colocar outra coisa..
        return redirect(url_for('login'))
    
    # print(session['usuario']['matricula'])
    livros_emprestados = [] # resolvemos adicionar os livros no dicionario, pois cada livro emprestado é único, não existirá a repetição de outro mesmo livro
    # percorrer os livros e se a data de hoje for igual a data de devolução, atualizar o status para 'pendente'
    data_emprestimo = date.today()
    dados_atualizados = False 
    
    dados_livros = extrairDados('emprestimos')
    for registro in dados_livros: # percorrer os livros emprestados para encontrar TODOS os livros emprestados do usuário
        if session['usuario']['matricula'] == registro['matricula_usuario']:
            livros_emprestados.append([registro['titulo'], registro['autor'], registro['data_emprestimo'], registro['data_devolucao'], registro['status']])
        
        if data_emprestimo.strftime('%d/%m/%Y') == registro['data_devolucao'] and  registro['status'] != 'entregue' :
            registro['status'] = 'pendente'  # atualizar o status
            dados_atualizados = True
            
    if dados_atualizados:
        salvarDados(dados_livros, 'emprestimos')

    # percorrer os livros e se a data de hoje for igual a data de devolução, atualizar o status para 'pendente'
    if len(livros_emprestados) >= 4:
        flash('Você não pode mais obter livros emprestados! Limite excedido!', 'warning')
    
    return render_template('emprestimos.html', info_livros_emprestados = livros_emprestados)

@app.route('/biblioteca/sobre')
def sobre():
    return '<h1>Sobre o projeto da biblioteca online</h1>'

def verificaUsuarioLogado(session):
    logado = 'usuario' in session
    return not(logado)
    # eu tentei colocar a decisão dentro da funmção mas dá erro, num sei pq