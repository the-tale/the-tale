
import smart_imports

smart_imports.all()


class NewNewsForm(utils_forms.Form):

    caption = utils_fields.CharField(label='Заголовок')
    description = utils_fields.TextField(label='Кратко')
    content = utils_fields.TextField(label='Полностью')

    @classmethod
    def get_initials(cls, news):
        return {'caption': news.caption,
                'description': news.description,
                'content': news.content}
