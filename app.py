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

import calendar
from datetime import datetime

@app.route("/calendario")
@login_requerido
def ver_calendario():
    id_user = session.get('id_user')
    rol = session.get('rol')
    ahora = datetime.now()
    cal = calendar.monthcalendar(ahora.year, ahora.month)
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    conn = conectarCampus()
    cursor = conn.cursor()

    # 1. Obtener Horarios
    cursor.execute("SELECT a.nombre_asig, h.dia_semana, h.hora_inicio, h.hora_fin FROM horarios h JOIN asignaturas a ON h.id_asig = a.id_asig WHERE h.id_user = %s", (id_user,))
    horarios = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    # CONVERTIR HORAS A TEXTO (Para evitar el error TypeError)
    for h in horarios:
        if h.get('hora_inicio') and hasattr(h['hora_inicio'], 'strftime'):
            h['hora_inicio'] = h['hora_inicio'].strftime('%H:%M')
        if h.get('hora_fin') and hasattr(h['hora_fin'], 'strftime'):
            h['hora_fin'] = h['hora_fin'].strftime('%H:%M')

    # 2. Obtener Eventos
    if rol == 'profesor':
        cursor.execute("SELECT e.titulo, e.fecha, a.nombre_asig FROM eventos e JOIN asignaturas a ON e.id_asig = a.id_asig WHERE e.id_profesor = %s", (id_user,))
    else:
        cursor.execute("SELECT e.titulo, e.fecha, a.nombre_asig FROM eventos e JOIN asignaturas a ON e.id_asig = a.id_asig WHERE e.id_asig IN (SELECT id_asig FROM horarios WHERE id_user = %s)", (id_user,))
    
    eventos = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    # CONVERTIR FECHAS DE EVENTOS A TEXTO (Importante para JSON)
    for ev in eventos:
        if ev.get('fecha') and hasattr(ev['fecha'], 'strftime'):
            ev['fecha_str'] = ev['fecha'].strftime('%Y-%m-%d')
            # Extraemos el día para usarlo en el HTML fácilmente
            ev['dia_num'] = ev['fecha'].day
    
    cursor.close()
    conn.close()

    return render_template("calendario.html", 
                           calendario=cal, 
                           mes_nombre=meses[ahora.month-1], 
                           mes_num=ahora.month, 
                           anio=ahora.year, 
                           horarios_alumno=horarios, 
                           eventos=eventos)

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
    rol = session.get('rol')
    email = session.get('email')
    
    conn = conectarCampus()
    cursor = conn.cursor()

    # 1. Horarios
    cursor.execute("""
        SELECT a.id_asig, a.nombre_asig, h.dia_semana, h.hora_inicio, h.hora_fin 
        FROM horarios h JOIN asignaturas a ON h.id_asig = a.id_asig 
        WHERE h.id_user = %s ORDER BY h.dia_semana, h.hora_inicio
    """, (id_usuario,))
    mis_horarios = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    # 2. Faltas (Corregido)
    cursor.execute("""
        SELECT f.fecha, a.nombre_asig, f.justificada 
        FROM faltas f JOIN asignaturas a ON f.id_asig = a.id_asig 
        WHERE f.id_user = %s
    """, (id_usuario,))
    mis_faltas = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    # 3. Notas
    if rol == 'padre':
        cursor.execute("""
            SELECT u.nombre as alumno, a.nombre_asig, n.calificacion, n.trimestre 
            FROM notas n JOIN users u ON n.id_user = u.id_user
            JOIN asignaturas a ON n.id_asig = a.id_asig WHERE u.email_tutor = %s
        """, (email,))
    else:
        cursor.execute("""
            SELECT a.nombre_asig, n.calificacion, n.trimestre 
            FROM notas n JOIN asignaturas a ON n.id_asig = a.id_asig WHERE n.id_user = %s
        """, (id_usuario,))
    mis_notas = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template("user.html", usuario=session.get('usuario'), email=email, 
                           rol=rol, horarios=mis_horarios, faltas=mis_faltas, notas=mis_notas)

