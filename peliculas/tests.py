from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from .models import EstadoPelicula, Pelicula


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

    def test_catalogo_muestra_todas_las_peliculas(self):
        self.client.force_login(self.normal)
        response = self.client.get('/peliculas/')
        self.assertContains(response, 'Película antigua')
        self.assertContains(response, 'Película reciente')

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

    def test_cambiar_estado_guarda_por_usuario(self):
        self.client.force_login(self.normal)
        self.client.post(
            f'/peliculas/estado/{self.pelicula_antigua.id}/', {'estado': 'vista'}
        )
        estado = EstadoPelicula.objects.get(
            usuario=self.normal, pelicula=self.pelicula_antigua
        )
        self.assertEqual(estado.estado, 'vista')

    def test_estado_es_independiente_por_usuario(self):
        self.client.force_login(self.normal)
        self.client.post(
            f'/peliculas/estado/{self.pelicula_antigua.id}/', {'estado': 'vista'}
        )
        self.client.force_login(self.otro)
        self.client.post(
            f'/peliculas/estado/{self.pelicula_antigua.id}/', {'estado': 'progreso'}
        )

        self.assertEqual(
            EstadoPelicula.objects.get(usuario=self.normal, pelicula=self.pelicula_antigua).estado,
            'vista',
        )
        self.assertEqual(
            EstadoPelicula.objects.get(usuario=self.otro, pelicula=self.pelicula_antigua).estado,
            'progreso',
        )

    def test_normal_ve_selector_de_estado(self):
        self.client.force_login(self.normal)
        response = self.client.get('/peliculas/')
        self.assertContains(response, '<select')

    def test_admin_no_ve_selector_de_estado(self):
        self.client.force_login(self.admin)
        response = self.client.get('/peliculas/')
        self.assertNotContains(response, '<select')

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

    def test_panel_admin_solo_superusuario(self):
        self.client.force_login(self.normal)
        response = self.client.get('/peliculas/panel-admin/')
        self.assertEqual(response.status_code, 302)

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
