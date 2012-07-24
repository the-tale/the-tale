# coding: utf-8

from dext.utils.app_settings import app_settings

class Section(object):

    def __init__(self, id_, caption, url, template_page):
        self.id = id_
        self.caption = caption
        self.url = url
        self.template_page = template_page


cms_settings = app_settings('CMS',
                            SECTIONS=(Section('test', u'Тест', 'cms/test/', 'cms/test_page.html'),
                                      Section('world', u'Мифология', 'guide/world/', 'guide/cms_page.html'))
    )