@app.route("/registro", methods=["GET", "POST"])
@login_requerido
@admin_requerido
def registrar_usuario():
    mensaje = ""
    if request.method == "POST":
        # Recogemos los datos del formulario
        nombre = request.form.get("nuevo_user")
        password = request.form.get("nuevo_password")
        email = request.form.get("nuevo_email")
        rol = request.form.get("nuevo_rol")
        f_nac = request.form.get("fecha_nacimiento")
        e_tutor = request.form.get("email_tutor") or None

        conn = None
        cursor = None
        try:
            conn = conectarCampus()
            cursor = conn.cursor()
            pass_cifrada = generate_password_hash(password)
            
            # SQL Correcto para insertar
            sql = """INSERT INTO users 
                     (nombre, password, mail, rol, fecha_alta, email_tutor, fecha_nacimiento) 
                     VALUES (%s, %s, %s, %s, CURRENT_DATE, %s, %s)"""
            
            cursor.execute(sql, (nombre, pass_cifrada, email, rol, e_tutor, f_nac))
            conn.commit()
            mensaje = "✅ ¡Usuario registrado con éxito!"
        except Exception as e:
            mensaje = f"❌ Error SQL: {e}"
            print(f"DEBUG ERROR: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    return render_template("registro_admin.html", mensaje=mensaje)

@app.route('/gestion_usuarios')
@login_requerido
def gestion_usuarios():
    id_user = session.get('id_user')
    rol = session.get('rol')
    
    if rol not in ['administrador', 'profesor']:
        return "Acceso denegado", 403

    conn = conectarCampus()
    cursor = conn.cursor()

    # 1. Lista de usuarios (para tablas y desplegables)
    cursor.execute("SELECT id_user, nombre, mail, rol FROM users ORDER BY nombre ASC")
    lista_usuarios = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    # 2. Lista de asignaturas (Filtrada si es profesor)
    if rol == 'profesor':
        cursor.execute("""
            SELECT DISTINCT a.id_asig, a.nombre_asig 
            FROM asignaturas a
            JOIN horarios h ON a.id_asig = h.id_asig
            WHERE h.id_user = %s
        """, (id_user,))
    else:
        cursor.execute("SELECT id_asig, nombre_asig FROM asignaturas ORDER BY nombre_asig ASC")
    lista_asignaturas = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    # 3. Consulta de Notas (Importante: nombre AS alumno)
    query_notas = """
        SELECT n.id_nota, u.nombre AS nombre, a.nombre_asig, n.calificacion, n.trimestre 
        FROM notas n
        JOIN users u ON n.id_user = u.id_user
        JOIN asignaturas a ON n.id_asig = a.id_asig
    """
    if rol == 'profesor':
        # El profesor solo ve notas de alumnos en sus asignaturas
        query_notas = """
            SELECT n.id_nota, u.nombre AS nombre, a.nombre_asig, n.calificacion, n.trimestre 
            FROM notas n
            JOIN users u ON n.id_user = u.id_user
            JOIN asignaturas a ON n.id_asig = a.id_asig
            WHERE n.id_asig IN (SELECT id_asig FROM horarios WHERE id_user = %s)
        """
        cursor.execute(query_notas, (id_user,))
    else:
        # El administrador ve todo
        query_notas = """
            SELECT n.id_nota, u.nombre AS nombre, a.nombre_asig, n.calificacion, n.trimestre 
            FROM notas n
            JOIN users u ON n.id_user = u.id_user
            JOIN asignaturas a ON n.id_asig = a.id_asig
        """
        cursor.execute(query_notas)
        
    notas_registradas = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

    # 4. Consulta de Horarios (Importante: u.nombre AS nombre_alumno)
    query_horarios = """
        SELECT h.id_horario, u.nombre AS nombre_alumno, a.nombre_asig, h.dia_semana, h.hora_inicio, h.hora_fin 
        FROM horarios h
        JOIN users u ON h.id_user = u.id_user
        JOIN asignaturas a ON h.id_asig = a.id_asig
    """
    if rol == 'profesor':
        query_horarios += " WHERE h.id_asig IN (SELECT id_asig FROM horarios WHERE id_user = %s)"
        cursor.execute(query_horarios, (id_user,))
    else:
        cursor.execute(query_horarios)
    lista_horarios = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]

   # 5. Consulta de Faltas (CORREGIDO: añadimos f.justificada)
    query_faltas = """
        SELECT f.id_falta, u.nombre AS alumno, a.nombre_asig, f.fecha, f.justificada 
        FROM faltas f
        JOIN users u ON f.id_user = u.id_user
        JOIN asignaturas a ON f.id_asig = a.id_asig
    """
    if rol == 'profesor':
        query_faltas += " WHERE f.id_asig IN (SELECT id_asig FROM horarios WHERE id_user = %s)"
        cursor.execute(query_faltas, (id_user,))
    else:
        cursor.execute(query_faltas)
    lista_faltas = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return render_template('gestion_usuarios.html', 
                           lista_usuarios=lista_usuarios, 
                           lista_asignaturas=lista_asignaturas, 
                           lista_horarios=lista_horarios,
                           notas_registradas=notas_registradas,
                           lista_faltas=lista_faltas)

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

