# coding: utf-8
import datetime

from django.core.management.base import BaseCommand

from the_tale.forum.prototypes import ThreadPrototype


class Command(BaseCommand):

    help = 'update subcategories and threads'

    def handle(self, *args, **options):

        threads_query = ThreadPrototype._db_filter(updated_at__gt=datetime.datetime.now() - datetime.timedelta(days=3))

        threads_count = threads_query.count()

        for i, thread in enumerate(ThreadPrototype.from_query(threads_query.order_by('id'))):
            print 'update thread: %d (%d) from %d' % (i+1, thread.id, threads_count)
            thread.update()
            thread.save()
