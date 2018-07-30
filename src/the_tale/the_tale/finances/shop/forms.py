
import smart_imports

smart_imports.all()


class GMForm(dext_forms.Form):
    amount = dext_fields.IntegerField(label='Печеньки')
    description = dext_fields.TextField(label='Описание', required=True)