@app.route('/registrar_nota', methods=['POST'])
@login_requerido
@admin_requerido
def registrar_nota():
    id_user = request.form.get('id_user')
    id_asig = request.form.get('id_asig')
    nota = request.form.get('calificacion')
    trimestre = request.form.get('trimestre')

    conn = conectarCampus()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO notas (id_user, id_asig, calificacion, trimestre) 
            VALUES (%s, %s, %s, %s)
        """, (id_user, id_asig, nota, trimestre))
        conn.commit()
    except Exception as e:
        print(f"Error al poner nota: {e}")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('gestion_usuarios'))

@app.route('/registrar_falta', methods=['POST'])
@login_requerido
@admin_requerido
def registrar_falta():
    id_user = request.form.get('id_user')
    id_asig = request.form.get('id_asig')
    fecha = request.form.get('fecha_falta')
    hora = request.form.get('hora_falta')
    conn = conectarCampus()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faltas (id_user, id_asig, fecha, hora) VALUES (%s, %s, %s, %s)", (id_user, id_asig, fecha, hora))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('gestion_usuarios'))

@app.route('/justificar_falta/<int:id>')
@login_requerido
@admin_requerido
def justificar_falta(id):
    conn = conectarCampus()
    cursor = conn.cursor()
    # Aquí es donde ocurre la magia: cambiamos 'justificada' a True
    cursor.execute("UPDATE faltas SET justificada = True WHERE id_falta = %s", (id,))
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

@app.route('/eliminar_nota/<int:id>')
@login_requerido
@admin_requerido
def eliminar_nota(id):
    conn = conectarCampus()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notas WHERE id_nota = %s", (id,))
    conn.commit()
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

@app.route('/crear_evento', methods=['POST'])
@login_requerido
def crear_evento():
    if session.get('rol') != 'profesor': return "No autorizado", 403
    id_asig = request.form.get('id_asig')
    titulo = request.form.get('titulo')
    fecha = request.form.get('fecha')
    id_profesor = session.get('id_user')

    conn = conectarCampus()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO eventos (id_asig, titulo, fecha, id_profesor) VALUES (%s, %s, %s, %s)",
                   (id_asig, titulo, fecha, id_profesor))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('perfil'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_registro'))

@app.route('/eliminar_falta/<int:id>')
@login_requerido
@admin_requerido
def eliminar_falta(id):
    conn = conectarCampus()
    cursor = conn.cursor()
    
    # Borramos la falta usando su ID único
    cursor.execute("DELETE FROM faltas WHERE id_falta = %s", (id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Volvemos a la gestión de usuarios para ver que ha desaparecido
    return redirect(url_for('gestion_usuarios'))

if __name__ == "__main__":
    app.run(debug=True)








