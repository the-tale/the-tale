import smart_imports

smart_imports.all()


class BBField(utils_fields.TextField):

    def __init__(self, renderer=renderers.default, **kwargs):
        super().__init__(**kwargs)
        self.renderer = renderer

    def html(self, bound_field):
        html = f"""
<div id="pgf-bbfield-{uuid.uuid4().hex}" class="pgf-bbfield bbfield">
  {bound_field.label_tag()}
  <div class="pgf-edit-content">
    {self.renderer.html_command_line()}
    {bound_field}
  </div>
  <div class="pgf-preview-content pgf-hidden bbfield-preview pgf-scrollable easy-block"></div>
  {bound_field.errors_container}
  <div class="widget">
    <button type="button" class="btn pgf-preview-button">Предпросмотр</button>
    <button type="button" class="btn pgf-edit-button pgf-hidden">Редактировать</button>
  </div>
  <br/>
</div>

"""
        return jinja2.Markup(html)
