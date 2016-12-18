# coding: utf-8

import datetime

from django.core.management.base import BaseCommand

from ... import conf
from ... import prototypes
from ... import relations
from ... import logic


class Command(BaseCommand):

    help = 'clean removed templates'

    def handle(self, *args, **options):

        time_border = datetime.datetime.now() - datetime.timedelta(days=conf.linguistics_settings.REMOVED_TEMPLATE_TIMEOUT)

        for template_model in prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.REMOVED,
                                                                      updated_at__lt=time_border):
            logic.full_remove_template(prototypes.TemplatePrototype(template_model))
