# Campus - Proyecto de Formación

## 📚 Descripción

**Campus** es un proyecto de formación que demuestra el desarrollo de una aplicación web completa con autenticación de usuarios y gestión de perfiles. El proyecto integra tecnologías modernas de frontend y backend para crear una experiencia de aprendizaje práctica.

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

```bash
git clone <URL_DEL_REPOSITORIO>
cd campus
```

### 2. Crear un Entorno Virtual

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

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

#### Paso 4.2: Crear la Tabla de Usuarios

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_mail VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Paso 4.3: Verificar la Tabla

```sql
-- Ver las tablas creadas
\dt

-- Ver la estructura de la tabla users
\d users
```

### 5. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```plaintext
# Configuración de Base de Datos
DB_HOST=localhost
DB_NAME=campus
DB_USER=postgres
DB_PASSWORD=tu_contraseña_aqui

# Configuración de Flask
SECRET_KEY=tu_clave_secreta_muy_segura_cambiar_en_produccion
FLASK_ENV=development
```

> ⚠️ **Importante:** Reemplaza los valores con tus credenciales reales. Nunca subas el archivo `.env` a control de versiones.

### 6. Ejecutar la Aplicación

```bash
python hello.py
```

La aplicación estará disponible en: `http://localhost:5000`

---

## 📁 Estructura del Proyecto

```
campus/
├── hello.py                 # Aplicación principal Flask
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
```

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

## 📝 Licencia

Este proyecto se encuentra bajo la licencia especificada en [LICENSE.md](LICENSE.md).

---

## 👤 Autor

Proyecto de formación desarrollado para propósitos educativos.

---

## 💡 Próximos Pasos

Para extender este proyecto puedes:

- Agregar más funcionalidades al perfil de usuario
- Implementar recuperación de contraseña por email
- Crear panel de administración
- Agregar validación de formularios en cliente y servidor
- Implementar tests unitarios
