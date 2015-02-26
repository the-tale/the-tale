# coding: utf-8

import markdown


class News(object):
    __slots__ = ('id', 'caption', 'description', 'content', 'created_at', 'forum_thread_id', 'emailed')

    def __init__(self, id, caption, description, content, created_at, forum_thread_id, emailed):
        self.id = id
        self.caption = caption
        self.description = description
        self.content = content
        self.created_at = created_at
        self.forum_thread_id = forum_thread_id
        self.emailed = emailed

    @property
    def html_description(self):
        return markdown.markdown(self.description)

    @property
    def html_content(self):
        return markdown.markdown(self.content)
