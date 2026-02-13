from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_segura")

def conectarCampus():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login_registro'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
def login_registro():
    if 'usuario' in session:
        return redirect(url_for('perfil'))
    
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
            hash_guardado, email_guardado = resultado
            if check_password_hash(hash_guardado, password_ingresada):
                session['usuario'] = usuario
                session['email'] = email_guardado
                cursor.close()
                conn.close()
                return redirect(url_for('perfil'))
            else:
                mensaje = "Contraseña incorrecta."
        else:
            # --- CASO REGISTRO ---
            mostrar_email = True
            if not email_ingresado:
                mensaje = "El usuario no existe. Ingrese su email para registrarse."
            else:
                # NUEVA VALIDACIÓN: ¿Existe ya este email en la DB?
                cursor.execute("SELECT username FROM users WHERE user_mail=%s", (email_ingresado,))
                if cursor.fetchone():
                    mensaje = "Error: Este correo ya está registrado con otra cuenta."
                else:
                    # Cifrado de seguridad original
                    pass_cifrada = generate_password_hash(password_ingresada)
                    try:
                        cursor.execute(
                            "INSERT INTO users (nombre, password, mail, rol) VALUES (%s, %s, %s, %s)",
                            (usuario, pass_cifrada, email_ingresado)
                        )
                        conn.commit()
                        session['usuario'] = usuario
                        session['email'] = email_ingresado
                        cursor.close()
                        conn.close()
                        return redirect(url_for('perfil'))
                    except Exception as e:
                        mensaje = f"Error al registrar: {e}"

        cursor.close()
        conn.close()

    return render_template("login.html", mensaje=mensaje, mostrar_email=mostrar_email)

@app.route("/perfil")
@login_requerido
def perfil():
    return render_template("user.html", usuario=session.get('usuario'), email=session.get('email'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_registro'))

if __name__ == "__main__":
    app.run(debug=True)







