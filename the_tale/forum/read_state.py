# coding: utf-8
import datetime

from the_tale.common.utils.decorators import lazy_property

from the_tale.forum.prototypes import ThreadReadInfoPrototype, SubCategoryReadInfoPrototype
from the_tale.forum.conf import forum_settings
from the_tale.forum.exceptions import ForumException


class ReadState(object):

    def __init__(self, account, subcategory, threads=()):
        self._account = account
        self._threads = threads
        self._subcategory = subcategory

        if self._subcategory is not None:
            if any(thread.subcategory_id != self._subcategory.id for thread in  self._threads):
                raise ForumException(u'ReadState can be constructed only with threads from one subcategory')

        if not self._account.is_authenticated() or self._subcategory is None:
            self.subcategory_read_info = None
        else:
            self.subcategory_read_info =  SubCategoryReadInfoPrototype.get_for(account_id=self._account.id, subcategory_id=self._subcategory.id)

    @lazy_property
    def threads_read_info(self):
        if not self._account.is_authenticated():
            return {}

        return ThreadReadInfoPrototype.get_threads_info(account_id=self._account.id,
                                                        threads_ids=[thread.id for thread in self._threads])

    def thread_has_new_messages(self, thread):
        if not self._account.is_authenticated():
            return False

        if thread.updated_at + datetime.timedelta(seconds=forum_settings.UNREAD_STATE_EXPIRE_TIME) < datetime.datetime.now():
            return False

        read_at = self.threads_read_info.get(thread.id, self._account.created_at)

        if self.subcategory_read_info is not None:
            read_at = max(self.subcategory_read_info.all_read_at, read_at)

        return thread.updated_at > read_at

    def thread_is_new(self, thread):
        if not self._account.is_authenticated():
            return False

        if thread.author.id == self._account.id:
            return False

        if thread.created_at + datetime.timedelta(seconds=forum_settings.UNREAD_STATE_EXPIRE_TIME) < datetime.datetime.now():
            return False

        read_at = self.threads_read_info.get(thread.id, self._account.created_at)

        if self.subcategory_read_info is not None:
            read_at = max(self.subcategory_read_info.read_at, read_at)

        return thread.created_at > read_at
