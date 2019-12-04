
import smart_imports

smart_imports.all()


class GMForm(utils_forms.Form):
    amount = utils_fields.IntegerField(label='Печеньки')
    description = utils_fields.TextField(label='Описание', required=True)
