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

    usuario = session['usuario'] 
    return render_template('inicio.html', usuario=usuario)
    # ainda falta desenvolver futuramente aqui

@app.route('/biblioteca/acervo_digital')
def acervo():
    if verificaUsuarioLogado(session): # se na chave 'usuario' não estiver presente no dicionario sessao
        flash('Faça o login para acessar o sistema!', 'warning')
        return redirect(url_for('login'))
    
    dados_livros = extrairDados('livros')
    print(dados_livros)
    return render_template('acervo.html', dados_livros=dados_livros)

@app.route('/biblioteca/emprestimo/livro/<string:id>', methods = ['GET', 'POST'])
def emprestimo_livro(id): 
    
    if verificaUsuarioLogado(session): # se na chave 'usuario' não estiver presente no dicionario sessao 
        flash('Faça o login para acessar o sistema!', 'warning')#  funcao para o emprestimo de somente o livro, o emprestimos to pensando em colocar outra coisa..
        return redirect(url_for('login'))
    
    dados = extrairDados('livros')
    for registro in dados:
        if registro['cod'] == id:
            livro = registro
            break
    
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
        'biblioteca': livro['biblioteca']
    }
    
    # EU PARTICULAMENTE ENTENDI O ERRO DE ONTEM, ERA NO STATUS. ELE APARENTEMENTE NÃO ESTAVA SALVANDO ESSA CAMPO NO JS, AÍ O PYTHON TENTAVA ACESSAR E DAVA ERRO.
    # MESMO ASSIM DEIXO PARA FAZER AMANHÃ:
    # * INSERIR NOVAMENTE A TELA DE FUNDO DO LOGIN
    # * NA TELA DE EMPRESTIMOS, EXIBIR UM ALERT CASO O NÚMERO DE LIVROS FOR IGUAL OU MAIOR A 4
    # * RELACIONAR N LIVROS EMPRESTADOS DO USUÁRIO, SE FOR MAIOR OU IGUAL A 4 ALTERAR MENSAGEM E DESABILITAR BOTÃO PARA EMPRÉSTIMO
    # E CREIO QUE É ISSO
    # * CRIAR A PÁGINA DE EDICAÇÃO DE PERFIL
    # * E ALGO AINDA SOBRE MATRIZES
    
    # implementar o requisito: se o usuário já possui mais de 3 livros cadastrados, a mensagem: 'Você pode obter esse livro! ' tem que alterar conforme o problema do usuário e desativar o botão: 'obter livro'
    
    if request.method == 'POST':
        flash(f'Emprestimo livro: {livro['titulo']} realizado com sucesso! Vá até a BIBLIOTECA UFAL ARAPIRACA SEDE para retirada', 'success')

        data_emprestimo = date.today()
        data_devolucao = data_emprestimo + timedelta(days=15)
        dados_livros = extrairDados('emprestimos')
        
        livro_emprestado = {
            'matricula_usuario': session['usuario']['matricula'],
            'email_usuario': session['usuario']['email'],
            'cod_livro': info_livro['cod'],
            'titulo': info_livro['titulo'],
            'autor': info_livro['autor'],
            'data_emprestimo': data_emprestimo.strftime('%d/%m/%Y'),
            'data_devolucao': data_devolucao.strftime('%d/%m/%Y')
        }
        
        dados_livros.append(livro_emprestado)
        print(dados_livros)
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
    
    dados_livros = extrairDados('emprestimos')
    for registro in dados_livros: # percorrer os livros emprestados para encontrar TODOS os livros emprestados do usuário
        if session['usuario']['matricula'] == registro['matricula_usuario']:
            livros_emprestados.append((registro['titulo'], registro['autor'], registro['data_emprestimo'], registro['data_devolucao']))
    
    return render_template('emprestimos.html', info_livros_emprestados = livros_emprestados)

@app.route('/biblioteca/sobre')
def sobre():
    return '<h1>Sobre o projeto da biblioteca online</h1>'

def verificaUsuarioLogado(session):
    logado = 'usuario' in session
    return not(logado)
    # eu tentei colocar a decisão dentro da funmção mas dá erro, num sei pq