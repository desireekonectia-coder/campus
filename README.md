# Campus - Proyecto de Formación

# Enlace a github

https://github.com/desireekonectia-coder/campus

# Enlace a railway

secure-heart-production.up.railway.app

Este proyecto está desplegado en Railway y gestiona un sistema académico completo.


## ⚙️ Configuración del Servidor
- **Python:** 3.12 (definido en runtime.txt)
- **Servidor:** Gunicorn (definido en Procfile)

## 📚 Descripción

**Campus**  es una plataforma educativa integral que permite la gestión de la vida académica en tiempo real. Este proyecto demuestra el desarrollo de una aplicación web completa, desde la autenticación segura hasta la visualización dinámica de datos escolares para alumnos, padres y profesores.
🌟 Funcionalidades Principales
•	Gestión de Usuarios: Autenticación segura con hash de contraseñas.
•	Panel de Control Personalizado: Vista de horarios, faltas y notas según el rol.
•	Calendario Dinámico: Visualización de clases semanales y eventos especiales.
•	Sistema de Eventos (Nuevo): Los profesores pueden publicar exámenes o avisos que aparecen automáticamente en el calendario de sus alumnos.

---

## 🛠️ Tecnologías Utilizadas

- **Frontend:**
  - HTML5
  - CSS3
  - JavaScript (Vanilla)

- **Backend:**
  - Python 3.x
  - Flask (Framework web)
  - PostgreSQL (Base de datos)

- **Autenticación y Seguridad:**
  - Werkzeug (Hash de contraseñas)
  - Sessions (Gestión de sesiones)

- **Configuración:**
  - python-dotenv (Variables de entorno)

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Git
- pip (gestor de paquetes de Python)

---

## 🚀 Guía de Instalación Paso a Paso

### 1. Clonar el Repositorio

bash
git clone <URL_DEL_REPOSITORIO>
cd campus


### 2. Crear un Entorno Virtual

# Crear entorno virtual en powershell
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\Activate
```

### 3. Instalar Dependencias

pip install -r requirements.txt

si no se puede

python -m pip install -r requirements.txt

si tienes instaladas versiones recientes:

py -m pip install -r requirements.txt


### 4. Configurar Base de Datos PostgreSQL

#### Paso 4.1: Crear la Base de Datos

Abre **pgAdmin** o la línea de comandos de PostgreSQL:

```sql
-- Conectarse a PostgreSQL como superusuario
psql -U postgres

-- Crear la base de datos
CREATE DATABASE campus;

-- Conectarse a la nueva base de datos
\c campus
```

#### Paso 4.2: Crear las Tablas 


CREATE TABLE users (id_user SERIAL PRIMARY KEY, nombre VARCHAR(100) NOT NULL, email VARCHAR(100) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, rol VARCHAR(20) NOT NULL, email_tutor VARCHAR(100));

CREATE TABLE asignaturas (id_asig SERIAL PRIMARY KEY, nombre_asig TEXT NOT NULL);

CREATE TABLE horarios (id_horario SERIAL PRIMARY KEY, id_asig INTEGER REFERENCES asignaturas(id_asig) ON DELETE CASCADE, dia_semana TEXT NOT NULL, hora_inicio TIME NOT NULL, hora_fin TIME NOT NULL);

CREATE TABLE faltas (id_falta SERIAL PRIMARY KEY, id_user INTEGER REFERENCES users(id_user) ON DELETE CASCADE, id_asig INTEGER REFERENCES asignaturas(id_asig) ON DELETE CASCADE, fecha DATE DEFAULT CURRENT_DATE, justificada BOOLEAN DEFAULT FALSE);

CREATE TABLE nоtas (id_nota SERIAL PRIMARY KEY, id_user INTEGER NOT NULL, id_asig INTEGER NOT NULL, calificacion DECIMAL(4,2) CHECK (calificacion >= 0 AND calificacion <= 10), trimestre VARCHAR(20), fecha_registro DATE DEFAULT CURRENT_DATE, CONSTRAINT fk_usuario FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE, CONSTRAINT fk_asignatura FOREIGN KEY (id_asig) REFERENCES asignaturas(id_asig) ON DELETE CASCADE);

CREATE TABLE eventos (id_evento SERIAL PRIMARY KEY, id_asig INTEGER REFERENCES asignaturas(id_asig), titulo VARCHAR(100), fecha DATE, id_profesor INTEGER REFERENCES users(id_user));


### 5. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:


# Variables de entorno .env
DB_HOST=localhost
DB_NAME=campus
DB_USER=postgres
DB_PASSWORD=tu_contraseña_aqui

# Configuración de Flask
SECRET_KEY=tu_clave_secreta_muy_segura_cambiar_en_produccion
FLASK_ENV=development


> ⚠️ **Importante:** Reemplaza los valores con tus credenciales reales. Nunca subas el archivo `.env` a control de versiones.

### 6. Ejecutar la Aplicación


flask --app app run


La aplicación estará disponible en: http://127.0.0.1:5000

---

## 📁 Estructura del Proyecto

```
campus/
├── app.py                 # Aplicación principal Flask
├── requirements.txt         # Dependencias del proyecto
├── README.md               # Este archivo
├── LICENSE.md              # Licencia del proyecto
├── .env                    # Variables de entorno (no incluir en Git)
├── .venv/                  # Entorno virtual
├── static/
│   ├── css/
│   │   └── style.css       # Estilos CSS
│   ├── js/
│   │   └── main.js         # JavaScript del cliente
│   └── images/             # Imágenes del proyecto
└── templates/
    ├── base.html           # Plantilla base
    ├── login.html          # Página de login/registro
    └── user.html           # Página de perfil del usuario


---

## 🔧 Solución de Problemas

### Error: "psycopg2: can't adapt type 'DictRow'"
Asegúrate de que PostgreSQL está en ejecución y que las credenciales en `.env` son correctas.

### Error: "ModuleNotFoundError: No module named 'flask'"
Verifica que has activado el entorno virtual y has ejecutado `pip install -r requirements.txt`.

### Error de conexión a Base de Datos
- Comprueba que PostgreSQL está corriendo
- Verifica las credenciales en el archivo `.env`
- Asegúrate de que la base de datos `campus` existe

---

# Nuevas Funcionalidades 
1. Borrado de Faltas (Solo Administrador)
El administrador ahora tiene un "borrador" para corregir errores humanos.
•	Botón 🗑️: Disponible en la tabla de Gestión de Asistencia.
•	Confirmación: El sistema pregunta antes de borrar para evitar clics accidentales.
•	Ejemplo: Si pones una falta a "Ruben" por error, ahora puedes eliminarla completamente en lugar de solo justificarla.


## 📝 Licencia

Este proyecto se encuentra bajo la licencia especificada en [LICENSE.md](LICENSE.md).

---

## 👤 Autor

Proyecto de formación desarrollado para propósitos educativos.

---

