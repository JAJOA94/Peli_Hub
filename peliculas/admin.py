from django.contrib import admin

from .models import EstadoPelicula, Pelicula, Perfil


@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'director', 'anio_estreno', 'genero', 'puntuacion', 'fecha_agregada')
    list_filter = ('genero',)
    search_fields = ('titulo', 'director')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono')
    search_fields = ('usuario__username',)


@admin.register(EstadoPelicula)
class EstadoPeliculaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pelicula', 'estado', 'actualizado')
    list_filter = ('estado',)
    search_fields = ('usuario__username', 'pelicula__titulo')
