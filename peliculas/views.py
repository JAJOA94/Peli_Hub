from urllib import request

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CalificacionForm, PeliculaForm, RegistroForm
from .models import Calificacion, EstadoPelicula, HistorialVisualizacion, ListaPersonalizada, Pelicula


def _redireccion_segura(request, por_defecto):
    """Valida un parámetro `next` y evita open redirects."""
    siguiente = request.POST.get('next') or request.GET.get('next')
    if siguiente and url_has_allowed_host_and_scheme(
        siguiente, allowed_hosts={request.get_host()}
    ):
        return redirect(siguiente)
    return redirect(por_defecto)


@login_required
def lista_peliculas(request):
    """Catálogo compartido: todos ven todas las películas disponibles."""
    try:
        busqueda = request.GET.get('buscar', '').strip()
        peliculas = Pelicula.objects.all()
        
        if busqueda:
            peliculas = peliculas.filter(titulo__icontains=busqueda)
        peliculas = list(peliculas)

        ESTADO_DISPLAY = {
            'pendiente': 'Pendiente',
            'progreso': 'En progreso',
            'vista': 'Vista',
        }
        
        if not request.user.is_superuser:
            estados = {
                e.pelicula_id: e.estado
                for e in EstadoPelicula.objects.filter(usuario=request.user)
            }
            for p in peliculas:
                estado = estados.get(p.id, 'pendiente')
                p.estado_usuario = estado
                p.estado_usuario_display = ESTADO_DISPLAY[estado]

        return render(request, 'peliculas/lista.html', {
            'peliculas': peliculas,
            'busqueda': busqueda,
        })
    except Exception as e:
        messages.error(request, 'Error de conexión al cargar el catálogo de películas.')
        return render(request, 'peliculas/lista.html', {'peliculas': [], 'busqueda': ''})


