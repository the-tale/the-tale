# coding: utf-8

import datetime

from django.utils import feedgenerator
from django.db import transaction

from dext.common.utils import views as dext_views
from dext.common.utils.urls import UrlBuilder, url
from the_tale.common.utils import views as utils_views

from the_tale.common.utils.pagination import Paginator

from the_tale.accounts import views as accounts_views
from the_tale.accounts import logic as accounts_logic

from the_tale.cms.news import models
from the_tale.cms.news import conf
from the_tale.cms.news import logic
from the_tale.cms.news import forms
from the_tale.cms.news import relations

from the_tale.forum import prototypes as forum_prototypes
from the_tale.forum import relations as forum_relations


########################################
# processors definition
########################################

class EditNewsProcessor(dext_views.PermissionProcessor):
    PERMISSION = 'news.edit_news'
    CONTEXT_NAME = 'news_can_edit'

class EditorAccessProcessor(dext_views.AccessProcessor):
    ERROR_CODE = u'news.no_edit_rights'
    ERROR_MESSAGE = u'Вы не можете редактировать новости'

    def check(self, context): return context.news_can_edit


class NewsProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'news'
    ERROR_MESSAGE = u'Новость не найдена'
    URL_NAME = 'news'

    def parse(self, context, raw_value):
        try:
            id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        news = logic.load_news(id)

        if news is None:
            self.raise_wrong_value()

        return news

########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='news')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(EditNewsProcessor())


@utils_views.PageNumberProcessor()
@resource('')
def index(context):

    url_builder = UrlBuilder(url('news:'), arguments={'page': context.page})

    news_count = models.News.objects.all().count()

    paginator = Paginator(context.page, news_count, conf.settings.NEWS_ON_PAGE, url_builder)

    if paginator.wrong_page_number:
        return dext_views.Redirect(paginator.last_page_url)

    news_from, news_to = paginator.page_borders(context.page)

    news = logic.load_news_from_query(models.News.objects.all().order_by('-created_at')[news_from:news_to])

    return dext_views.Page('news/index.html',
                           content={'news': news,
                                    'paginator': paginator,
                                    'resource': context.resource} )

@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@resource('new')
def new(context):
    return dext_views.Page('news/new.html',
                           content={'resource': context.resource,
                                    'form': forms.NewNewsForm()})

@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@dext_views.FormProcessor(form_class=forms.NewNewsForm)
@resource('create', method='POST')
def create(context):
    news = logic.create_news(caption=context.form.c.caption,
                             description=context.form.c.description,
                             content=context.form.c.content)
    return dext_views.AjaxOk(content={'next_url': url('news:show', news.id)})


@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@NewsProcessor()
@resource('#news', 'edit')
def edit(context):
    return dext_views.Page('news/edit.html',
                           content={'resource': context.resource,
                                    'form': forms.NewNewsForm(initial=forms.NewNewsForm.get_initials(context.news))})

@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@NewsProcessor()
@dext_views.FormProcessor(form_class=forms.NewNewsForm)
@resource('#news', 'update', method='POST')
def update(context):
    context.news.caption = context.form.c.caption
    context.news.description = context.form.c.description
    context.news.content = context.form.c.content

    logic.save_news(context.news)

    return dext_views.AjaxOk(content={'next_url': url('news:show', context.news.id)})


@NewsProcessor()
@resource('#news', name='show')
def show(context):
    from the_tale.forum.views import ThreadPageData

    thread_data = None

    if context.news.forum_thread_id is not None:
        thread_data = ThreadPageData()
        thread_data.initialize(account=context.account,
                               thread=forum_prototypes.ThreadPrototype.get_by_id(context.news.forum_thread_id),
                               page=1,
                               inline=True)

    return dext_views.Page('news/show.html',
                           content={'news': context.news,
                                    'thread_data': thread_data,
                                    'resource': context.resource} )


@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@NewsProcessor()
@resource('#news', 'publish-on-forum', name='publish-on-forum', method='POST')
@transaction.atomic
def publish_on_forum(context):

    if conf.settings.FORUM_CATEGORY_UID is None:
        raise dext_views.exceptions.ViewError(code='forum_category_not_specified',
                                              message=u'try to publish news on forum when FORUM_CATEGORY_ID has not specified')

    if forum_prototypes.SubCategoryPrototype.get_by_uid(conf.settings.FORUM_CATEGORY_UID) is None:
        raise dext_views.exceptions.ViewError(code='forum_category_not_exists',
                                              message=u'try to publish news on forum when FORUM_CATEGORY_ID has not exists')

    if context.news.forum_thread_id is not None:
        raise dext_views.exceptions.ViewError(code='forum_thread_already_exists',
                                              message=u'try to publish news on forum when FORUM_CATEGORY_ID has not specified')

    thread = forum_prototypes.ThreadPrototype.create(forum_prototypes.SubCategoryPrototype.get_by_uid(conf.settings.FORUM_CATEGORY_UID ),
                                                     caption=context.news.caption,
                                                     author=accounts_logic.get_system_user(),
                                                     text=context.news.content,
                                                     markup_method=forum_relations.MARKUP_METHOD.MARKDOWN)

    context.news.forum_thread_id = thread.id
    logic.save_news(context.news)

    return dext_views.AjaxOk(content={'next_url': url('forum:threads:show', thread.id)})


@resource('feed')
def feed(context):
    feed = feedgenerator.Atom1Feed(u'Сказка: Новости',
                                   context.django_request.build_absolute_uri('/'),
                                   u'Новости мморпг «Сказка»',
                                   language=u'ru',
                                   feed_url=context.django_request.build_absolute_uri(url('news:feed')))

    news = logic.load_news_from_query(models.News.objects.order_by('-created_at')[:conf.settings.FEED_ITEMS_NUMBER])

    for news_item in news:

        if datetime.datetime.now() - news_item.created_at < datetime.timedelta(seconds=conf.settings.FEED_ITEMS_DELAY):
            continue

        feed.add_item(title=news_item.caption,
                      link=context.django_request.build_absolute_uri(url('news:show', news_item.id)),
                      description=news_item.html_content,
                      pubdate=news_item.created_at,
                      comments=url('forum:threads:show', news_item.forum_thread_id) if news_item.forum_thread_id else None,
                      unique_id=str(news_item.id))

    return dext_views.Atom(feed)


@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@NewsProcessor()
@resource('#news', 'send-mails', method='POST')
def send_mails(context):
    if not context.news.emailed.is_NOT_EMAILED:
        raise dext_views.exceptions.ViewError(code='wrong_mail_state',
                                              message=u'Эту новость нельзя отправить в рассылку')

    logic.send_mails(context.news)

    return dext_views.AjaxOk()


@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@NewsProcessor()
@resource('#news', 'disable-send-mails', method='POST')
def disable_send_mails(context):
    if not context.news.emailed.is_NOT_EMAILED:
        raise dext_views.exceptions.ViewError(code='wrong_mail_state',
                                              message=u'Рассылку этой новости нельзя запретить')

    context.news.emailed = relations.EMAILED_STATE.DISABLED
    logic.save_news(context.news)

    return dext_views.AjaxOk()
