from django.contrib import admin

from .models import (
    Actor,
    Calificacion,
    Director,
    EstadoPelicula,
    HistorialVisualizacion,
    ListaPersonalizada,
    Pelicula,
    Perfil,
)


@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'director', 'anio_estreno', 'genero',
        'duracion', 'calificacion_promedio', 'total_calificaciones',
        'visualizaciones', 'fecha_agregada'
    )
    list_filter = ('genero', 'anio_estreno', 'puntuacion')
    search_fields = ('titulo', 'director', 'sinopsis')
    filter_horizontal = ('actores',)
    date_hierarchy = 'fecha_agregada'


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nacionalidad')
    search_fields = ('nombre', 'nacionalidad', 'biografia')


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nacionalidad')
    search_fields = ('nombre', 'nacionalidad', 'biografia')


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pelicula', 'puntuacion', 'fecha')
    list_filter = ('puntuacion', 'fecha')
    search_fields = ('usuario__username', 'pelicula__titulo', 'comentario')


@admin.register(EstadoPelicula)
class EstadoPeliculaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pelicula', 'estado', 'actualizado')
    list_filter = ('estado', 'actualizado')
    search_fields = ('usuario__username', 'pelicula__titulo')


@admin.register(HistorialVisualizacion)
class HistorialVisualizacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pelicula', 'fecha_visualizacion', 'progreso')
    list_filter = ('fecha_visualizacion', 'progreso')
    search_fields = ('usuario__username', 'pelicula__titulo')


@admin.register(ListaPersonalizada)
class ListaPersonalizadaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nombre', 'es_privada', 'fecha_creacion')
    list_filter = ('es_privada', 'fecha_creacion')
    search_fields = ('usuario__username', 'nombre', 'descripcion')
    filter_horizontal = ('peliculas',)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono')
    search_fields = ('usuario__username', 'telefono')