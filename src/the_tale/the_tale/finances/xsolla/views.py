
import smart_imports

smart_imports.all()


logger = logging.getLogger(__name__)


class XsollaResource(utils_resources.Resource):

    def initialize(self, *args, **kwargs):
        super(XsollaResource, self).initialize(*args, **kwargs)

    def log(self, name):
        message = '%(name)s\tfrom "%(referer)s" with %(arguments)r' % {'name': name,
                                                                       'referer': self.user_ip,
                                                                       'arguments': self.request.GET}
        logger.info(message)

    def create_answer(self, check_result):
        answer = '''<?xml version="1.0" encoding="windows-1251"?>
<response>
    <result>%(xsolla_result)s</result>
    <comment>%(comment)s</comment>
</response>
''' % {'xsolla_result': check_result.xsolla_result.value, 'comment': check_result.text}
        logger.info(answer)
        return self.xml(answer.encode('cp1251'), charset='cp1251')

    def create_check_answer(self, check_result):
        return self.create_answer(check_result)

    def create_pay_answer(self, pay_result, xsolla_id, internal_id, sum):
        answer = '''<?xml version="1.0" encoding="windows-1251"?>
<response>
    <id>%(xsolla_id)s</id>
    <id_shop>%(internal_id)s</id_shop>
    <sum>%(sum)s</sum>
    <result>%(xsolla_result)s</result>
    <comment>%(comment)s</comment>
</response>
''' % {'xsolla_result': pay_result.xsolla_result.value,
            'comment': pay_result.text,
            'xsolla_id': xsolla_id,
            'internal_id': internal_id,
            'sum': sum}
        logger.info(answer)
        return self.xml(answer.encode('cp1251'), charset='cp1251')

    def create_cancel_answer(self):
        return self.create_answer(relations.CANCEL_RESULT.NOT_SUPPORTED)

    @old_views.handler('command', method='get')
    def command(self,
                command=None, md5=None,
                v1=None, v2=None, v3=None,
                id=None, sum=None, test=None, date=None):
        try:
            self.log(command)

            if self.user_ip not in conf.settings.ALLOWED_IPS:
                return self.create_answer(relations.COMMON_RESULT.DISALLOWED_IP)

            try:
                command = relations.COMMAND_TYPE(command)
            except:
                return self.create_answer(relations.COMMON_RESULT.WRONG_COMMAND)

            if command.is_CHECK:
                return self.create_check_answer(logic.check_user(command=command,
                                                                 external_md5=md5,
                                                                 v1=v1,
                                                                 v2=v2,
                                                                 v3=v3))
            elif command.is_PAY:
                pay_result, internal_id = logic.pay(command=command,
                                                    external_md5=md5,
                                                    v1=v1,
                                                    v2=v2,
                                                    v3=v3,
                                                    id=id,
                                                    sum=sum,
                                                    test=test,
                                                    date=date,
                                                    request_url=self.request.build_absolute_uri())
                return self.create_pay_answer(pay_result, xsolla_id=id, internal_id=internal_id, sum=sum)

            elif command.is_CANCEL:
                return self.create_cancel_answer()
        except:
            logger.error('XSOLLA command exception',
                         exc_info=sys.exc_info(),
                         extra={})
            return self.create_answer(relations.COMMON_RESULT.UNKNOWN_ERROR)

    @utils_decorators.superuser_required()
    @utils_decorators.debug_required
    @old_views.handler('debug', method='get')
    def debug(self, id='13', sum='666', test='0', v1='test@test.com'):
        check_url = utils_urls.url('bank:xsolla:command',
                                  command=relations.COMMAND_TYPE.CHECK.value,
                                  v1=v1,
                                  md5=logic.check_user_md5(relations.COMMAND_TYPE.CHECK, v1))

        pay_url = utils_urls.url('bank:xsolla:command',
                                command=relations.COMMAND_TYPE.PAY.value,
                                v1=v1,
                                id=id,
                                sum=sum,
                                test=test,
                                md5=logic.pay_md5(relations.COMMAND_TYPE.PAY, v1, id))

        cancel_url = utils_urls.url('bank:xsolla:command',
                                   command=relations.COMMAND_TYPE.CANCEL.value,
                                   id=id,
                                   md5=logic.cancel_md5(relations.COMMAND_TYPE.CANCEL, id))

        return self.json_ok(data={'check_url': check_url,
                                  'pay_url': pay_url,
                                  'cancel_url': cancel_url})
