from main import app 
from flask import render_template, url_for, redirect, request, flash, session
from models import extrairDados, salvarDados
dados = extrairDados()

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
        
        dados.append({
            "matricula":matricula,
            "nome_completo":nome_completo,
            "email":email,
            "senha":senha}) # dava para usar o hash na senha, furutramente implementar isso para não salvar a senha de forma crua
        salvarDados(dados)
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
        login_sucesso = False
        for registro in dados:
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
    if not('usuario' in session): # se na chave 'usuario' não estiver presente no dicionario sessao
        flash('Faça o login para acessar o sistema!', 'warning')
        return redirect(url_for('login'))
    
    usuario = session['usuario'] 
    
    return render_template('inicio.html', usuario=usuario)

@app.route('/biblioteca/acervo_digital')
def acervo():
    return render_template('acervo.html')

@app.route('/biblioteca/sobre')
def sobre():
    return '<h1>Sobre o projeto da biblioteca online</h1>'

