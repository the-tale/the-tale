
import smart_imports

smart_imports.all()


def check_user_md5(command, v1):
    md5_hash = hashlib.md5()
    md5_hash.update(command.value.encode('utf-8'))
    md5_hash.update(v1.encode('utf-8'))
    md5_hash.update(conf.settings.SECRET_KEY.encode('utf-8'))
    return md5_hash.hexdigest()


def check_user(command, external_md5, v1, v2, v3):

    if v1 is None:
        return relations.CHECK_USER_RESULT.NOT_SPECIFIED_V1

    if not external_md5 or check_user_md5(command, v1).lower() != external_md5.lower():
        return relations.CHECK_USER_RESULT.WRONG_MD5

    if bank_logic.get_account_id(email=v1) is None:
        return relations.CHECK_USER_RESULT.USER_NOT_EXISTS

    return relations.CHECK_USER_RESULT.USER_EXISTS


def pay_md5(command, v1, id):
    md5_hash = hashlib.md5()
    md5_hash.update(command.value.encode('utf-8'))
    md5_hash.update(v1.encode('utf-8'))
    md5_hash.update(id.encode('utf-8'))
    md5_hash.update(conf.settings.SECRET_KEY.encode('utf-8'))
    return md5_hash.hexdigest()


def pay(command, external_md5, v1, v2, v3, id, sum, test, date, request_url):

    if v1 is None:
        return relations.PAY_RESULT.NOT_SPECIFIED_V1, None

    if id is None:
        return relations.PAY_RESULT.NOT_SPECIFIED_ID, None

    if sum is None:
        return relations.PAY_RESULT.NOT_SPECIFIED_SUM, None

    if not external_md5 or pay_md5(command, v1, id).lower() != external_md5.lower():
        return relations.PAY_RESULT.WRONG_MD5, None

    invoice = prototypes.InvoicePrototype.pay(v1=v1,
                                              v2=v2,
                                              v3=v3,
                                              xsolla_id=id,
                                              payment_sum=sum,
                                              test=test,
                                              date=date,
                                              request_url=request_url)

    return invoice.pay_result, invoice.id


def cancel_md5(command, id):
    md5_hash = hashlib.md5()
    md5_hash.update(command.value.encode('utf-8'))
    md5_hash.update(id.encode('utf-8'))
    md5_hash.update(conf.settings.SECRET_KEY.encode('utf-8'))
    return md5_hash.hexdigest()
