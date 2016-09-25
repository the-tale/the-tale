# coding: utf-8

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'clean database'

    def handle(self, *args, **options):
        from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype
        from the_tale.forum.prototypes import SubCategoryReadInfoPrototype, ThreadReadInfoPrototype
        from the_tale.post_service.prototypes import MessagePrototype

        PostponedTaskPrototype.remove_old_tasks()

        ThreadReadInfoPrototype.remove_old_infos()
        SubCategoryReadInfoPrototype.remove_old_infos()

        MessagePrototype.remove_old_messages()
