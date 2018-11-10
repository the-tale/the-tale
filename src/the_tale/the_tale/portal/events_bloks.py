
import smart_imports

smart_imports.all()


class Event:
    __slots__ = ('date', 'initiator', 'title', 'operation', 'url')

    def __init__(self, date, initiator, title, operation, url):
        self.date = date
        self.initiator = initiator
        self.title = title
        self.operation = operation
        self.url = url

    def is_today(self):
        return self.date.date() == datetime.datetime.now().date()

    def is_yesterday(self):
        return self.date.date() + datetime.timedelta(days=1) == datetime.datetime.now().date()


class Block:
    __slots__ = ('title', 'rss', 'url', 'events')

    def __init__(self, title, rss, url, events):
        self.title = title
        self.rss = rss
        self.url = url
        self.events = events


def forum_common(limit, exclude_subcategories=()):
    forum_threads = forum_prototypes.ThreadPrototype.get_last_threads(account=None,
                                                                      limit=limit,
                                                                      exclude_subcategories=exclude_subcategories)
    events = [Event(date=thread.updated_at,
                    initiator=thread.last_poster.nick_verbose if thread.last_poster else None,
                    title=thread.caption,
                    operation=None,
                    url=thread.paginator.last_page_url) for thread in forum_threads]

    return Block(title='Горячие темы',
                 rss=dext_urls.url('forum:feed'),
                 url=dext_urls.url('forum:'),
                 events=events)


def forum_subcategory(title, subcategory, limit):
    if subcategory is None:
        return None

    forum_threads = subcategory.get_last_threads(limit=limit)

    events = [Event(date=thread.updated_at,
                    initiator=thread.last_poster.nick_verbose if thread.last_poster else None,
                    title=thread.caption,
                    operation=None,
                    url=thread.paginator.last_page_url) for thread in forum_threads]

    return Block(title=title,
                 rss=None,
                 url=dext_urls.url('forum:subcategories:show', subcategory.id),
                 events=events)


def blogs_common(limit):
    blog_posts = [blogs_prototypes.PostPrototype(blog_post_model)
                  for blog_post_model in blogs_models.Post.objects.filter(state__in=[blogs_relations.POST_STATE.ACCEPTED,
                                                                                     blogs_relations.POST_STATE.NOT_MODERATED],
                                                                          votes__gte=0).order_by('-created_at')[:limit]]

    events = [Event(date=post.created_at,
                    initiator=post.author.nick_verbose if post.author else None,
                    title=post.caption,
                    operation=None,
                    url=dext_urls.url('blogs:posts:show', post.id)) for post in blog_posts]

    return Block(title='Фольклор',
                 rss=None,
                 url=dext_urls.url('blogs:posts:'),
                 events=events)


def bills_common(limit):
    bills = bills_prototypes.BillPrototype.get_recently_modified_bills(limit)

    events = [Event(date=bill.updated_at if bill.state.is_VOTING else bill.voting_end_at,
                    initiator=None,
                    title=bill.caption,
                    operation=bill.last_bill_event_text,
                    url=dext_urls.url('game:bills:show', bill.id)) for bill in bills]

    return Block(title='Книга Судеб',
                 rss=None,
                 url=dext_urls.url('game:bills:'),
                 events=events)
