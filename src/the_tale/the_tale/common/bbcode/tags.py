
import smart_imports

smart_imports.all()


class SpoilerTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super().__init__(name, inline=False)
        self.tag_key = 'SpoilerTag.nest_level'

    def render_open(self, parser, node_index):
        parser.tag_data[self.tag_key] = parser.tag_data.setdefault(self.tag_key, 0) + 1

        if self.params:
            caption = self.params.strip()
        else:
            caption = 'спойлер'

        return '''
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
        return '</div></div></div></div>'


class SafeSpoilerTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super().__init__(name, inline=False)
        self.tag_key = 'SafeSpoilerTag.nest_level'

    def render_open(self, parser, node_index):
        parser.tag_data[self.tag_key] = parser.tag_data.setdefault(self.tag_key, 0) + 1

        if self.params:
            caption = self.params.strip()
        else:
            caption = 'спойлер'

        return '--------------%(caption)s--------------<br/>' % {'caption': caption}

    def render_close(self, parser, node_index):
        parser.tag_data[self.tag_key] -= 1
        return '<br/>--------------'


class YoutubeTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super().__init__(name, inline=False, auto_close=True)
        self.tag_key = 'YoutubeTag.nest_level'

    def render_open(self, parser, node_index):
        return '<iframe width="560" height="315" src="https://www.youtube.com/embed/{code}?rel=0" frameborder="0" allowfullscreen></iframe>'.format(code=self.params.strip())

    def render_close(self, parser, node_index):
        return ''


class HRTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super().__init__(name, inline=False, auto_close=True)
        self.tag_key = 'HRTag.nest_level'

    def render_open(self, parser, node_index):
        return '<hr/>'

    def render_close(self, parser, node_index):
        return ''


class LeftSquareBracketTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super().__init__(name, inline=True, auto_close=True)
        self.tag_key = 'LeftSquareBracketTag.nest_level'

    def render_open(self, parser, node_index):
        return '&#91;'

    def render_close(self, parser, node_index):
        return ''


class RightSquareBracketTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super().__init__(name, inline=True, auto_close=True)
        self.tag_key = 'RightSquareBracketTag.nest_level'

    def render_open(self, parser, node_index):
        return '&#93;'

    def render_close(self, parser, node_index):
        return ''


class LinkTag(postmarkup.LinkTag):
    _safe_chars = postmarkup.LinkTag._safe_chars | frozenset('+')


class RedLineTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super().__init__(name, inline=True, auto_close=True)
        self.tag_key = 'RedLineTag.nest_level'

    def render_open(self, parser, node_index):
        return '&nbsp;&nbsp;&nbsp;&nbsp;'

    def render_close(self, parser, node_index):
        return ''


def tag(id, tag_class, example, args=None, kwargs=None, name=None, single=False):
    if name is None:
        name = id

    return (name,
            id,
            tag_class,
            args if args is not None else (),
            kwargs if kwargs is not None else {},
            example,
            single)


class TAG(rels.Relation):
    name = rels.Column(primary=True, no_index=True, primary_checks=True)
    value = rels.Column(no_index=True, unique=False)
    tag_class = rels.Column(unique=False)
    args = rels.Column(unique=False, single_type=False)
    kwargs = rels.Column(unique=False)
    example = rels.Column(single_type=False)
    single = rels.Column(unique=False)

    records = (tag('b', postmarkup.SimpleTag, '<strong>жирный</strong>', args=['strong']),
               tag('i', postmarkup.SimpleTag, '<i>курсив</i>', args=['em']),
               tag('u', postmarkup.SimpleTag, '<u>подчёркнутый</u>', args=['u']),
               tag('s', postmarkup.SimpleTag, '<strike>зачёркнутый</strike>', args=['strike']),
               tag('quote', postmarkup.QuoteTag, '<blockquote>цитата</blockquote>'),
               tag('img', postmarkup.ImgTag, '[img]https://адрес картинки[/img]'),
               tag('url', LinkTag, '[url="https://адрес"]текст[/url]', kwargs={'annotate_links': False}),
               tag('spoiler', SpoilerTag, '[spoiler="опциональный текст"]скрытое содержимое[/spoiler]'),
               tag('list', postmarkup.ListTag, '[list]список[/list]'),
               tag('*', postmarkup.ListItemTag, '[*]элемент списка', name='list_id', single=True),
               tag('hr', HRTag, '[hr] — горизонтальная линия', single=True),
               tag('lsb', LeftSquareBracketTag, '[lsb] — «[» левая квадратная скобка', single=True),
               tag('rsb', RightSquareBracketTag, '[rsb] — «]» правая квадратная скобка', single=True),
               tag('rl', RedLineTag, '[rl] — красная строка (отступ)', single=True),
               tag('youtube', YoutubeTag, '[youtube=code] — видео с Youtube', single=True),
               tag('spoiler', SafeSpoilerTag, None, name='safe_spoiler'),
               tag('center', postmarkup.CenterTag, 'отобразить текст по центру'),
               tag('size', postmarkup.SizeTag, '[size=10]размер текста[/size]'),
               tag('color', postmarkup.ColorTag, '[color=#004455]цвет текста[/color]'),
               tag('pre', postmarkup.SimpleTag, '<pre>без форматирования</pre>', args=['pre']))
