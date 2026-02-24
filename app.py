from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_segura_123")

# --- CONEXIÓN A BASE DE DATOS ---
def conectarCampus():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# --- DECORADORES DE SEGURIDAD ---
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login_registro'))
        return f(*args, **kwargs)
    return decorated_function

def admin_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica que el rol en la sesión sea estrictamente administrador
        if session.get('rol') != 'administrador':
            return "Acceso denegado: Se requieren permisos de administrador.", 403
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS ---

@app.route("/", methods=["GET", "POST"])
def login_registro():
    if 'usuario' in session:
        return redirect(url_for('perfil'))
    
    mensaje = ""
    if request.method == "POST":
        # Capturamos los datos del formulario (deben coincidir con el name="" del HTML)
        usuario_ingresado = request.form["username"]
        password_ingresada = request.form["password"]

        conn = conectarCampus()
        cursor = conn.cursor()

        # 1. Buscamos por la columna 'nombre' que es la que usas en tu tabla
        cursor.execute("SELECT id_user, nombre, password, mail, rol FROM users WHERE nombre=%s", (usuario_ingresado,))
        resultado = cursor.fetchone()

        if resultado:
            # Desempaquetamos los 5 valores que pedimos en el SELECT
            id_user, nombre_db, hash_guardado, email_guardado, rol_guardado = resultado
            
            # 2. Verificamos la contraseña cifrada
            if check_password_hash(hash_guardado, password_ingresada):
                # Guardamos datos en la sesión
                session['usuario'] = nombre_db
                session['email'] = email_guardado
                session['rol'] = rol_guardado
                
                cursor.close()
                conn.close()
                return redirect(url_for('perfil'))
            else:
                mensaje = "Contraseña incorrecta."
        else:
            mensaje = "El usuario no existe."

        cursor.close()
        conn.close()

    return render_template("login.html", mensaje=mensaje)

@app.route("/registro", methods=["GET", "POST"])
@login_requerido
@admin_requerido # <--- Solo el admin puede ejecutar esta función
def registrar_usuario():
    mensaje = ""
    if request.method == "POST":
        nuevo_user = request.form["nuevo_user"]
        nuevo_pass = request.form["nuevo_password"]
        nuevo_email = request.form["nuevo_email"]
        nuevo_rol = request.form["nuevo_rol"]

        conn = conectarCampus()
        cursor = conn.cursor()

        try:
            # Verificar si el correo ya existe
            cursor.execute("SELECT nombre FROM users WHERE mail=%s", (nuevo_email,))
            if cursor.fetchone():
                mensaje = "Error: El correo ya está registrado."
            else:
                pass_cifrada = generate_password_hash(nuevo_pass)
                cursor.execute(
                    """
                    INSERT INTO users (nombre, password, mail, rol, creado_en, actualizado_en) 
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    (nuevo_user, pass_cifrada, nuevo_email, nuevo_rol)
                )
                conn.commit()
                mensaje = f"Éxito: Usuario '{nuevo_user}' registrado correctamente."
        except Exception as e:
            mensaje = f"Error al registrar: {e}"
        finally:
            cursor.close()
            conn.close()

    return render_template("registro_admin.html", mensaje=mensaje)

@app.route("/perfil")
@login_requerido
def perfil():
    return render_template("user.html", usuario=session.get('usuario'), email=session.get('email'), rol=session.get('rol'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_registro'))


# --- RUTA PARA VER LA LISTA ---
@app.route('/gestion_usuarios')
@login_requerido
@admin_requerido
def gestion_usuarios():
    conn = conectarCampus()
    cursor = conn.cursor()
    
    # 1. CONSULTA DE USUARIOS
    cursor.execute("SELECT id_user, nombre, mail, rol FROM users")
    cols_users = [desc[0] for desc in cursor.description]
    usuarios = [dict(zip(cols_users, row)) for row in cursor.fetchall()]
    
    # 2. CONSULTA DE ASIGNATURAS (Añade esto)
    cursor.execute("SELECT id_asig, nombre_asig FROM asignaturas")
    cols_asig = [desc[0] for desc in cursor.description]
    asignaturas = [dict(zip(cols_asig, row)) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    # Enviamos AMBAS listas al HTML
    return render_template('gestion_usuarios.html', 
                           lista_usuarios=usuarios, 
                           lista_asignaturas=asignaturas)

@app.route('/eliminar_usuario/<int:id>')
@login_requerido
@admin_requerido
def eliminar_usuario(id):
    conn = conectarCampus() 
    cursor = conn.cursor()
    # Aquí también usamos 'id_user'
    cursor.execute("DELETE FROM users WHERE id_user = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('gestion_usuarios'))

# RUTA PARA GUARDAR
@app.route('/registrar_asignatura', methods=['POST'])
def registrar_asignatura():
    nombre = request.form.get('nombre_asig')
    print(f"DEBUG: Intentando registrar asignatura: {nombre}") # Esto saldrá en tu terminal
    
    if nombre:
        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO asignaturas (nombre_asig) VALUES (%s)", (nombre,))
            conn.commit() # ¡Muy importante para guardar los cambios!
            cursor.close()
            conn.close()
            print("DEBUG: Guardado exitoso")
        except Exception as e:
            print(f"DEBUG: Error al insertar: {e}")
            
    return redirect(url_for('registrar_usuario'))

# RUTA PARA BORRAR (Usa el mismo estilo que con usuarios)
@app.route('/eliminar_asignatura/<int:id>')
def eliminar_asignatura(id):
    conn = conectarCampus()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM asignaturas WHERE id_asig = %s", (id,))
    conn.commit()
    return redirect(url_for('gestion_usuarios'))

if __name__ == "__main__":
    app.run(debug=True)






