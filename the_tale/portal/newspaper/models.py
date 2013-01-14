# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

NEWSPAPER_EVENT_TYPE = create_enum('NEWSPAPER_EVENT_TYPE', (('BILL_CREATED', 0, u'закон выдвинут'),
                                                            ('BILL_EDITED', 1, u'закон отредактирован'),
                                                            ('BILL_PROCESSED', 2, u'закон обработан'),
                                                            ('HERO_OF_THE_DAY', 3, u'герой дня'),
                                                            ('BILL_REMOVED', 4, u'закон удалён'),) )

NEWSPAPER_EVENT_SECTION = create_enum('NEWSPAPER_EVENT_SECTION', (('BILLS', 0, u'законы'),
                                                                  ('HERO_OF_THE_DAY', 1, u'герой дня')) )


class NewspaperEvent(models.Model):

    section = models.IntegerField(null=False, choices=NEWSPAPER_EVENT_SECTION._CHOICES, db_index=True)

    type = models.IntegerField(null=True, choices=NEWSPAPER_EVENT_TYPE._CHOICES, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    created_at_turn = models.IntegerField(null=False)

    data = models.TextField(default=u'{}')
