
import smart_imports

smart_imports.all()


class SayForm(dext_forms.Form):

    text = dext_fields.CharField(max_length=1024, required=True)
