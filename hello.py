from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        usuario = request.form["user"]
        password = request.form["password"]

        print("Usuario ingresado:", usuario)
        print("Password:", password)

        return f"Usuario {usuario} ha intentado iniciar sesion"


    return render_template("login.html")

@app.route("/user")
def hello_user():
    return "<p>Hello, Usuario</p>"

@app.route("/logged")
def logged_user():
    return render_template("user_custom.html")

@app.route("/horario")
def horario():
    return render_template("horario.html")

if __name__ == "__main__":
    app.run(debug=True)

