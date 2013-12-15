# coding: utf-8
import datetime

from the_tale.common.utils.decorators import lazy_property

from the_tale.forum.prototypes import ThreadReadInfoPrototype, SubCategoryReadInfoPrototype, ThreadPrototype
from the_tale.forum.conf import forum_settings


class ReadState(object):

    def __init__(self, account):
        self._account = account

        # can not make lazy properties, since some read_infos can be created after this object was constructed
        self.subcategories_read_info = self.get_subcategories_read_info()
        self.threads_read_info = self.get_threads_read_info()

    def get_subcategories_read_info(self):
        if not self._account.is_authenticated():
            return {}

        return SubCategoryReadInfoPrototype.get_subcategories_info(account_id=self._account.id)

    def get_threads_read_info(self):
        if not self._account.is_authenticated():
            return {}

        return ThreadReadInfoPrototype.get_threads_info(account_id=self._account.id)

    @lazy_property
    def threads_info(self):
        if not self._account.is_authenticated():
            return {}

        time_barrier = datetime.datetime.now() - datetime.timedelta(seconds=forum_settings.UNREAD_STATE_EXPIRE_TIME)

        return {thread.id: thread for thread in ThreadPrototype.from_query(ThreadPrototype._db_filter(updated_at__gt=time_barrier))}

    def thread_has_new_messages(self, thread):
        if not self._account.is_authenticated():
            return False

        if thread.updated_at + datetime.timedelta(seconds=forum_settings.UNREAD_STATE_EXPIRE_TIME) < datetime.datetime.now():
            return False

        thread_read_info = self.threads_read_info.get(thread.id)
        read_at = thread_read_info.read_at if thread_read_info else self._account.created_at

        subcategory_read_info = self.subcategories_read_info.get(thread.subcategory_id)

        if subcategory_read_info is not None:
            read_at = max(subcategory_read_info.all_read_at, read_at)

        return thread.updated_at > read_at

    def thread_is_new(self, thread):
        if not self._account.is_authenticated():
            return False

        if thread.author.id == self._account.id:
            return False

        if thread.created_at + datetime.timedelta(seconds=forum_settings.UNREAD_STATE_EXPIRE_TIME) < datetime.datetime.now():
            return False

        thread_read_info = self.threads_read_info.get(thread.id)
        read_at = thread_read_info.read_at if thread_read_info else self._account.created_at

        subcategory_read_info = self.subcategories_read_info.get(thread.subcategory_id)

        if subcategory_read_info is not None:
            read_at = max(subcategory_read_info.read_at, read_at)

        return thread.created_at > read_at


    # TODO: we have minor bug here
    # user can got to thread page (and update thread_read_info)
    # without going into subcategory page (and updating subcategory_read_info info)
    # => user can read all threads, but subcategory will be displayed as unread
    def subcategory_has_new_messages(self, subcategory):

        if not self._account.is_authenticated():
            return False

        subcategory_read_info = self.subcategories_read_info.get(subcategory.id)

        if subcategory_read_info is None:
            return True

        if subcategory.updated_at + datetime.timedelta(seconds=forum_settings.UNREAD_STATE_EXPIRE_TIME) < datetime.datetime.now():
            return False

        return any(self.thread_has_new_messages(thread)
                   for thread in self.threads_info.values()
                   if thread.subcategory_id == subcategory.id)
