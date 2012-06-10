# coding: utf-8

from dext.forms import forms, fields

class EditProfileForm(forms.Form):

    email = fields.EmailField(label=u'Email (логин)')

    password = fields.PasswordField(label=u'Пароль', required=False)


class LoginForm(forms.Form):

    email = fields.EmailField(label=u'Email')
    password = fields.PasswordField(label=u'Пароль')


class ResetPasswordForm(forms.Form):

    email = fields.EmailField(label=u'Email')
