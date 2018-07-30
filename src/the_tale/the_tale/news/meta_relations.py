
import smart_imports

smart_imports.all()


class News(utils_meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 12
    TYPE_CAPTION = 'Новость'

    def __init__(self, caption, **kwargs):
        super(News, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('news:show', self.id)

    @classmethod
    def create_from_object(cls, news):
        return cls(id=news.id, caption=news.caption)

    @classmethod
    def create_from_id(cls, id):
        try:
            news = models.News.objects.get(id=id)
        except models.News.DoesNotExists:
            return None

        return cls.create_from_object(news)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
