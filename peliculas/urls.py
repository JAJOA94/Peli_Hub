from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_peliculas, name='lista_peliculas'),
    path('nueva/', views.crear_pelicula, name='crear_pelicula'),
    path('editar/<int:id>/', views.editar_pelicula, name='editar_pelicula'),
    path('eliminar/<int:id>/', views.eliminar_pelicula, name='eliminar_pelicula'),
    path('ver/<int:id>/', views.ver_pelicula, name='ver_pelicula'),
    path('terminar/<int:id>/', views.terminar_pelicula, name='terminar_pelicula'),
    path('login/', views.iniciar_sesion, name='login'),
    path('registro/', views.registrarse, name='registro'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('logout/', views.cerrar_sesion, name='logout'),
]