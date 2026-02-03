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

@app.route("/", methods=["GET", "POST"])
def login_registro():
    mensaje = ""
    mostrar_email = False  # Para decidir si mostramos campo email para registro

    if request.method == "POST":
        usuario = request.form["user"]
        password = request.form["password"]
        email = request.form.get("email", None)

        conn = conectarCampus()
        cursor = conn.cursor()

        # Revisamos si el usuario ya existe
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (usuario, password))
        user = cursor.fetchone()

        if user:
            # Usuario existe → logeo
            cursor.close()
            conn.close()
            return render_template("user.html", usuario=usuario, email=user[3])
        else:
            # Usuario no existe → mostrar formulario de registro
            mostrar_email = True
            mensaje = "Usuario no existe. Complete su email para registrarse."

            # Si ya llenó el email, lo registramos
            if email:
                cursor.execute(
                    "INSERT INTO users (username, password, user_mail) VALUES (%s, %s, %s)",
                    (usuario, password, email)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return render_template("user.html", usuario=usuario, email=email)

        cursor.close()
        conn.close()

    return render_template("login.html", mensaje=mensaje, mostrar_email=mostrar_email)







