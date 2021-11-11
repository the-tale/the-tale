
import smart_imports

smart_imports.all()


import jinja2  # импортируем модуль из глобального окружения


class FormsException(Exception):
    pass


HTML_WIDGET_WRAPPER = '<div class="pgf-widget control-group">%(content)s</div>'
HTML_ERROR_CONTAINER = '<div class="pgf-form-field-marker-%(name)s pgf-error-container alert alert-error pgf-hidden"></div>'


def errors_container(self):
    return jinja2.Markup(HTML_ERROR_CONTAINER % {'name': self.name})


def html(self):

    if hasattr(self.field, 'html'):
        return jinja2.Markup(self.field.html(self))

    return (jinja2.Markup(self.label_tag(label_suffix=getattr(self.field, 'LABEL_SUFFIX', None))) +
            jinja2.Markup(self) +
            self.errors_container)


def widget(self):
    template = jinja2.Markup(HTML_WIDGET_WRAPPER)
    html =  template % {'content': self.html}
    html = jinja2.Markup(html)
    return html


django_forms.boundfield.BoundField.html = property(html)
django_forms.boundfield.BoundField.errors_container = property(errors_container)
django_forms.boundfield.BoundField.widget = property(widget)


class CleanedDataAccessor(object):

    def __init__(self, form):
        self.form = form

    def __getattr__(self, name):
        if name in self.form.cleaned_data:
            return self.form.cleaned_data[name]
        raise FormsException('can not get cleaned data - wrong field name "%s"' % name)

    @property
    def data(self):
        return self.form.cleaned_data


class Form(django_forms.Form):

    @property
    def errors_container(self):
        return jinja2.Markup('<div class="pgf-form-marker pgf-error-container alert alert-error pgf-hidden"></div>')

    @property
    def errors(self):

        errors = super(Form, self).errors

        for name, field in list(self.fields.items()):

            if not hasattr(field, 'get_extra_errors'):
                continue

            value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))

            extra_errors = field.get_extra_errors(value)

            errors.update(extra_errors)

        return errors

    @property
    def c(self):
        if not hasattr(self, '_c'):
            self._c = CleanedDataAccessor(self)
        return self._c
