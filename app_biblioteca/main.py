from flask import Flask
 
app = Flask(__name__,static_folder='static')
app.secret_key = '123456'

from views import * # arquivo contem as rotas e tratamento das requisições

if __name__ == '__main__':
    app.run(debug=True) # type: ignore