# Projeto Final APC (Algoritmos e Programação de Computadores) 2025.1 - 1º periodo

O presente projeto é um sistema desevolvido em Python utilizando o Framework Flask como projeto final da disciplina de Algoritmos e Programação de Computadores, lecionada pelo professor Alexandre Barbosa. 

#### Tecnologias Utilizadas
* Front-End
1. HTML, CSS
2. JavaScript
3. Boostrap

* Back-End
1. Python
2. Flask
3. JSON

#### Requisitos e Informações Adicionais
Por motivos educacionais, não utilizamos um SGBD para incluir o conteúdo de arquivos. Sendo assim, por padrão, o projeto vai com os arquivos criados já com alguns registros, principalmente dos livros, senão é necessário criar três arquivos .json que serão as bases de dados utilizados pelo sistema `livros.json` e `registros.json` em `app_biblioteca/`. 

```
import json
with open('app_biblioteca/registros.json','r') as arquivo
    json.dump([], arquivo)

with open('app_biblioteca/livros.json','r') as arquivo
    json.dump([], arquivo)

with open('app_biblioteca/emprestimos.json','r') as arquivo
    json.dump([], arquivo)
```

Outro ponto a destacar, é necessário cadastrar manualmente os livros, pois ainda não foi desenvolvido a parte dos sistema para o ator da administração. É de atuação dos futuros atores da administração: cadastrar livros, dar baixa nos livros entregues pelos usuários.

---
UNIVERSIDADE FEDERAL DE ALAGOAS

EDSON BARROS PONCIÚNCULA

JACKELINE OLIVEIRA DA SILVA

AUGUSTO CÉSAR DE JESUS
