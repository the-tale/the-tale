
import smart_imports

smart_imports.all()


class NewNewsForm(dext_forms.Form):

    caption = dext_fields.CharField(label='Заголовок')
    description = dext_fields.TextField(label='Кратко')
    content = dext_fields.TextField(label='Полностью')

    @classmethod
    def get_initials(cls, news):
        return {'caption': news.caption,
                'description': news.description,
                'content': news.content}
