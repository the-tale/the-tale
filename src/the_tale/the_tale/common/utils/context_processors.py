
import smart_imports

smart_imports.all()


def common(request):
    context = {'settings': django_settings}

    if request is not None:
        context['request'] = request
        context['csrf_input'] = django_template_backends_utils.csrf_input_lazy(request)
        context['csrf_token'] = django_template_backends_utils.csrf_token_lazy(request)

    return context
