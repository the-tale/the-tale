
import smart_imports

smart_imports.all()


class Account(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 7
    TYPE_CAPTION = 'Хранитель'

    def __init__(self, caption, **kwargs):
        super(Account, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('accounts:show', self.id)

    @classmethod
    def create_from_object(cls, account):
        return cls(id=account.id, caption=account.nick_verbose)

    @classmethod
    def create_removed(cls):
        return cls(id=None, caption='неизвестный Хранитель')

    @classmethod
    def create_from_id(cls, id):
        from . import prototypes

        account = prototypes.AccountPrototype.get_by_id(id)

        if account is None:
            return cls.create_removed()

        return cls.create_from_object(account)

    @classmethod
    def create_from_ids(cls, ids):
        records = models.Account.objects.filter(id__in=ids)

        if len(ids) != len(records):
            raise meta_relations_exceptions.ObjectsNotFound(type=cls.TYPE, ids=ids)

        return [cls.create_from_object(prototypes.AccountPrototype(record)) for record in records]
