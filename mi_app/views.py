from django.shortcuts import redirect, render


def inicio(request):
    """Página de bienvenida / aterrizaje.

    Los usuarios autenticados van directo a su biblioteca.
    """
    if request.user.is_authenticated:
        return redirect('lista_peliculas')
    return render(request, 'mi_app/inicio.html')
