# coding: utf-8

from django_next.views.dispatcher import resource_patterns

from .views import ForumResource

urlpatterns = resource_patterns(ForumResource)

