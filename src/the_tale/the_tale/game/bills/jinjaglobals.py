
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def bills_menu_types():
    return sorted(bills.BILLS_BY_ID.items(), key=lambda x: x[1].type.text)
