# coding: utf-8

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'clean database'

    def handle(self, *args, **options):
        from common.postponed_tasks.prototypes import PostponedTaskPrototype
        from forum.prototypes import SubCategoryReadInfoPrototype, ThreadReadInfoPrototype
        from post_service.prototypes import MessagePrototype

        PostponedTaskPrototype.remove_old_tasks()

        ThreadReadInfoPrototype.remove_old_infos()
        SubCategoryReadInfoPrototype.remove_old_infos()

        MessagePrototype.remove_old_messages()
