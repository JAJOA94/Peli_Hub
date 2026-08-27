from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


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
    fecha_agregada = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-anio_estreno', '-fecha_agregada']
        verbose_name = 'película'
        verbose_name_plural = 'películas'

    def __str__(self):
        return f'{self.titulo} ({self.anio_estreno})'

    def get_absolute_url(self):
        return reverse('lista_peliculas')


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
