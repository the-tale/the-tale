
import smart_imports

smart_imports.all()


class MARKUP_METHOD(rels_django.DjangoEnum):
    records = (('POSTMARKUP', 0, 'bb-code'),
               ('MARKDOWN', 1, 'markdown'))


class POST_REMOVED_BY(rels_django.DjangoEnum):
    records = (('AUTHOR', 0, 'удалён аффтаром'),
               ('THREAD_OWNER', 1, 'удалён владельцем темы'),
               ('MODERATOR', 2, 'удалён модератором'))


class POST_STATE(rels_django.DjangoEnum):
    records = (('DEFAULT', 0, 'видим'),
               ('REMOVED', 1, 'удалён'))
