# coding: utf-8

from django.core.urlresolvers import reverse_lazy

from dext.common.utils.app_settings import app_settings

guide_settings = app_settings('GUIDE',
                               API_FORUM_THREAD=reverse_lazy('forum:threads:show', args=[939]) )
