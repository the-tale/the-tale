# coding: utf-8
from dext.views.dispatcher import resource_patterns
from .views import AbilitiesResource

urlpatterns = resource_patterns(AbilitiesResource)


