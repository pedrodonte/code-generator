from flask import Flask, request, render_template

from blueprints.generador import generador_page

app = Flask(__name__, template_folder='templates')

app.register_blueprint(generador_page)
app.secret_key = 'esto es para que exista session'


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('autor.html', name="Pedro")
