from django.test import TestCase


class InicioHeroTests(TestCase):
	def test_inicio_muestra_clips_de_video_locales(self):
		response = self.client.get('/')

		self.assertContains(response, 'class="hero hero--video"')
		self.assertContains(response, '/static/peliculas/videos/hero/sala-cine.mp4')
		self.assertContains(response, '/static/peliculas/videos/hero/ambiente-cyberpunk.mp4')
		self.assertContains(response, '/static/peliculas/videos/hero/escena-nocturna-auto.mp4')
		self.assertContains(response, 'data-home-audio')
