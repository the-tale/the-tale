

import smart_imports

smart_imports.all()


class AccessTokenAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'state', 'account', 'uid', 'created_at', 'application_name')
    list_filter = ('state',)


django_admin.site.register(models.AccessToken, AccessTokenAdmin)
