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


render = postmarkup.create(use_pygments=False)
render.tag_factory.add_tag(SpoilerTag, 'spoiler')


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
</div>
'''

    def html(self, bound_field):
        return jinja2.Markup(bound_field.label_tag()) + jinja2.Markup(self.command_line) + jinja2.Markup(bound_field) + bound_field.errors_container
