from app_biblioteca.main import app
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, url_for, redirect, request, flash, session, abort
from models.data_utils import extrairDados, salvarDados
from utils.validacoes import verificar_matricula_existente, validar_email, realiza_login, verifica_matricula_cadastrada_retorna_email, verifica_usuario_logado, verifica_email_cadastrado

@app.route('/')
def raiz():
    return redirect(url_for('login'))

@app.route('/cadastro', methods = ['GET', 'POST']) 
def cadastro():
    """
    Cadastra o discente na base de dados
    """
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        nome_completo = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if validar_email(email):
            flash('E-mail inválido! Informe um email institucional!', 'warning')
            return redirect(url_for('cadastro'))
        
        if len(str(matricula)) != 10:
            flash('Matricula inválida!', 'warning')
            return redirect(url_for('cadastro'))
        
        if senha != confirmar_senha:
            flash('Senhas informadas não coincidem', 'warning')
            return redirect(url_for('cadastro'))
        
        try:
            dados_usuarios = extrairDados('registros')
            if verificar_matricula_existente(dados_usuarios, matricula):
                flash('Matrícula ja cadastrada no sistema!', 'warning')
                return redirect(url_for('cadastro'))
            
            dados_usuarios.append({
                "matricula":matricula,
                "nome_completo":nome_completo,
                "email":email,
                "senha":generate_password_hash(str(senha))
            })
            
            salvarDados(dados_usuarios, 'registros')
            flash('Cadastro criado com sucesso! Faça o login!', 'success')
            
        except Exception as erro:
            flash(f'Não foi possível cadastrar o discente: {erro}', 'warning')
            return redirect(url_for('cadastro'))
        
        return redirect(url_for('cadastro'))
    return render_template('cadastro.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    """
    Realiza o login do discente redirecionando para o 'inicio', armazenando-o na sessão do navegador se a operação for sucedida 
    """
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')

        login_sucesso, usuario = realiza_login(matricula, senha)
        if login_sucesso:
            session['usuario'] = {
                'matricula': usuario['matricula'], # está vermelho, pq estou retornando None se o login não tiver sucesso
                'nome_completo': usuario['nome_completo'],
                'email': usuario['email'],
            }
            return redirect(url_for('inicio'))
        
        else:
            flash('Matricula ou senha incorreta. Ou usuário não cadastrado!', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        matricula = request.form.get('matricula')

        existe, email = verifica_matricula_cadastrada_retorna_email(matricula)
        if existe:
            flash(f'E-mail enviado para: {email} ! Verifique também sua caixa de spam', 'success')
            return redirect(url_for('recuperar_senha'))
        flash('Matricula não encontrada', 'danger')
    return render_template('recuperar_senha.html')

@app.route('/biblioteca')
def inicio():
    if verifica_usuario_logado(session):
        flash('Faça o login para acessar o sistema!', 'warning')
        return redirect(url_for('login')), 302
    livros_emprestados = []
    
    try:
        dados_emprestimos = extrairDados('emprestimos')
        for emprestimo in dados_emprestimos:
            if (session['usuario']['matricula'] == emprestimo['matricula_usuario'] 
                and emprestimo['status'] == 'aberto'):
                livros_emprestados.append(emprestimo)
                
    except Exception as erro:
        flash(f'Não foi possível carregar informações: {erro}')
            
    return render_template('inicio.html', 
                           nome_usuario=session['usuario']['nome_completo'].split(), 
                           n_livros_emprestados=len(livros_emprestados),
                           livros_emprestados=livros_emprestados
                           )

@app.route('/biblioteca/acervo_digital', methods = ['GET', 'POST'])
@app.route('/biblioteca/acervo_digital/<int:pagina>')
def acervo(pagina=1):
    if verifica_usuario_logado(session):
        flash('Faça o login para acessar o sistema!', 'warning')
        return redirect(url_for('login')), 302
    
    dados = extrairDados('livros')
    if request.method == 'POST':
        """
        Sistema de pesquisa e filtro por titulo e status
        """
        opcao = request.form.get('acao') # busca os valores 'values' dos botões, pois há dois botões em POST
        instancias = []
        
        if opcao == 'pesquisar_titulo': 
            try:
                pesquisa_titulo = request.form.get('pesquisa_titulo')
                
                for dado in dados:
                    if str(pesquisa_titulo).title() in dado['titulo']:
                        instancias.append(dado)
                        
            except Exception as erro:
                flash(f'Não foi possível realizar pesquisa por título: {erro}', 'danger')
                return redirect(url_for('acervo'))
                
        elif opcao == 'aplicar_filtro':
            try:
                status = request.form.get('status')
                
                for dado in dados: 
                    if dado['status'] == status:
                        instancias.append(dado)
                        
            except Exception as erro:
                flash(f'Não foi possível realizar filtro: {erro}', 'danger')
                return redirect(url_for('acervo'))              
            
        if len(instancias) > 0:
            return render_template('acervo.html', dados = instancias)
        else:
            flash('Nenhum resultado encontrado', 'warning')
            return redirect(url_for('acervo'))
    return render_template('acervo.html', dados = dados)

@app.route('/biblioteca/emprestimo/livro/<string:id>', methods = ['GET', 'POST'])
def emprestimo_livro(id): 
    if verifica_usuario_logado(session): 
        flash('Faça o login para acessar o sistema!', 'warning')
        return redirect(url_for('login')), 302
    
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
    
    if request.method == 'POST':
        livro['quantidade'] = livro['quantidade'] - 1 # decrementa uma unidade a cada empréstimo realizado por usuários
        salvarDados(dados, 'livros') # salvar essa alteração, prestar atenção senão vai fazer como na ultima vez kkk

        flash(f"Emprestimo livro: {livro['titulo']} realizado com sucesso! Vá até a sede para retirada", 'success')

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
        return redirect(url_for('emprestimos'))
    return render_template('emprestimo_livro.html', livro = info_livro)

@app.route('/biblioteca/emprestimos')
def emprestimos():
    if verifica_usuario_logado(session): 
        flash('Faça o login para acessar o sistema!', 'warning')
        return redirect(url_for('login'))
    
    livros_emprestados = [] 
    # percorrer os livros e se a data de hoje for igual a data de devolução, atualizar o status para 'pendente'
    data_emprestimo = date.today()
    dados_atualizados = False 
    
    try:
        dados_livros = extrairDados('emprestimos')
        
        for registro in dados_livros: # percorrer os livros emprestados para encontrar TODOS os livros emprestados do usuário
            if session['usuario']['matricula'] == registro['matricula_usuario']:
                livros_emprestados.append([registro['titulo'], registro['autor'], registro['data_emprestimo'], registro['data_devolucao'], registro['status']])
            
            if data_emprestimo.strftime('%d/%m/%Y') == registro['data_devolucao'] and registro['status'] != 'entregue':
                registro['status'] = 'pendente'  # atualizar o status
                dados_atualizados = True
                
        if dados_atualizados:
            salvarDados(dados_livros, 'emprestimos')

        if len(livros_emprestados) >= 4:
            flash('Você não pode mais obter livros emprestados! Limite excedido!', 'warning')
            
    except Exception as erro:
        flash(f'Não foi possivel carregar os livros emprestados: {erro}')        
    return render_template('emprestimos.html', info_livros_emprestados = livros_emprestados)

@app.route('/biblioteca/sobre')
def sobre():
    return '<h1>Sobre o projeto da biblioteca online</h1>'

@app.route('/biblioteca/perfil/', methods = ['GET', 'POST'])
def editar_perfil():
    if verifica_usuario_logado(session): 
        flash('Faça o login para acessar o sistema!', 'warning')
        return redirect(url_for('login')), 302
    
    try:
        dados = extrairDados('registros')
        
        for dado in dados:
            if dado['matricula'] == session['usuario']['matricula']:
                usuario = dado
                break
        
        if request.method == 'POST':
            novo_nome_completo = request.form.get('nome_completo')
            novo_email = request.form.get('email')
            
            if verifica_email_cadastrado(novo_email, dados):
                flash('E-mail já cadastrado!', 'warning')
            
            else:
                usuario['nome_completo'] = novo_nome_completo
                usuario['email'] = novo_email
                
                salvarDados(dados, 'registros')
                flash('Dados alterados com sucesso!', 'success')
            
    except Exception as erro:
        flash(f'Não foi possível editar perfil: {erro}')
    return render_template('editar_perfil.html', dados = usuario)

@app.route('/biblioteca/perfil/editar_senha/', methods = ['GET', 'POST'])
def editar_senha():
    if verifica_usuario_logado(session): 
        flash('Faça o login para acessar o sistema!', 'warning')
        return redirect(url_for('login')), 302
    
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        try:
            dados = extrairDados('registros')
            for dado in dados:
                if dado['matricula'] == session['usuario']['matricula']:
                    usuario = dado
                    break
            
            if check_password_hash(usuario['senha'], str(senha_atual)):
                if nova_senha == confirmar_senha:
                    usuario['senha'] = generate_password_hash(str(nova_senha))
                    salvarDados(dados, 'registros')
                    flash('Senha alterada com sucesso!', 'success')
                else:
                    flash('Senhas não coincidem', 'warning')
            else:
                flash('Não foi possível alterar a senha', 'danger')
                 
        except Exception as erro:
            flash(f'Não foi possível alterar senha: {erro}')
    return render_template('editar_senha.html')

@app.route('/biblioteca/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
    
@app.context_processor
def inject_usuario():
    """
    Função resposável por injetar em TODOS os templates informações do usuário que realizou a sessão. 
    """
    usuario = session.get('usuario')
    return {
        'usuario_logado': usuario,
        'matricula_usuario': usuario.get('matricula') if usuario else None
    }