from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Calificacion, Pelicula


def _actualizar_promedio(pelicula_id):
    pelicula = Pelicula.objects.filter(pk=pelicula_id).first()
    if pelicula:
        pelicula.recalcular_promedio()


@receiver(post_save, sender=Calificacion)
def actualizar_promedio_al_guardar(sender, instance, **kwargs):
    _actualizar_promedio(instance.pelicula_id)


@receiver(post_delete, sender=Calificacion)
def actualizar_promedio_al_eliminar(sender, instance, **kwargs):
    _actualizar_promedio(instance.pelicula_id)
