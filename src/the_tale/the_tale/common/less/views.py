
import smart_imports

smart_imports.all()


@django_decorators.cache.never_cache
def less_compiler(request, path):

    file_path = os.path.join(django_settings.LESS_FILES_DIR, path + '.less')

    if not os.path.exists(file_path):
        file_path = os.path.join(django_settings.LESS_FILES_DIR, path + '.css')

    (out, err) = subprocess.Popen(["lessc", file_path], stdout=subprocess.PIPE).communicate()

    return django_http.HttpResponse(out, content_type='text/css; charset=utf-8')
