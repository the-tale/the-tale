
import smart_imports

smart_imports.all()


class RequestAccessForm(dext_forms.Form):
    application_name = dext_fields.CharField(max_length=models.AccessToken.APPLICATION_NAME_MAX_LENGTH, required=True)
    application_info = dext_fields.CharField(max_length=models.AccessToken.APPLICATION_INFO_MAX_LENGTH, required=False)
    application_description = dext_fields.CharField(required=True)
