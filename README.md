# 🎬 PeliHub

Aplicación web en **Django** de catálogo de películas: los **administradores** agregan
las películas y los **usuarios** se registran para ver el catálogo y seguir su propio
progreso de visionado (pendiente / en progreso / vista).

## Funcionalidades

- Registro e inicio de sesión (con perfil que guarda tu teléfono).
- **Catálogo compartido**: los administradores agregan, editan y eliminan películas;
  los usuarios normales solo las visualizan.
- **Estado de visionado por usuario**: cada usuario marca, sobre cada película,
  si está pendiente, en progreso o vista (independiente para cada uno).
- CRUD de películas (solo admin): título, director, año, género, sinopsis, puntuación (1–5) y portada.
- Búsqueda por título.
- Panel de administración propio (solo superusuarios) + admin de Django.
- Recuperación de contraseña por correo.
- Banner con imágenes rotativas.
- Cierre de sesión seguro (POST).

## Seguridad

- **Clave secreta fuera del código**: se lee de `.env` (no se sube a Git).
- **Anti fuerza bruta** en login con [django-axes](https://github.com/jazzband/django-axes):
  5 intentos fallidos → bloqueo de 1 hora.
- **SQL injection**: protegido por el ORM de Django (consultas parametrizadas).
- **XSS**: escapado automático de plantillas.
- **CSRF**: protección en todos los formularios.
- **Validación de contraseñas** y de `next` (evita *open redirect*).
- Cabeceras de seguridad: `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`,
  cookies `HttpOnly`/`SameSite`.
- **Producción** (con `DJANGO_DEBUG=False`): redirección a HTTPS, HSTS, cookies
  seguras y proxy SSL.

## Requisitos

- Python 3.13
- Dependencias en `requirements.txt`

## Instalación (desarrollo)

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
source venv/Scripts/activate   # Windows (bash) — Linux/macOS: source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
#   y editá .env con tu clave secreta

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear el superusuario (para el panel admin)
python manage.py createsuperuser

# 6. Levantar el servidor
python manage.py runserver
```

Abrí http://127.0.0.1:8000/ en tu navegador.

## Variables de entorno

| Variable                  | Por defecto                    | Descripción                                  |
|---------------------------|--------------------------------|----------------------------------------------|
| `DJANGO_SECRET_KEY`       | —                              | Clave secreta (obligatoria). Generá una con `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_DEBUG`            | `False`                        | `True` solo en desarrollo                    |
| `DJANGO_ALLOWED_HOSTS`    | `localhost,127.0.0.1,[::1]`    | Hosts permitidos, separados por coma         |
| `DJANGO_SECURE_SSL_REDIRECT` | `True` (en prod)            | Forzar HTTPS                                 |

## Despliegue (producción)

1. Subí el repo a GitHub **sin** `.env` ni `db.sqlite3` (ya están en `.gitignore`).
2. En tu plataforma (Render, Railway, PythonAnywhere, etc.) configurá las variables
   de entorno de arriba con `DJANGO_DEBUG=False`.
3. Recolectá los estáticos (WhiteNoise los sirve):
   ```bash
   python manage.py collectstatic --noinput
   ```
4. Ejecutá las migraciones y levantá con un servidor WSGI/ASGI (Gunicorn/Uvicorn).

> El correo de recuperación de contraseña usa el backend de consola por defecto.
> En producción configurá un SMTP real (ver `EMAIL_BACKEND` en `config/settings.py`).

## Estructura

```
Peli_Hub/
├── config/        # settings, urls, wsgi/asgi del proyecto
├── mi_app/        # app núcleo: página de inicio (landing)
├── peliculas/     # app principal: modelos, vistas, templates, estáticos
├── .env.example   # plantilla de variables de entorno
├── manage.py
└── requirements.txt
```

## Tests

```bash
python manage.py test
```
