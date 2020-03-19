
import smart_imports

smart_imports.all()


class SayForm(utils_forms.Form):

    text = utils_fields.CharField(max_length=1024, required=True)
