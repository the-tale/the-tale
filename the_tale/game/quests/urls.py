# coding: utf-8

from dext.views import resource_patterns
from .views import QuestsResource

urlpatterns = resource_patterns(QuestsResource)
