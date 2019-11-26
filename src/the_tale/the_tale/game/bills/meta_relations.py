
import smart_imports

smart_imports.all()


class Bill(meta_relations_objects.MetaType):
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
    def create_unknown(cls, id):
        return cls(id=id, caption='неизвестная запись Книги Судеб')

    @classmethod
    def create_from_object(cls, bill):
        return cls(id=bill.id, caption=bill.caption)

    @classmethod
    def create_from_id(cls, id):
        try:
            bill = models.Bill.objects.get(id=id)
        except models.Bill.DoesNotExist:
            return cls.create_unknown(id)

        return cls.create_from_object(bill)

    @classmethod
    def create_from_ids(cls, ids):
        bills = [cls(id=id, caption=caption) for id, caption in models.Bill.objects.filter(id__in=ids).values_list('id', 'caption')]

        found_ids = {bill.id for bill in bills}

        for id in ids:
            if id in found_ids:
                continue

            bills.append(cls.create_unknown(id))

        return bills
