from django.contrib import admin
from .models import Pelicula, EstadoPelicula, Perfil

@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    # Columnas visibles en la lista
    list_display = ('titulo', 'director', 'anio_estreno', 'genero', 'puntuacion', 'fecha_agregada')
    # Filtros laterales
    list_filter = ('genero', 'anio_estreno', 'puntuacion')
    # Barra de búsqueda
    search_fields = ('titulo', 'director', 'sinopsis')
    # Jerarquía por fechas para navegación rápida
    date_hierarchy = 'fecha_agregada'

@admin.register(EstadoPelicula)
class EstadoPeliculaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pelicula', 'estado', 'actualizado')
    list_filter = ('estado', 'actualizado')
    # Búsqueda a través de llaves foráneas (el username del usuario o el título de la película)
    search_fields = ('usuario__username', 'pelicula__titulo')

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono')
    search_fields = ('usuario__username', 'telefono')