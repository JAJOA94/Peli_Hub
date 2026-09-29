import random

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from peliculas.models import Calificacion, Pelicula


class Command(BaseCommand):
    help = 'Genera calificaciones aleatorias de demostración para llenar los rankings.'

    def add_arguments(self, parser):
        parser.add_argument('--seed', type=int, default=2026)

    def handle(self, *args, **options):
        Usuario = get_user_model()
        demo, creado = Usuario.objects.get_or_create(
            username='pelihub_demo_calificaciones',
            defaults={'is_active': False},
        )
        if not creado and demo.is_active:
            raise CommandError(
                'El usuario reservado para las calificaciones demo está activo; '
                'no se modificó ningún dato.'
            )
        if creado or demo.has_usable_password():
            demo.set_unusable_password()
            demo.is_active = False
            demo.save(update_fields=['password', 'is_active'])

        generador = random.Random(options['seed'])
        ahora = timezone.now()
        nuevas = 0
        actualizadas = 0

        with transaction.atomic():
            for pelicula in Pelicula.objects.all().iterator():
                _, fue_creada = Calificacion.objects.update_or_create(
                    usuario=demo,
                    pelicula=pelicula,
                    defaults={
                        'puntuacion': generador.randint(1, 5),
                        'comentario': 'Calificación aleatoria de demostración.',
                        'fecha': ahora,
                    },
                )
                if fue_creada:
                    nuevas += 1
                else:
                    actualizadas += 1

        self.stdout.write(self.style.SUCCESS(
            f'{nuevas} calificaciones creadas y {actualizadas} actualizadas '
            f'para {Pelicula.objects.count()} películas. '
            'Se guardaron este mes en la cuenta demo inactiva.'
        ))
