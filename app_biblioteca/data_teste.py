from datetime import date, timedelta

data_emprestimo = date.today()
data_devolucao = data_emprestimo + timedelta(days=15)
print(f"Data do Empréstimo: {data_emprestimo.strftime('%d/%m/%Y')}")
print(f"Data de Devolução (+15 dias): {data_devolucao.strftime('%d/%m/%Y')}")

# estava estudando o sistema de datas, agora preciso utilizar isso para poder inserir no sistema de datas do emprestimo do livro 