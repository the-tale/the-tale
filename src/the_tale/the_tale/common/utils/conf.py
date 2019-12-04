
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('UTILS',
                                           PID_DIRECTORY='/tmp',
                                           PID_DIRECTORY_MODE=0o755,
                                           DIALOG_ERROR_TEMPLATE='dialog_error.html',
                                           PAGE_ERROR_TEMPLATE='error.html',
                                           DEFAUL_ERROR_MESSAGE='Произошла ошибка, мы уже работаем над её устранением, повторите попытку через некоторое время')
