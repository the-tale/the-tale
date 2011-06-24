# -*- coding: utf-8 -*-

from django_next.forms import forms, fields

class RegistrationForm(forms.Form):
    
    email = fields.EmailField(label='email')

    nick = fields.CharField(label='nick')

    password = fields.PasswordField(label='password')

    password_repeated = fields.PasswordField(label='repeated password')


    def clean(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get('password')
        password_repeated = cleaned_data.get('password_repeated')

        if password != password_repeated:
            raise forms.forms.ValidationError(u'Пароли не совпадают, повторите попытку')

        return cleaned_data


class LoginForm(forms.Form):
    
    email = fields.EmailField(label='email')
    password = fields.PasswordField(label='password')
