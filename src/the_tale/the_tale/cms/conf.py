# coding: utf-8

from dext.common.utils.app_settings import app_settings

class Section(object):

    def __init__(self, id_, caption, url, template_page):
        self.id = id_
        self.caption = caption
        self.url = url
        self.template_page = template_page


cms_settings = app_settings('CMS',
                            SECTIONS=(Section('test', 'Тест', 'cms/test/', 'cms/test_page.html'),
                                      Section('world', 'Мифология', 'guide/world/', 'guide/cms_page.html'),
                                      Section('development', 'Разработка', 'guide/development/', 'guide/cms_page.html'))
    )
