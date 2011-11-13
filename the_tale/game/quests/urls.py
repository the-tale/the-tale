# coding: utf-8

from django_next.views.dispatcher import resource_patterns
from .views import QuestsResource

urlpatterns = resource_patterns(QuestsResource)
