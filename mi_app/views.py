from django.shortcuts import redirect, render
from django.templatetags.static import static


VIDEOS_INICIO = (
    static('peliculas/videos/hero/sala-cine.mp4'),
    static('peliculas/videos/hero/ambiente-cyberpunk.mp4'),
    static('peliculas/videos/hero/escena-nocturna-auto.mp4'),
)


def inicio(request):
    """Página de bienvenida / aterrizaje.

    Los usuarios autenticados van directo a su biblioteca.
    """
    if request.user.is_authenticated:
        return redirect('lista_peliculas')
    return render(request, 'mi_app/inicio.html', {'videos_inicio': VIDEOS_INICIO})
