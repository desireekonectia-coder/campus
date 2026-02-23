from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_segura_123")

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
        rol_ingresado = "administrador" if request.form.get("rol") == "admin" else request.form.get("rol")

        conn = conectarCampus()
        cursor = conn.cursor()

        # 1. Buscar si el usuario existe
        cursor.execute("SELECT password, mail FROM users WHERE nombre=%s", (usuario,))
        resultado = resultado = cursor.fetchone()

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
                mensaje = "El usuario no existe. Ingrese sus datos para registrarse."
            else:
                cursor.execute("SELECT nombre FROM users WHERE mail=%s", (email_ingresado,))
                if cursor.fetchone():
                    mensaje = "Error: Este correo ya está registrado."
                else:
                    pass_cifrada = generate_password_hash(password_ingresada)
                    try:
                        # INSERT actualizado con las 2 nuevas columnas
                        cursor.execute(
                            """
                            INSERT INTO users (nombre, password, mail, rol, creado_en, actualizado_en) 
                            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            """,
                            (usuario, pass_cifrada, email_ingresado, rol_ingresado)
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

@app.route("/app-admin")
def perfil_admin():
    return render_template(url_for("admin.html"))

if __name__ == "__main__":
    app.run(debug=True)







