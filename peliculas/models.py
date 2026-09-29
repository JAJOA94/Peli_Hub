from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Director(models.Model):
    """Persona responsable de la dirección de una película."""

    nombre = models.CharField(max_length=150)
    nacionalidad = models.CharField(max_length=100, blank=True, default='')
    biografia = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['nombre']
        verbose_name = 'director'
        verbose_name_plural = 'directores'

    def __str__(self):
        return self.nombre


class Actor(models.Model):
    """Actor asociado a una o varias películas."""

    nombre = models.CharField(max_length=150)
    nacionalidad = models.CharField(max_length=100, blank=True, default='')
    biografia = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['nombre']
        verbose_name = 'actor'
        verbose_name_plural = 'actores'

    def __str__(self):
        return self.nombre


class Pelicula(models.Model):
    """Película del catálogo, gestionada únicamente por los administradores."""

    GENEROS = [
        ('accion', 'Acción'),
        ('aventura', 'Aventura'),
        ('comedia', 'Comedia'),
        ('drama', 'Drama'),
        ('terror', 'Terror'),
        ('scifi', 'Ciencia ficción'),
        ('romance', 'Romance'),
        ('documental', 'Documental'),
        ('animacion', 'Animación'),
        ('otros', 'Otros'),
    ]

    PUNTUACIONES = [(i, str(i)) for i in range(1, 6)]

    titulo = models.CharField(max_length=200)
    director = models.CharField(max_length=150)
    anio_estreno = models.IntegerField()
    genero = models.CharField(max_length=20, choices=GENEROS, default='otros')
    sinopsis = models.TextField(blank=True, default='')
    puntuacion = models.IntegerField(choices=PUNTUACIONES, null=True, blank=True)
    portada = models.ImageField(upload_to='portadas/', blank=True, null=True)
    mostrar_en_banner = models.BooleanField(
        default=False,
        help_text='Incluye esta película en el banner del catálogo.',
    )
    imagen = models.ImageField(upload_to='portadas/', blank=True, null=True)
    video_fondo_url = models.URLField(
        blank=True,
        help_text='URL opcional de un video MP4 para el banner principal.',
    )
    duracion = models.PositiveIntegerField(default=0, help_text='Duración en minutos')
    fecha_agregada = models.DateTimeField(default=timezone.now)
    calificacion_promedio = models.FloatField(default=0.0)
    total_calificaciones = models.PositiveIntegerField(default=0)
    visualizaciones = models.PositiveIntegerField(default=0)
    actores = models.ManyToManyField(Actor, blank=True, related_name='peliculas')

    class Meta:
        ordering = ['-anio_estreno', '-fecha_agregada']
        verbose_name = 'película'
        verbose_name_plural = 'películas'

    def __str__(self):
        return f'{self.titulo} ({self.anio_estreno})'

    def get_absolute_url(self):
        return reverse('lista_peliculas')

    def recalcular_promedio(self):
        agregados = self.calificaciones.aggregate(
            promedio=models.Avg('puntuacion'),
            total=models.Count('id'),
        )
        self.calificacion_promedio = round(agregados['promedio'] or 0.0, 2)
        self.total_calificaciones = agregados['total'] or 0
        self.save(update_fields=['calificacion_promedio', 'total_calificaciones'])

    def registrar_visualizacion(self):
        self.visualizaciones += 1
        self.save(update_fields=['visualizaciones'])


class HistorialVisualizacion(models.Model):
    """Registro del historial de visualización de cada usuario."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='historial_visualizacion',
    )
    pelicula = models.ForeignKey(
        Pelicula,
        on_delete=models.CASCADE,
        related_name='historial_visualizacion',
    )
    fecha_visualizacion = models.DateTimeField(default=timezone.now)
    duracion_vista = models.PositiveIntegerField(default=0, help_text='Segundos vistos')
    progreso = models.PositiveIntegerField(default=0, help_text='Porcentaje de avance')

    class Meta:
        ordering = ['-fecha_visualizacion']
        verbose_name = 'historial de visualización'
        verbose_name_plural = 'historiales de visualización'

    def __str__(self):
        return f'{self.usuario.username} — {self.pelicula.titulo}'


class ListaPersonalizada(models.Model):
    """Lista personalizada creada por un usuario."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listas_personalizadas',
    )
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, default='')
    es_privada = models.BooleanField(default=True)
    peliculas = models.ManyToManyField(Pelicula, related_name='en_listas_personalizadas', blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'lista personalizada'
        verbose_name_plural = 'listas personalizadas'

    def __str__(self):
        return f'{self.usuario.username}: {self.nombre}'


class EstadoPelicula(models.Model):
    """Estado de visionado de un usuario sobre una película del catálogo."""

    ESTADOS = [
        ('vista', 'Vista'),
        ('progreso', 'En progreso'),
        ('pendiente', 'Pendiente'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='estados_peliculas',
    )
    pelicula = models.ForeignKey(
        Pelicula,
        on_delete=models.CASCADE,
        related_name='estados_usuarios',
    )
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'pelicula')
        ordering = ['-actualizado']
        verbose_name = 'estado de película'
        verbose_name_plural = 'estados de películas'

    def __str__(self):
        return f'{self.usuario.username} — {self.pelicula.titulo}: {self.get_estado_display()}'

class Calificacion(models.Model):

    PUNTUACIONES = [(i, str(i)) for i in range(1, 6)]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calificaciones',
    )
    pelicula = models.ForeignKey(
        Pelicula,
        on_delete=models.CASCADE,
        related_name='calificaciones',
    )
    puntuacion = models.IntegerField(choices=PUNTUACIONES)
    comentario = models.TextField(blank=True, default='')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'pelicula')
        ordering = ['-fecha']
        verbose_name = 'calificación'
        verbose_name_plural = 'calificaciones'

    def __str__(self):
        return f'{self.usuario.username} → {self.pelicula.titulo}: {self.puntuacion}/5'

class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
    )
    telefono = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfiles'

    def __str__(self):
        return self.usuario.username

