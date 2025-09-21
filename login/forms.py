from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):

    email = forms.EmailField(required=True)
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = '' # Establecer la ayuda de username en vacio
        self.fields['password1'].help_text = ''  # Establece la ayuda para la contraseña en vacío
        self.fields['password2'].help_text = ''  # Establece la ayuda para la confirmación de la contraseña en vacío

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# eliminar cuenta
class UserDeleteForm(forms.Form):
    confirm = forms.BooleanField(label="Confirmar eliminación de cuenta")


# restablecimiento de contraseña
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Correo Electrónico", max_length=254, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].help_text = 'Introduce el correo electrónico asociado a tu cuenta.'

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Confirmar nueva contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = 'Tu nueva contraseña debe tener al menos 8 caracteres.'
        self.fields['new_password2'].help_text = 'Introduce la misma contraseña que antes, para verificación.'
