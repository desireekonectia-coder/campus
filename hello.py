from flask import Flask, render_template, request
import psycopg2

def conectarCampus():
    conexion = psycopg2.connect(
        host="localhost",
        database="campus",
        user="postgres",
        password="admin"
    )
    return conexion

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        usuario = request.form["user"]
        password = request.form["password"]
        email = request.form["email"]
       
        conn= conectarCampus()
        cursor = conn.cursor()
        cursor.execute("insert into users (username, password, user_mail) values (%s, %s, %s)", (usuario, password, email))

        conn.commit()      
        cursor.close()
        conn.close()

        return render_template("user.html", usuario=usuario, email=email)
        #return f"<p>Usuario {usuario} ha intentado iniciar sesion</p>"


    return render_template("login.html")






