# -*- coding: utf-8 -*-

from django.http import Http404
from django.core.urlresolvers import reverse

from dext.views.resources import handler

from common.utils.resources import Resource

from cms.models import Page


class CMSResource(Resource):

    def initialize(self, slug='', section=None, *args, **kwargs):
        super(CMSResource, self).initialize(*args, **kwargs)

        if section is None:
            raise Http404

        self.slug = slug
        self.section = section

    @property
    def page(self):
        if not hasattr(self, '_page'):
            try:
                self._page = Page.objects.get(slug=self.slug, active=True)
            except Page.DoesNotExist:
                self._page = None
        return self._page

    @handler('', method='get')
    def index(self):

        if self.page is not None:
            return self.template(self.section.template_page)

        try:
            first_page = Page.objects.filter(section=self.section.id, active=True).order_by('order')[0]
        except:
            raise Http404

        return self.redirect(reverse('cms:%s:page' % first_page.section, args=[first_page.slug]))


    @handler('#slug', name='page', method='get')
    def show_page(self):

        if self.page is None:
            raise Http404

        return self.template(self.section.template_page)
