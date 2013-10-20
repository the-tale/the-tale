# coding: utf-8

import re
import datetime

from django.core.urlresolvers import reverse_lazy

from dext.utils.app_settings import app_settings

guide_settings = app_settings('GUIDE',
                               API_FORUM_THREAD=reverse_lazy('forum:threads:show', args=[939]) )
