from flask import Flask
from dotenv import load_dotenv
import os
 
app = Flask(__name__,static_folder='static')
load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')

from .views import *

if __name__ == '__main__':
    app.run(debug=True) # type: ignore
    