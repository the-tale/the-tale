# coding: utf-8

from the_tale.cms.news import models
from the_tale.cms.news import relations
from the_tale.cms.news import objects


def news_from_model(model):
    return objects.News(id=model.id,
                        caption=model.caption,
                        description=model.description,
                        content=model.content,
                        created_at=model.created_at,
                        forum_thread_id=model.forum_thread_id,
                        emailed=model.emailed)



def create_news(caption, description, content):
    model = models.News.objects.create(caption=caption,
                                       description=description,
                                       content=content,
                                       emailed=relations.EMAILED_STATE.NOT_EMAILED)
    return news_from_model(model)


def save_news(news):
    models.News.objects.filter(id=news.id).update(
        caption=news.caption,
        description=news.description,
        content=news.content,
        forum_thread=news.forum_thread_id,
        emailed=news.emailed)


def load_news(news_id):
    try:
        return news_from_model(models.News.objects.get(id=news_id))
    except models.News.DoesNotExist:
        return None


def load_news_from_query(query):
    return [news_from_model(news_model) for news_model in list(query)]


def load_last_news():
    try:
        return news_from_model(models.News.objects.latest())
    except models.News.DoesNotExist:
        return None


def send_mails(news):
    from the_tale.post_service.prototypes import MessagePrototype as PostServiceMessagePrototype
    from the_tale.post_service.message_handlers import NewsHandler
    PostServiceMessagePrototype.create(NewsHandler(news_id=news.id))

    news.emailed = relations.EMAILED_STATE.EMAILED
    save_news(news)
