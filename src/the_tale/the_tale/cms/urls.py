# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.cms.views import CMSResource
from the_tale.cms.conf import cms_settings


urlpatterns = []

for section in cms_settings.SECTIONS:
    urlpatterns += [url(section.url, include(resource_patterns(CMSResource, args={'section': section}), namespace=section.id)) ]
