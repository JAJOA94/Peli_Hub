from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Pelicula, Perfil


class PeliculaForm(forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = [
            'titulo',
            'director',
            'anio_estreno',
            'genero',
            'sinopsis',
            'puntuacion',
            'portada',
        ]
        widgets = {
            'anio_estreno': forms.NumberInput(attrs={'min': 1888, 'max': 2100}),
            'sinopsis': forms.Textarea(attrs={'rows': 4}),
        }


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    telefono = forms.CharField(
        required=True,
        max_length=20,
        label='Número de teléfono',
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'telefono']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['username'].help_text = ''
        self.fields['password1'].label = 'Contraseña'
        self.fields['password1'].help_text = ''
        self.fields['password2'].label = 'Repetir contraseña'
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']

        if commit:
            usuario.save()
            Perfil.objects.update_or_create(
                usuario=usuario,
                defaults={'telefono': self.cleaned_data['telefono']},
            )

        return usuario
