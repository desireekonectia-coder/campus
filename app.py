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

def admin_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Usamos 'rol_usuario' que es como aparece en tu imagen
        if session.get('rol') != 'administrador':
            return "Acceso denegado: Se requieren permisos de administrador.", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
def login_registro():
    if 'usuario' in session:
        return redirect(url_for('perfil'))
    
    mensaje = ""
    if request.method == "POST":
        usuario_ingresado = request.form["username"]
        password_ingresada = request.form["password"]

        conn = conectarCampus()
        cursor = conn.cursor()
        # Volvemos a usar 'rol' porque 'rol_usuario' no existe según el error
        cursor.execute("SELECT id_user, nombre, password, mail, rol FROM users WHERE nombre=%s", (usuario_ingresado,))
        resultado = resultado = cursor.fetchone()

        if resultado:
            id_user, nombre_db, hash_guardado, email_guardado, rol_guardado = resultado
            if check_password_hash(hash_guardado, password_ingresada):
                session['usuario'] = nombre_db
                session['email'] = email_guardado
                session['rol'] = rol_guardado
                session['id_user'] = id_user
                
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

@app.route("/perfil")
@login_requerido
def perfil():
    id_usuario = session.get('id_user')
    conn = conectarCampus()
    cursor = conn.cursor()

    # Consultamos solo los horarios y asignaturas de este alumno
    cursor.execute("""
        SELECT a.nombre_asig, h.dia_semana, h.hora_inicio, h.hora_fin 
        FROM horarios h 
        JOIN asignaturas a ON h.id_asig = a.id_asig 
        WHERE h.id_user = %s
        ORDER BY h.dia_semana, h.hora_inicio
    """, (id_usuario,))
    
    # Convertimos los resultados en una lista de diccionarios
    mis_horarios = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template("user.html", 
                           usuario=session.get('usuario'), 
                           email=session.get('email'), 
                           rol=session.get('rol'),
                           horarios=mis_horarios)

@app.route("/registro", methods=["GET", "POST"])
@login_requerido
@admin_requerido
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
            pass_cifrada = generate_password_hash(nuevo_pass)
            # Insertamos en 'rol_usuario'
            cursor.execute(
                "INSERT INTO users (nombre, password, mail, rol_usuario) VALUES (%s, %s, %s, %s)",
                (nuevo_user, pass_cifrada, nuevo_email, nuevo_rol)
            )
            conn.commit()
            mensaje = f"Éxito: Usuario '{nuevo_user}' registrado."
        except Exception as e:
            mensaje = f"Error: {e}"
        finally:
            cursor.close()
            conn.close()

    return render_template("registro_admin.html", mensaje=mensaje)

@app.route('/gestion_usuarios')
@login_requerido
@admin_requerido
def gestion_usuarios():
    conn = conectarCampus()
    cursor = conn.cursor()
    
    # 1. Usuarios (Usando 'rol')
    cursor.execute("SELECT id_user, nombre, mail, rol FROM users")
    usuarios = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
    
    # 2. Asignaturas
    cursor.execute("SELECT id_asig, nombre_asig FROM asignaturas")
    asignaturas = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
    
    # 3. Horarios 
    # ¡RECUERDA! Debes haber ejecutado: ALTER TABLE horarios ADD COLUMN id_user INTEGER;
    cursor.execute("""
        SELECT h.id_horario, u.nombre as nombre_alumno, a.nombre_asig, h.dia_semana, h.hora_inicio, h.hora_fin 
        FROM horarios h 
        JOIN asignaturas a ON h.id_asig = a.id_asig
        JOIN users u ON h.id_user = u.id_user
        ORDER BY h.dia_semana, h.hora_inicio
    """)
    horarios = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    return render_template('gestion_usuarios.html', 
                           lista_usuarios=usuarios, 
                           lista_asignaturas=asignaturas, 
                           lista_horarios=horarios)

@app.route('/asignar_horario', methods=['POST'])
@login_requerido
@admin_requerido
def asignar_horario():
    id_user = request.form.get('id_user')
    id_asig = request.form.get('id_asig')
    dia = request.form.get('dia_semana')
    inicio = request.form.get('hora_inicio')
    fin = request.form.get('hora_fin')

    conn = conectarCampus()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO horarios (id_user, id_asig, dia_semana, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s, %s)",
                   (id_user, id_asig, dia, inicio, fin))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('gestion_usuarios'))

# Ruta necesaria para que no de BuildError en registro_admin.html
@app.route('/registrar_asignatura', methods=['POST'])
@login_requerido
@admin_requerido
def registrar_asignatura():
    nombre = request.form.get('nombre_asig')
    if nombre:
        conn = conectarCampus()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO asignaturas (nombre_asig) VALUES (%s)", (nombre,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('gestion_usuarios'))

@app.route('/eliminar_usuario/<int:id>')
@login_requerido
@admin_requerido
def eliminar_usuario(id):
    conn = conectarCampus()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id_user = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('gestion_usuarios'))

@app.route('/eliminar_asignatura/<int:id>')
@login_requerido
@admin_requerido
def eliminar_asignatura(id):
    try:
        conn = conectarCampus()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM asignaturas WHERE id_asig = %s", (id,))
        conn.commit()
    except Exception as e:
        print(f"Error al eliminar asignatura: {e}")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('gestion_usuarios'))

@app.route('/eliminar_horario/<int:id>')
@login_requerido
@admin_requerido
def eliminar_horario(id):
    conn = conectarCampus()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM horarios WHERE id_horario = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('gestion_usuarios'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_registro'))

if __name__ == "__main__":
    app.run(debug=True)