@login_required
def crear_pelicula(request):
    if not request.user.is_superuser:
        messages.error(request, 'Solo los administradores pueden agregar películas.')
        return redirect('lista_peliculas')

    if request.method == 'POST':
        form = PeliculaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pelicula = form.save()
                messages.success(request, f'Película "{pelicula.titulo}" agregada al catálogo.')
                return redirect('lista_peliculas')
            except Exception as e:
                messages.error(request, 'Error en la base de datos al intentar guardar la película.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = PeliculaForm()

    return render(request, 'peliculas/formulario.html', {'form': form})


@login_required
def editar_pelicula(request, id):
    if not request.user.is_superuser:
        messages.error(request, 'Solo los administradores pueden editar películas.')
        return redirect('lista_peliculas')

    pelicula = get_object_or_404(Pelicula, id=id)

    if request.method == 'POST':
        form = PeliculaForm(request.POST, request.FILES, instance=pelicula)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Película actualizada correctamente.')
                return redirect('lista_peliculas')
            except Exception as e:
                messages.error(request, 'Error al actualizar la película en la base de datos.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = PeliculaForm(instance=pelicula)

    return render(request, 'peliculas/formulario.html', {'form': form})


@login_required
def eliminar_pelicula(request, id):
    if not request.user.is_superuser:
        messages.error(request, 'Solo los administradores pueden eliminar películas.')
        return redirect('lista_peliculas')

    pelicula = get_object_or_404(Pelicula, id=id)

    if request.method == 'POST':
        try:
            pelicula.delete()
            messages.success(request, 'Película eliminada de forma exitosa.')
        except Exception as e:
            messages.error(request, 'Ocurrió un error al intentar eliminar la película.')
        return redirect('lista_peliculas')

    return render(request, 'peliculas/confirmar_eliminar.html', {'pelicula': pelicula})


@login_required
def ver_pelicula(request, id):
    """El usuario pulsa 'Ver película' -> pasa automáticamente a 'en progreso'."""
    if request.user.is_superuser:
        messages.error(request, 'El estado de visionado es propio de cada usuario.')
        return redirect('lista_peliculas')

    pelicula = get_object_or_404(Pelicula, id=id)

    try:
        actual = EstadoPelicula.objects.filter(
            usuario=request.user, pelicula=pelicula
        ).first()

        if not actual or actual.estado != 'vista':
            EstadoPelicula.objects.update_or_create(
                usuario=request.user,
                pelicula=pelicula,
                defaults={'estado': 'progreso'},
            )

        HistorialVisualizacion.objects.update_or_create(
            usuario=request.user,
            pelicula=pelicula,
            defaults={'progreso': 1, 'duracion_vista': 0},
        )
    except Exception as e:
        messages.error(request, 'Error de conexión al registrar tu avance.')
        return redirect('lista_peliculas')

    calificacion_usuario = Calificacion.objects.filter(
        usuario=request.user, pelicula=pelicula
    ).first()
    form_calificacion = CalificacionForm(instance=calificacion_usuario)

    return render(request, 'peliculas/ver.html', {
        'pelicula': pelicula,
        'form_calificacion': form_calificacion,
        'calificacion_usuario': calificacion_usuario,
    })


@login_required
@require_POST
def terminar_pelicula(request, id):
    """El usuario termina de ver la película -> pasa automáticamente a 'vista'."""
    if request.user.is_superuser:
        messages.error(request, 'El estado de visionado es propio de cada usuario.')
        return redirect('lista_peliculas')

    pelicula = get_object_or_404(Pelicula, id=id)
    
    try:
        EstadoPelicula.objects.update_or_create(
            usuario=request.user,
            pelicula=pelicula,
            defaults={'estado': 'vista'},
        )
        messages.success(request, f'Marcaste "{pelicula.titulo}" como vista.')
    except Exception as e:
        messages.error(request, 'Error en el servidor al intentar actualizar el estado.')
        
    return redirect('lista_peliculas')

@login_required
@require_POST
def calificar_pelicula(request, id):
    """Usuario deja/actualiza su calificación (1-5) y comentario; recalcula el promedio."""
    if request.user.is_superuser:
        messages.error(request, 'Las calificaciones son propias de cada usuario.')
        return redirect('lista_peliculas')

    pelicula = get_object_or_404(Pelicula, id=id)
    instancia = Calificacion.objects.filter(usuario=request.user, pelicula=pelicula).first()
    form = CalificacionForm(request.POST, instance=instancia)

    if form.is_valid():
        try:
            calificacion = form.save(commit=False)
            calificacion.usuario = request.user
            calificacion.pelicula = pelicula
            calificacion.save()
            pelicula.recalcular_promedio()
            messages.success(request, '¡Gracias por tu calificación!')
        except Exception as e:
            messages.error(request, 'Error en la base de datos al guardar tu calificación.')
    else:
        messages.error(request, 'Revisa tu calificación: debe ser un puntaje entre 1 y 5.')

    return redirect('ver_pelicula', id=pelicula.id)


@login_required
def historial_visualizacion(request):
    historial = HistorialVisualizacion.objects.filter(
        usuario=request.user
    ).select_related('pelicula').order_by('-fecha_visualizacion')
    return render(request, 'peliculas/historial.html', {'historial': historial})


@login_required
def listas_personalizadas(request):
    listas = ListaPersonalizada.objects.filter(
        usuario=request.user
    ).prefetch_related('peliculas').order_by('-fecha_creacion')
    return render(request, 'peliculas/listas.html', {'listas': listas})


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('lista_peliculas')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return _redireccion_segura(request, 'lista_peliculas')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()

    return render(request, 'peliculas/login.html', {'form': form})


def registrarse(request):
    if request.user.is_authenticated:
        return redirect('lista_peliculas')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save()
                login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, '¡Cuenta creada! Bienvenido a PeliHub.')
                return redirect('lista_peliculas')
            except Exception as e:
                messages.error(request, 'Error en el servidor al intentar crear la cuenta.')
        else:
            messages.error(request, 'Revisa los errores en el formulario para poder continuar.')
    else:
        form = RegistroForm()

    return render(request, 'peliculas/registro.html', {'form': form})


@user_passes_test(lambda user: user.is_superuser)
def panel_admin(request):
    User = get_user_model()
    return render(request, 'peliculas/panel_admin.html', {
        'peliculas_count': Pelicula.objects.count(),
        'usuarios': User.objects.order_by('username'),
    })


@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')