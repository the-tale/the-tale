
import smart_imports

smart_imports.all()


class Bill(utils_meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 2
    TYPE_CAPTION = 'Запись Книги Судеб'

    def __init__(self, caption, **kwargs):
        super(Bill, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('game:bills:show', self.id)

    @classmethod
    def create_from_object(cls, bill):
        return cls(id=bill.id, caption=bill.caption)

    @classmethod
    def create_from_id(cls, id):
        try:
            bill = models.Bill.objects.get(id=id)
        except models.Bill.DoesNotExist:
            return None

        return cls.create_from_object(bill)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls(id=id, caption=caption) for id, caption in models.Bill.objects.filter(ids__in=ids).values_list('id', 'caption')]
