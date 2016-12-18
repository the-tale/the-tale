# coding: utf-8

from dext.views import resource_patterns

from the_tale.common.postponed_tasks.views import PostponedTaskResource

urlpatterns = resource_patterns(PostponedTaskResource)
