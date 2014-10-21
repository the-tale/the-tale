# coding: utf-8
import uuid
import jinja2

import postmarkup

from dext.forms import fields


class SpoilerTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super(SpoilerTag, self).__init__(name, inline=False)
        self.tag_key = u'SpoilerTag.nest_level'

    def render_open(self, parser, node_index):
        parser.tag_data[self.tag_key] = parser.tag_data.setdefault(self.tag_key, 0) + 1

        if self.params:
            caption = self.params.strip()
        else:
            caption = u'спойлер'

        return u'''
<div class="accordion" id="pgf-spoiler-%(accordion_id)s">
  <div class="accordion-group">
    <div class="accordion-heading">
      <a class="accordion-toggle collapsed" data-toggle="collapse" data-parent="#pgf-spoiler%(accordion_id)s" href="#pgf-spoiler-element-%(accordion_id)s">
      %(caption)s
      </a>
    </div>
    <div id="pgf-spoiler-element-%(accordion_id)s" class="accordion-body collapse" style="height: 0px;">
      <div class="accordion-inner">
''' % {'accordion_id': uuid.uuid4().hex,
       'caption': caption}

    def render_close(self, parser, node_index):
        parser.tag_data[self.tag_key] -= 1
        return u'</div></div></div></div>'


class SafeSpoilerTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super(SafeSpoilerTag, self).__init__(name, inline=False)
        self.tag_key = u'SafeSpoilerTag.nest_level'

    def render_open(self, parser, node_index):
        parser.tag_data[self.tag_key] = parser.tag_data.setdefault(self.tag_key, 0) + 1

        if self.params:
            caption = self.params.strip()
        else:
            caption = u'спойлер'

        return u'--------------%(caption)s--------------<br/>' % {'caption': caption}

    def render_close(self, parser, node_index):
        parser.tag_data[self.tag_key] -= 1
        return u'<br/>--------------'


class HRTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super(HRTag, self).__init__(name, inline=False)
        self.tag_key = u'HRTag.nest_level'

    def render_open(self, parser, node_index):
        return u'<hr/>'

    def render_close(self, parser, node_index):
        return u''


class LeftSquareBracketTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super(LeftSquareBracketTag, self).__init__(name, inline=False)
        self.tag_key = u'LeftSquareBracketTag.nest_level'

    def render_open(self, parser, node_index):
        return u'['

    def render_close(self, parser, node_index):
        return u''


class RightSquareBracketTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super(RightSquareBracketTag, self).__init__(name, inline=False)
        self.tag_key = u'RightSquareBracketTag.nest_level'

    def render_open(self, parser, node_index):
        return u']'

    def render_close(self, parser, node_index):
        return u''



_renderer = postmarkup.create(use_pygments=False, annotate_links=False)
_renderer.tag_factory.add_tag(SpoilerTag, 'spoiler')
_renderer.tag_factory.add_tag(HRTag, 'hr')
_renderer.tag_factory.add_tag(LeftSquareBracketTag, 'lsb')
_renderer.tag_factory.add_tag(RightSquareBracketTag, 'rsb')


def render(*argv, **kwargs):
    try:
        return _renderer.render_to_html(*argv, **kwargs)
    except:
        return u'Текст нельзя отформатировать. Возможно Вы ошиблись при вводе тегов.'


_safe_renderer = postmarkup.create(use_pygments=False, annotate_links=False)
_safe_renderer.tag_factory.add_tag(SafeSpoilerTag, 'spoiler')
_safe_renderer.tag_factory.add_tag(HRTag, 'hr')

def safe_render(*argv, **kwargs):
    try:
        return _safe_renderer.render_to_html(*argv, **kwargs)
    except:
        return u'Текст нельзя отформатировать. Возможно Вы ошиблись при вводе тегов.'



class BBField(fields.TextField):

    @property
    def command_line(self):
        return u'''
<div class="pgf-bb-command-line command-line">
<a class="pgf-bb-command" href="#" data-tag="b" rel="tooltip" title="<strong>жирный</strong>">[b]</a>
<a class="pgf-bb-command" href="#" data-tag="i" rel="tooltip" title="<i>курсив</i>">[i]</a>
<a class="pgf-bb-command" href="#" data-tag="u" rel="tooltip" title="<u>подчёрнутый</u>">[u]</a>
<a class="pgf-bb-command" href="#" data-tag="s" rel="tooltip" title="<strike>зачёркнутый</strike>">[s]</a>
<a class="pgf-bb-command" href="#" data-tag="quote" rel="tooltip" title="<blockquote>цитата</blockquote>">[quote]</a>
<a class="pgf-bb-command" href="#" data-tag="img" rel="tooltip" title="[img]http://адрес картинки[/img]">[img]</a>
<a class="pgf-bb-command" href="#" data-tag="url" rel="tooltip" title=\'[url="http://адрес"]текст[/url]\'>[url]</a>
<a class="pgf-bb-command" href="#" data-tag="spoiler" rel="tooltip" title=\'[spoiler="опциональный текст"]скрытое содержимое[/spoiler]\'>[spoiler]</a>
<a class="pgf-bb-command" href="#" data-tag="list" rel="tooltip" title="[list]список[/list]">[list]</a>
<a class="pgf-bb-command" href="#" data-tag="*" data-single="true" rel="tooltip" title="[*]элемент списка">[*]</a>
<a class="pgf-bb-command" href="#" data-tag="hr" data-single="true" rel="tooltip" title="[hr] — вертикальная линия">[hr]</a>
<a class="pgf-bb-command" href="#" data-tag="lsb" data-single="true" rel="tooltip" title="[lsb] — «[» левая квадратная скобка">[lsb]</a>
<a class="pgf-bb-command" href="#" data-tag="rsb" data-single="true" rel="tooltip" title="[rsb] — «]» правая квадратная скобка">[rsb]</a>
</div>
'''

    def html(self, bound_field):
        html = u"""
<div id="pgf-bbfield-%(field_id)s" class="pgf-bbfield bbfield">
  %(label)s
  <div class="pgf-edit-content">
    %(command_line)s
    %(bound_field)s
  </div>
  <div class="pgf-preview-content pgf-hidden bbfield-preview pgf-scrollable block white"></div>
  %(errors_container)s
  <div class="widget">
    <button type="button" class="btn pgf-preview-button">Предпросмотр</button>
    <button type="button" class="btn pgf-edit-button pgf-hidden">Редактировать</button>
  </div>
  <br/>
</div>

""" % {'field_id': uuid.uuid4().hex,
       'label': bound_field.label_tag(),
       'command_line': self.command_line,
       'bound_field': bound_field,
       'errors_container': bound_field.errors_container}

        return jinja2.Markup(html)
