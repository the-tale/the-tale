# coding: utf-8

from dext.views import resource_patterns

from common.postponed_tasks.views import PostponedTaskResource

urlpatterns = resource_patterns(PostponedTaskResource)
