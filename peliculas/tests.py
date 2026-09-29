from django import forms
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models import Count
from django.test import TestCase, override_settings
from django.utils import timezone

from .forms import CalificacionForm
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


@override_settings(ALLOWED_HOSTS=['testserver'])
class PeliculasTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser(
            username='admin_test', password='ClaveSegura123!'
        )
        self.normal = User.objects.create_user(
            username='usuario_test', password='ClaveSegura123!'
        )
        self.otro = User.objects.create_user(
            username='otro_test', password='ClaveSegura123!'
        )

        self.pelicula_antigua = Pelicula.objects.create(
            titulo='Película antigua', director='Director A', anio_estreno=1999,
        )
        self.pelicula_reciente = Pelicula.objects.create(
            titulo='Película reciente', director='Director B', anio_estreno=2024,
        )

    def test_registro_guarda_usuario_y_perfil(self):
        response = self.client.post('/peliculas/registro/', {
            'username': 'nueva_persona',
            'email': 'nueva@example.com',
            'telefono': '5551234567',
            'password1': 'OtraClave123!',
            'password2': 'OtraClave123!',
        })
        self.assertRedirects(response, '/peliculas/')
        usuario = get_user_model().objects.get(username='nueva_persona')
        self.assertEqual(usuario.email, 'nueva@example.com')
        self.assertEqual(usuario.perfil.telefono, '5551234567')

    def test_perfil_solo_actualiza_los_datos_del_usuario_autenticado(self):
        Perfil.objects.create(usuario=self.normal, telefono='111111')
        Perfil.objects.create(usuario=self.otro, telefono='222222')
        self.client.force_login(self.normal)

        response = self.client.post('/peliculas/mi-perfil/', {
            'username': 'usuario_actualizado',
            'email': 'actualizado@example.com',
            'telefono': '333333',
        })

        self.assertRedirects(response, '/peliculas/mi-perfil/')
        self.normal.refresh_from_db()
        self.otro.refresh_from_db()
        self.assertEqual(self.normal.username, 'usuario_actualizado')
        self.assertEqual(self.normal.email, 'actualizado@example.com')
        self.assertEqual(self.normal.perfil.telefono, '333333')
        self.assertEqual(self.otro.username, 'otro_test')
        self.assertEqual(self.otro.perfil.telefono, '222222')

    def test_perfil_requiere_autenticacion(self):
        response = self.client.get('/peliculas/mi-perfil/')
        self.assertRedirects(
            response,
            '/peliculas/login/?next=/peliculas/mi-perfil/',
        )

    def test_catalogo_muestra_todas_las_peliculas(self):
        self.client.force_login(self.normal)
        response = self.client.get('/peliculas/')
        self.assertContains(response, 'Película antigua')
        self.assertContains(response, 'Película reciente')

    def test_hero_incluye_clips_locales_de_fondo(self):
        self.client.force_login(self.normal)

        response = self.client.get('/peliculas/')

        self.assertContains(response, '/static/peliculas/videos/hero/sala-cine.mp4')
        self.assertContains(response, '/static/peliculas/videos/hero/ambiente-cyberpunk.mp4')
        self.assertContains(response, '/static/peliculas/videos/hero/escena-nocturna-auto.mp4')

    def test_lista_ordenada_por_anio_descendente(self):
        self.client.force_login(self.normal)
        response = self.client.get('/peliculas/')
        self.assertLess(
            response.content.index(b'Pel\xc3\xadcula reciente'),
            response.content.index(b'Pel\xc3\xadcula antigua'),
        )

    def test_normal_no_puede_crear(self):
        self.client.force_login(self.normal)
        response = self.client.post('/peliculas/nueva/', {
            'titulo': 'Película no autorizada',
            'director': 'X',
            'anio_estreno': 2020,
            'genero': 'drama',
            'sinopsis': '',
            'puntuacion': '',
        })
        self.assertRedirects(response, '/peliculas/')
        self.assertFalse(Pelicula.objects.filter(titulo='Película no autorizada').exists())

    def test_admin_puede_crear(self):
        self.client.force_login(self.admin)
        response = self.client.post('/peliculas/nueva/', {
            'titulo': 'Nueva peli',
            'director': 'Director X',
            'anio_estreno': 2023,
            'genero': 'drama',
            'sinopsis': '',
            'puntuacion': '',
        })
        self.assertRedirects(response, '/peliculas/')
        self.assertTrue(Pelicula.objects.filter(titulo='Nueva peli').exists())

    def test_promedio_se_recalcula_al_crear_actualizar_y_borrar_calificacion(self):
        primera = Calificacion.objects.create(
            usuario=self.normal,
            pelicula=self.pelicula_antigua,
            puntuacion=4,
        )
        self.pelicula_antigua.refresh_from_db()
        self.assertEqual(self.pelicula_antigua.calificacion_promedio, 4.0)
        self.assertEqual(self.pelicula_antigua.total_calificaciones, 1)

        segunda = Calificacion.objects.create(
            usuario=self.otro,
            pelicula=self.pelicula_antigua,
            puntuacion=2,
        )
        self.pelicula_antigua.refresh_from_db()
        self.assertEqual(self.pelicula_antigua.calificacion_promedio, 3.0)

        primera.puntuacion = 5
        primera.save()
        self.pelicula_antigua.refresh_from_db()
        self.assertEqual(self.pelicula_antigua.calificacion_promedio, 3.5)

        segunda.delete()
        self.pelicula_antigua.refresh_from_db()
        self.assertEqual(self.pelicula_antigua.calificacion_promedio, 5.0)
        self.assertEqual(self.pelicula_antigua.total_calificaciones, 1)

    def test_catalogo_busca_con_q_genero_y_anio(self):
        coincidencia = Pelicula.objects.create(
            titulo='Búsqueda avanzada',
            director='Directora de prueba',
            anio_estreno=2020,
            genero='drama',
        )
        Pelicula.objects.create(
            titulo='Año diferente',
            director='Directora de prueba',
            anio_estreno=2021,
            genero='drama',
        )
        Pelicula.objects.create(
            titulo='Género diferente',
            director='Directora de prueba',
            anio_estreno=2020,
            genero='accion',
        )
        self.client.force_login(self.normal)

        response = self.client.get(
            '/peliculas/?q=Directora&genero=drama&anio=2020'
        )

        self.assertContains(response, coincidencia.titulo)
        self.assertNotContains(response, 'Año diferente')
        self.assertNotContains(response, 'Género diferente')
        self.assertNotContains(response, self.pelicula_antigua.titulo)

    def test_top_historico_y_mensual_usan_sus_periodos(self):
        Calificacion.objects.create(
            usuario=self.normal,
            pelicula=self.pelicula_antigua,
            puntuacion=5,
        )
        Calificacion.objects.create(
            usuario=self.otro,
            pelicula=self.pelicula_reciente,
            puntuacion=4,
        )
        Calificacion.objects.filter(pelicula=self.pelicula_reciente).update(
            fecha=timezone.now().replace(day=1) - timezone.timedelta(days=1)
        )
        self.client.force_login(self.normal)

        response = self.client.get('/peliculas/')

        self.assertContains(response, 'class="top10-list"')
        self.assertContains(response, 'class="top10-number"')
        self.assertContains(response, 'class="top10-placeholder"')
        self.assertEqual(
            response.context['top_historico'][0].pk,
            self.pelicula_antigua.pk,
        )
        self.assertEqual(
            [pelicula.pk for pelicula in response.context['top_mensual']],
            [self.pelicula_antigua.pk],
        )

    def test_detalle_recomienda_por_director_y_genero(self):
        pelicula = Pelicula.objects.create(
            titulo='Película base',
            director='Directora compartida',
            anio_estreno=2020,
            genero='drama',
        )
        misma_directora = Pelicula.objects.create(
            titulo='Otra de la directora',
            director='Directora compartida',
            anio_estreno=2021,
            genero='comedia',
        )
        similar = Pelicula.objects.create(
            titulo='Otro drama',
            director='Otro director',
            anio_estreno=2022,
            genero='drama',
        )
        Calificacion.objects.create(
            usuario=self.normal,
            pelicula=similar,
            puntuacion=5,
        )
        self.client.force_login(self.normal)

        response = self.client.get(f'/peliculas/ver/{pelicula.pk}/')

        director_ids = {
            recomendada.pk
            for recomendada in response.context['peliculas_por_director']
        }
        similares = response.context['peliculas_similares']
        self.assertIn(misma_directora.pk, director_ids)
        self.assertNotIn(pelicula.pk, director_ids)
        self.assertIn(similar.pk, [recomendada.pk for recomendada in similares])
        self.assertNotIn(
            misma_directora.pk,
            [recomendada.pk for recomendada in similares],
        )
        self.assertTrue(all(recomendada.genero == pelicula.genero for recomendada in similares))

    def test_ver_pelicula_la_pone_en_progreso(self):
        self.client.force_login(self.normal)
        response = self.client.get(
            f'/peliculas/ver/{self.pelicula_antigua.id}/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            EstadoPelicula.objects.filter(
                usuario=self.normal, pelicula=self.pelicula_antigua
            ).exists()
        )
        response = self.client.post(
            f'/peliculas/ver/{self.pelicula_antigua.id}/iniciar/'
        )
        self.assertRedirects(response, f'/peliculas/ver/{self.pelicula_antigua.id}/')
        estado = EstadoPelicula.objects.get(
            usuario=self.normal, pelicula=self.pelicula_antigua
        )
        self.assertEqual(estado.estado, 'progreso')

    def test_terminar_pelicula_la_pone_en_vista(self):
        self.client.force_login(self.normal)
        self.client.post(f'/peliculas/ver/{self.pelicula_antigua.id}/iniciar/')
        response = self.client.post(
            f'/peliculas/terminar/{self.pelicula_antigua.id}/'
        )
        self.assertRedirects(response, '/peliculas/')
        estado = EstadoPelicula.objects.get(
            usuario=self.normal, pelicula=self.pelicula_antigua
        )
        self.assertEqual(estado.estado, 'vista')

    def test_estado_por_defecto_es_pendiente(self):
        self.client.force_login(self.normal)
        response = self.client.get('/peliculas/')
        self.assertContains(response, 'Pendiente')
        self.assertFalse(
            EstadoPelicula.objects.filter(
                usuario=self.normal, pelicula=self.pelicula_antigua
            ).exists()
        )

    def test_estado_es_independiente_por_usuario(self):
        self.client.force_login(self.normal)
        self.client.post(f'/peliculas/ver/{self.pelicula_antigua.id}/iniciar/')
        self.client.post(f'/peliculas/terminar/{self.pelicula_antigua.id}/')

        self.client.force_login(self.otro)
        self.client.post(f'/peliculas/ver/{self.pelicula_antigua.id}/iniciar/')

        self.assertEqual(
            EstadoPelicula.objects.get(usuario=self.normal, pelicula=self.pelicula_antigua).estado,
            'vista',
        )
        self.assertEqual(
            EstadoPelicula.objects.get(usuario=self.otro, pelicula=self.pelicula_antigua).estado,
            'progreso',
        )

    def test_ver_de_nuevo_no_degrada_vista(self):
        self.client.force_login(self.normal)
        self.client.post(f'/peliculas/ver/{self.pelicula_antigua.id}/iniciar/')
        self.client.post(f'/peliculas/terminar/{self.pelicula_antigua.id}/')
        self.client.post(f'/peliculas/ver/{self.pelicula_antigua.id}/iniciar/')
        self.assertEqual(
            EstadoPelicula.objects.get(
                usuario=self.normal, pelicula=self.pelicula_antigua
            ).estado,
            'vista',
        )

    def test_admin_no_puede_ver_ni_terminar(self):
        self.client.force_login(self.admin)
        self.client.get(f'/peliculas/ver/{self.pelicula_antigua.id}/')
        self.client.post(f'/peliculas/ver/{self.pelicula_antigua.id}/iniciar/')
        self.client.post(f'/peliculas/terminar/{self.pelicula_antigua.id}/')
        self.assertFalse(
            EstadoPelicula.objects.filter(
                usuario=self.admin, pelicula=self.pelicula_antigua
            ).exists()
        )

    def test_normal_ve_boton_ver_pelicula(self):
        self.client.force_login(self.normal)
        response = self.client.get('/peliculas/')
        self.assertContains(response, 'Ver detalles')
        self.assertContains(response, '+ Mi lista')

    def test_catalogo_esta_disponible_desde_mi_perfil(self):
        self.client.force_login(self.normal)
        response = self.client.get('/peliculas/mi-perfil/')
        self.assertContains(response, 'Catálogo')
        self.assertContains(response, 'href="/peliculas/"')

    def test_admin_no_ve_boton_ver_pelicula(self):
        self.client.force_login(self.admin)
        response = self.client.get('/peliculas/')
        self.assertNotContains(response, 'Ver detalles')
        self.assertNotContains(response, '+ Mi lista')

    def test_agregar_pelicula_crea_lista_privada_del_usuario(self):
        self.client.force_login(self.normal)
        response = self.client.post(
            f'/peliculas/mi-lista/agregar/{self.pelicula_antigua.id}/'
        )
        self.assertRedirects(response, '/peliculas/')
        lista = ListaPersonalizada.objects.get(usuario=self.normal, nombre='Mi lista')
        self.assertTrue(lista.es_privada)
        self.assertTrue(lista.peliculas.filter(id=self.pelicula_antigua.id).exists())

    def test_catalogo_agrupa_por_genero_y_tarjeta_abre_detalle(self):
        pelicula = Pelicula.objects.create(
            titulo='Romance de prueba',
            director='Directora C',
            anio_estreno=2023,
            genero='romance',
        )
        self.client.force_login(self.normal)

        response = self.client.get('/peliculas/')

        self.assertContains(response, 'Romance')
        self.assertContains(
            response,
            f'data-detail-url="/peliculas/ver/{pelicula.id}/"',
            html=False,
        )

    def test_detalle_muestra_sinopsis_completa_y_boton_ver(self):
        sinopsis = 'Esta es la sinopsis completa que debe mostrarse sin recortarse.'
        pelicula = Pelicula.objects.create(
            titulo='Detalle completo',
            director='Directora D',
            anio_estreno=2025,
            sinopsis=sinopsis,
        )
        self.client.force_login(self.normal)

        response = self.client.get(f'/peliculas/ver/{pelicula.id}/')

        self.assertContains(response, sinopsis)
        self.assertContains(response, 'Ver película')

    def test_normal_no_puede_editar(self):
        self.client.force_login(self.normal)
        self.client.post(
            f'/peliculas/editar/{self.pelicula_antigua.id}/',
            {
                'titulo': 'Hackeada',
                'director': 'Director A',
                'anio_estreno': 1999,
                'genero': 'drama',
                'sinopsis': '',
                'puntuacion': '',
            },
        )
        self.pelicula_antigua.refresh_from_db()
        self.assertEqual(self.pelicula_antigua.titulo, 'Película antigua')

    def test_normal_no_puede_eliminar(self):
        self.client.force_login(self.normal)
        self.client.post(f'/peliculas/eliminar/{self.pelicula_antigua.id}/')
        self.assertTrue(Pelicula.objects.filter(id=self.pelicula_antigua.id).exists())

    def test_admin_puede_editar(self):
        self.client.force_login(self.admin)
        self.client.post(
            f'/peliculas/editar/{self.pelicula_antigua.id}/',
            {
                'titulo': 'Película antigua editada',
                'director': 'Director A',
                'anio_estreno': 1999,
                'genero': 'drama',
                'sinopsis': '',
                'puntuacion': '',
            },
        )
        self.pelicula_antigua.refresh_from_db()
        self.assertEqual(self.pelicula_antigua.titulo, 'Película antigua editada')

    def test_eliminar_muestra_confirmacion_en_get(self):
        self.client.force_login(self.admin)
        response = self.client.get(f'/peliculas/eliminar/{self.pelicula_antigua.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Pelicula.objects.filter(id=self.pelicula_antigua.id).exists())

    def test_admin_puede_eliminar(self):
        self.client.force_login(self.admin)
        response = self.client.post(f'/peliculas/eliminar/{self.pelicula_antigua.id}/')
        self.assertRedirects(response, '/peliculas/')
        self.assertFalse(Pelicula.objects.filter(id=self.pelicula_antigua.id).exists())

    def test_logout_requiere_post(self):
        self.client.force_login(self.normal)
        response = self.client.get('/peliculas/logout/')
        self.assertEqual(response.status_code, 405)
        response = self.client.post('/peliculas/logout/')
        self.assertRedirects(response, '/')


class ModelosRequeridosTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser(
            username='admin_modelos', password='ClaveSegura123!'
        )
        self.normal = User.objects.create_user(
            username='usuario_modelos', password='ClaveSegura123!'
        )

    def test_existencia_de_modelos_y_campos_requeridos(self):
        self.assertTrue(hasattr(Director, 'nombre'))
        self.assertTrue(hasattr(Actor, 'nombre'))
        self.assertTrue(hasattr(Actor, 'peliculas'))
        self.assertTrue(hasattr(Pelicula, 'duracion'))
        self.assertTrue(hasattr(Pelicula, 'imagen'))
        self.assertTrue(hasattr(Pelicula, 'visualizaciones'))
        self.assertTrue(hasattr(Calificacion, 'usuario'))
        self.assertTrue(hasattr(Calificacion, 'pelicula'))
        self.assertTrue(hasattr(HistorialVisualizacion, 'usuario'))
        self.assertTrue(hasattr(HistorialVisualizacion, 'pelicula'))
        self.assertTrue(hasattr(ListaPersonalizada, 'usuario'))
        self.assertTrue(hasattr(ListaPersonalizada, 'es_privada'))
        self.assertTrue(hasattr(ListaPersonalizada, 'peliculas'))

    def test_catalogo_tiene_al_menos_12_peliculas_por_genero(self):
        conteos = {
            fila['genero']: fila['total']
            for fila in Pelicula.objects.values('genero').annotate(total=Count('id'))
        }

        self.assertEqual(
            conteos,
            {genero: 12 for genero, _ in Pelicula.GENEROS},
        )

    def test_comando_demo_llena_los_tops_sin_duplicar_calificaciones(self):
        call_command('generar_calificaciones_demo', verbosity=0)
        call_command('generar_calificaciones_demo', verbosity=0)

        Usuario = get_user_model()
        demo = Usuario.objects.get(username='pelihub_demo_calificaciones')
        calificaciones_demo = Calificacion.objects.filter(usuario=demo)
        ahora = timezone.localtime()

        self.assertFalse(demo.is_active)
        self.assertFalse(demo.has_usable_password())
        self.assertEqual(calificaciones_demo.count(), Pelicula.objects.count())
        self.assertEqual(
            calificaciones_demo.filter(
                fecha__year=ahora.year,
                fecha__month=ahora.month,
            ).count(),
            Pelicula.objects.count(),
        )

    def test_formulario_de_calificacion_usa_estrellas(self):
        form = CalificacionForm()
        self.assertIsInstance(form.fields['puntuacion'].widget, forms.RadioSelect)
        self.assertIn('type="radio"', form['puntuacion'].as_widget())

    def test_panel_admin_solo_superusuario(self):
        self.client.force_login(self.normal)
        response = self.client.get('/peliculas/panel-admin/')
        self.assertRedirects(response, '/peliculas/')

        self.client.force_login(self.admin)
        response = self.client.get('/peliculas/panel-admin/')
        self.assertContains(response, 'Panel de administración')

    def test_inicio_redirige_usuario_autenticado(self):
        self.client.force_login(self.normal)
        response = self.client.get('/')
        self.assertRedirects(response, '/peliculas/')

    def test_inicio_muestra_landing_anonimo(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PeliHub')
