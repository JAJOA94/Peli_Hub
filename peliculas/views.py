from urllib import request
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CalificacionForm, PerfilForm, PeliculaForm, RegistroForm, UsuarioPerfilForm
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
        busqueda = request.GET.get('q', request.GET.get('buscar', '')).strip()
        genero = request.GET.get('genero', '').strip()
        anio = request.GET.get('anio', '').strip()
        anio_invalido = bool(anio and not anio.isdigit())
        peliculas = Pelicula.objects.all()

        if busqueda:
            peliculas = peliculas.filter(
                Q(titulo__icontains=busqueda)
                | Q(director__icontains=busqueda)
                | Q(sinopsis__icontains=busqueda)
            )
        generos_validos = {codigo for codigo, _ in Pelicula.GENEROS}
        if genero in generos_validos:
            peliculas = peliculas.filter(genero=genero)
        elif genero:
            genero = ''
        if anio and not anio_invalido:
            peliculas = peliculas.filter(anio_estreno=int(anio))
        peliculas = list(peliculas)

        peliculas_destacadas = list(
            Pelicula.objects.filter(
                mostrar_en_banner=True,
                portada__isnull=False,
            )
            .exclude(portada='')
            .order_by('-calificacion_promedio', '-visualizaciones', '-anio_estreno')[:5]
        )

        ESTADO_DISPLAY = {
            'pendiente': 'Pendiente',
            'progreso': 'En progreso',
            'vista': 'Vista',
        }
        
        peliculas_por_genero = []
        for codigo, nombre in Pelicula.GENEROS:
            peliculas_genero = [p for p in peliculas if p.genero == codigo]
            if peliculas_genero:
                peliculas_por_genero.append({
                    'codigo': codigo,
                    'nombre': nombre,
                    'peliculas': peliculas_genero,
                })

        peliculas_en_mi_lista = set()
        if not request.user.is_superuser:
            estados = {
                e.pelicula_id: e.estado
                for e in EstadoPelicula.objects.filter(usuario=request.user)
            }
            peliculas_en_mi_lista = set(
                ListaPersonalizada.objects.filter(
                    usuario=request.user, nombre='Mi lista'
                ).values_list('peliculas__id', flat=True)
            )
            for p in peliculas:
                estado = estados.get(p.id, 'pendiente')
                p.estado_usuario = estado
                p.estado_usuario_display = ESTADO_DISPLAY[estado]

        ahora = timezone.localtime()
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if inicio_mes.month == 12:
            inicio_mes_siguiente = inicio_mes.replace(year=inicio_mes.year + 1, month=1)
        else:
            inicio_mes_siguiente = inicio_mes.replace(month=inicio_mes.month + 1)

        top_historico = Pelicula.objects.filter(
            total_calificaciones__gt=0
        ).order_by('-calificacion_promedio', '-total_calificaciones', 'titulo')[:10]
        puntuaciones_mes = list(
            Calificacion.objects.filter(
                fecha__gte=inicio_mes,
                fecha__lt=inicio_mes_siguiente,
            )
            .values('pelicula_id')
            .annotate(promedio_mes=Avg('puntuacion'), votos_mes=Count('id'))
            .order_by('-promedio_mes', '-votos_mes', 'pelicula_id')[:10]
        )
        peliculas_mes = Pelicula.objects.in_bulk(
            fila['pelicula_id'] for fila in puntuaciones_mes
        )
        top_mensual = []
        for fila in puntuaciones_mes:
            pelicula = peliculas_mes.get(fila['pelicula_id'])
            if pelicula:
                pelicula.promedio_mes = round(fila['promedio_mes'], 2)
                pelicula.votos_mes = fila['votos_mes']
                top_mensual.append(pelicula)

        return render(request, 'peliculas/lista.html', {
            'peliculas': peliculas,
            'peliculas_por_genero': peliculas_por_genero,
            'peliculas_en_mi_lista': peliculas_en_mi_lista,
            'busqueda': busqueda,
            'genero_seleccionado': genero,
            'anio': anio if not anio_invalido else '',
            'anio_invalido': anio_invalido,
            'generos': Pelicula.GENEROS,
            'top_historico': top_historico,
            'top_mensual': top_mensual,
            'peliculas_destacadas': peliculas_destacadas,
            'pelicula_destacada': peliculas_destacadas[0] if peliculas_destacadas else None,
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
    """Muestra el detalle sin cambiar el estado hasta que el usuario pulse Ver."""
    pelicula = get_object_or_404(Pelicula, id=id)
    calificacion_usuario = None
    form_calificacion = None
    en_mi_lista = False
    estado_usuario = None
    if not request.user.is_superuser:
        calificacion_usuario = Calificacion.objects.filter(
            usuario=request.user, pelicula=pelicula
        ).first()
        form_calificacion = CalificacionForm(instance=calificacion_usuario)
        en_mi_lista = ListaPersonalizada.objects.filter(
            usuario=request.user,
            nombre='Mi lista',
            peliculas=pelicula,
        ).exists()
        estado_usuario = EstadoPelicula.objects.filter(
            usuario=request.user, pelicula=pelicula
        ).values_list('estado', flat=True).first() or 'pendiente'

    peliculas_por_director = list(
        Pelicula.objects.filter(director__iexact=pelicula.director)
        .exclude(pk=pelicula.pk)
        .order_by('-calificacion_promedio', '-total_calificaciones', 'titulo')[:5]
    )
    peliculas_similares = Pelicula.objects.filter(genero=pelicula.genero).exclude(
        pk=pelicula.pk
    ).exclude(
        pk__in=[recomendada.pk for recomendada in peliculas_por_director]
    ).order_by('-calificacion_promedio', '-total_calificaciones', 'titulo')[:5]

    return render(request, 'peliculas/ver.html', {
        'pelicula': pelicula,
        'form_calificacion': form_calificacion,
        'calificacion_usuario': calificacion_usuario,
        'en_mi_lista': en_mi_lista,
        'estado_usuario': estado_usuario,
        'peliculas_por_director': peliculas_por_director,
        'peliculas_similares': peliculas_similares,
    })


@login_required
@require_POST
def iniciar_visualizacion(request, id):
    if request.user.is_superuser:
        messages.error(request, 'El estado de visionado es propio de cada usuario.')
        return redirect('lista_peliculas')

    pelicula = get_object_or_404(Pelicula, id=id)
    try:
        estado, creado = EstadoPelicula.objects.get_or_create(
            usuario=request.user,
            pelicula=pelicula,
            defaults={'estado': 'progreso'},
        )
        if not creado and estado.estado != 'vista':
            estado.estado = 'progreso'
            estado.save(update_fields=['estado', 'actualizado'])
        HistorialVisualizacion.objects.update_or_create(
            usuario=request.user,
            pelicula=pelicula,
            defaults={'progreso': 1, 'duracion_vista': 0},
        )
        pelicula.registrar_visualizacion()
        messages.success(request, f'Comenzaste a ver "{pelicula.titulo}".')
    except Exception:
        messages.error(request, 'No se pudo registrar el inicio de la visualización.')
    return redirect('ver_pelicula', id=pelicula.id)


@login_required
@require_POST
def agregar_a_mi_lista(request, id):
    if request.user.is_superuser:
        messages.error(request, 'Las listas personales son para cuentas de usuario.')
        return redirect('lista_peliculas')

    pelicula = get_object_or_404(Pelicula, id=id)
    lista, _ = ListaPersonalizada.objects.get_or_create(
        usuario=request.user,
        nombre='Mi lista',
        defaults={'es_privada': True},
    )
    lista.peliculas.add(pelicula)
    messages.success(request, f'"{pelicula.titulo}" se agregó a Mi lista.')
    return _redireccion_segura(request, 'lista_peliculas')


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


@login_required
def perfil_usuario(request):
    perfil = getattr(request.user, 'perfil', None)
    if request.method == 'POST':
        usuario_form = UsuarioPerfilForm(request.POST, instance=request.user)
        perfil_form = PerfilForm(request.POST, instance=perfil)
        if usuario_form.is_valid() and perfil_form.is_valid():
            with transaction.atomic():
                usuario_form.save()
                perfil_actualizado = perfil_form.save(commit=False)
                perfil_actualizado.usuario = request.user
                perfil_actualizado.save()
            messages.success(request, 'Tu perfil se actualizó correctamente.')
            return redirect('perfil_usuario')
        messages.error(request, 'Revisa los datos del formulario.')
    else:
        usuario_form = UsuarioPerfilForm(instance=request.user)
        perfil_form = PerfilForm(instance=perfil)

    return render(request, 'peliculas/perfil.html', {
        'usuario_form': usuario_form,
        'perfil_form': perfil_form,
    })


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


@login_required
@user_passes_test(
    lambda user: user.is_superuser,
    login_url='lista_peliculas',
    redirect_field_name=None,
)
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