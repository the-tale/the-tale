# coding: utf-8

from dext.utils.decorators import nested_commit_on_success

from forum.models import SubCategory, Thread, Post, MARKUP_METHOD, POST_STATE, POST_REMOVED_BY

@nested_commit_on_success
def create_thread(subcategory, caption, author, text, markup_method=MARKUP_METHOD.POSTMARKUP):

    if isinstance(subcategory, int):
        subcategory = SubCategory.objects.get(id=subcategory)

    thread = Thread.objects.create(subcategory=subcategory,
                                   caption=caption,
                                   author=author,
                                   last_poster=author,
                                   posts_count=0)

    post = Post.objects.create(thread=thread,
                               author=author,
                               markup_method=markup_method,
                               text=text)

    subcategory.threads_count = Thread.objects.filter(subcategory=subcategory).count()
    subcategory.last_poster = author
    subcategory.posts_count = sum(Thread.objects.filter(subcategory=subcategory).values_list('posts_count', flat=True))
    subcategory.updated_at = post.created_at
    subcategory.save()

    return thread

@nested_commit_on_success
def delete_thread(subcategory, thread):

    if isinstance(subcategory, int):
        subcategory = SubCategory.objects.get(id=subcategory)

    Post.objects.filter(thread=thread).delete()

    thread.delete()

    subcategory.threads_count = Thread.objects.filter(subcategory=subcategory).count()
    subcategory.posts_count = sum(Thread.objects.filter(subcategory=subcategory).values_list('posts_count', flat=True))
    subcategory.save()

@nested_commit_on_success
def update_thread(subcategory, thread, caption, new_subcategory_id):

    thread.caption = caption

    subcategory_changed = new_subcategory_id is not None and subcategory.id != new_subcategory_id

    if subcategory_changed:
        thread.subcategory = SubCategory.objects.get(id=new_subcategory_id)

    thread.save()

    if subcategory_changed:
        subcategory.threads_count = Thread.objects.filter(subcategory=subcategory).count()
        subcategory.posts_count = sum(Thread.objects.filter(subcategory=subcategory).values_list('posts_count', flat=True))
        subcategory.save()

        thread.subcategory.threads_count = Thread.objects.filter(subcategory=thread.subcategory).count()
        thread.subcategory.posts_count = sum(Thread.objects.filter(subcategory=thread.subcategory).values_list('posts_count', flat=True))
        thread.subcategory.save()


@nested_commit_on_success
def create_post(subcategory, thread, author, text):

    post = Post.objects.create(thread=thread, author=author, text=text)

    thread.updated_at = post.created_at
    thread.posts_count = Post.objects.filter(thread=thread).count() - 1
    thread.last_poster = author
    thread.save()

    subcategory.updated_at = post.created_at
    subcategory.last_poster = author
    subcategory.posts_count = sum(Thread.objects.filter(subcategory=subcategory).values_list('posts_count', flat=True))
    subcategory.save()

    return post


@nested_commit_on_success
def delete_post(initiator, thread, post):

    post.state = POST_STATE.REMOVED

    if post.author == initiator:
        post.removed_by = POST_REMOVED_BY.AUTHOR
    elif thread.author == initiator:
        post.removed_by = POST_REMOVED_BY.THREAD_OWNER
    else:
        post.removed_by = POST_REMOVED_BY.MODERATOR

    post.remove_initiator = initiator

    post.save()
