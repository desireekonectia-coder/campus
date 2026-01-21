from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# CONFIGURACIÓN (Rellena con tus datos de pgAdmin)
# Estructura: postgresql://usuario:contraseña@localhost:5432/nombre_base_datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:TU_CONTRASEÑA@localhost:5432/TU_BASE_DE_DATOS'
db = SQLAlchemy(app)

@app.route('/')
def hola():
    return "<h1>¡Servidor Flask funcionando y conectado!</h1>"

if __name__ == '__main__':
    app.run(debug=True)