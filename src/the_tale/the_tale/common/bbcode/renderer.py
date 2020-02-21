
import smart_imports

smart_imports.all()


class Renderer:
    __slots__ = ('tags', '_renderer')

    def __init__(self, tags):
        self.tags = tags

        self._renderer = postmarkup.create(include=[],
                                           use_pygments=False,
                                           annotate_links=False)

        for tag in tags:
            self._renderer.tag_factory.add_tag(tag.tag_class, tag.value, *tag.args, **tag.kwargs)

    def render(self, *args, **kwargs):
        try:
            kwargs['cosmetic_replace'] = False
            kwargs['encoding'] = 'utf-8'
            return self._renderer.render_to_html(*args, **kwargs)
        except Exception:
            return 'Текст нельзя отформатировать. Возможно Вы ошиблись при вводе тегов.'

    def html_command_line(self):
        lines = ['<div class="pgf-bb-command-line command-line">']

        for tag in self.tags:
            single = 'data-single="true"' if tag.single else ''
            line = f'<a class="pgf-bb-command" href="#" data-tag="{tag.value}" {single} rel="tooltip" title=\'{tag.example}\'>[{tag.value}]</a>'
            lines.append(line)

        lines.append('</div>')

        return '\n'.join(lines)
