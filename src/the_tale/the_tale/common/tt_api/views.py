
import smart_imports

smart_imports.all()


class RequestProcessor(dext_views.BaseViewProcessor):
    ARG_REQUEST_CLASS = dext_views.ProcessorArgument()

    def preprocess(self, context):
        try:
            context.tt_request = self.request_class.FromString(context.django_request.body)
        except:
            raise dext_views.ViewError(code='common.wrong_tt_post_data',
                                       message='Переданы неверные данные',
                                       http_status=dext_relations.HTTP_STATUS.INTERNAL_SERVER_ERROR)


class SecretProcessor(dext_views.BaseViewProcessor):
    ARG_SECRET = dext_views.ProcessorArgument()

    def preprocess(self, context):
        if context.tt_request.secret != self.secret:
            raise dext_views.ViewError(code='common.wrong_tt_secret',
                                       message='У Вас нет прав для проведения данной операции',
                                       http_status=dext_relations.HTTP_STATUS.INTERNAL_SERVER_ERROR)
