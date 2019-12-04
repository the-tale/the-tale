
import smart_imports

smart_imports.all()


class RequestAccessForm(utils_forms.Form):
    application_name = utils_fields.CharField(max_length=models.AccessToken.APPLICATION_NAME_MAX_LENGTH, required=True)
    application_info = utils_fields.CharField(max_length=models.AccessToken.APPLICATION_INFO_MAX_LENGTH, required=False)
    application_description = utils_fields.CharField(required=True)
