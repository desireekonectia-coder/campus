from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

#Cargar variables de entorno desde archivo .env
load_dotenv()

app = Flask(__name__)

# Configuración de la conexión
def conectarCampus():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@app.route("/", methods=["GET", "POST"])
def login_registro():
    mensaje = ""
    mostrar_email = False

    if request.method == "POST":
        usuario = request.form["user"]
        password_ingresada = request.form["password"]
        email_ingresado = request.form.get("email")

        conn = conectarCampus()
        cursor = conn.cursor()

        # 1. Buscar si el usuario existe
        cursor.execute("SELECT password, user_mail FROM users WHERE username=%s", (usuario,))
        resultado = cursor.fetchone()

        if resultado:
            # --- CASO LOGIN ---
            hash_guardado = resultado[0]
            email_guardado = resultado[1]
            
            # Verificamos si la contraseña coincide con el hash
            if check_password_hash(hash_guardado, password_ingresada):
                cursor.close()
                conn.close()
                return render_template("user.html", usuario=usuario, email=email_guardado)
            else:
                mensaje = "Contraseña incorrecta. Intente de nuevo."
        else:
            # --- CASO REGISTRO ---
            mostrar_email = True
            if not email_ingresado:
                mensaje = "El usuario no existe. Ingrese su email para registrarse."
            else:
                # Ciframos la contraseña antes de guardarla
                pass_cifrada = generate_password_hash(password_ingresada)
                try:
                    cursor.execute(
                        "INSERT INTO users (username, password, user_mail) VALUES (%s, %s, %s)",
                        (usuario, pass_cifrada, email_ingresado)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return render_template("user.html", usuario=usuario, email=email_ingresado)
                except Exception as e:
                    mensaje = f"Error al registrar: {e}"

        cursor.close()
        conn.close()

    return render_template("login.html", mensaje=mensaje, mostrar_email=mostrar_email)

if __name__ == "__main__":
    app.run(debug=True)







