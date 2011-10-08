# coding: utf-8

from django_next.views.dispatcher import resource_patterns
from .views import AngelsResource

urlpatterns = resource_patterns(AngelsResource)

