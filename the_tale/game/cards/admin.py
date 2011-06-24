# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Card, CardsQueueItem

admin.site.register(Card)

admin.site.register(CardsQueueItem)
