# coding: utf-8

from django.core.urlresolvers import reverse

from dext.jinja2.decorators import jinjaglobal

from accounts import logic

@jinjaglobal
def login_url(next_url=''):
    return logic.login_url(next_url)

@jinjaglobal
def logout_url():
    return reverse('accounts:auth:logout')
