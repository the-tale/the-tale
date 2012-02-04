# coding: utf-8

from dext.views.dispatcher import resource_patterns
from .views import AngelsResource

urlpatterns = resource_patterns(AngelsResource)

