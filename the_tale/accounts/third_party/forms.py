# coding: utf-8

from dext.forms import forms, fields

from the_tale.accounts.third_party import models


class RequestAccessForm(forms.Form):
    application_name = fields.CharField(max_length=models.AccessToken.APPLICATION_NAME_MAX_LENGTH, required=True)
    application_info = fields.CharField(max_length=models.AccessToken.APPLICATION_INFO_MAX_LENGTH, required=False)
    application_description = fields.CharField(required=True)
