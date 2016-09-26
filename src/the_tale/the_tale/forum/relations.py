# coding: utf-8

from rels.django import DjangoEnum


class MARKUP_METHOD(DjangoEnum):
    records = ( ('POSTMARKUP', 0, 'bb-code'),
                 ('MARKDOWN', 1, 'markdown') )


class POST_REMOVED_BY(DjangoEnum):
    records = ( ('AUTHOR', 0, 'удалён автором'),
                 ('THREAD_OWNER', 1, 'удалён владельцем темы'),
                 ('MODERATOR', 2, 'удалён модератором') )


class POST_STATE(DjangoEnum):
    records = ( ('DEFAULT', 0, 'видим'),
                 ('REMOVED', 1, 'удалён') )
