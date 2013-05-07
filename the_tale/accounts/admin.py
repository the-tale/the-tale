# coding: utf-8

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _


from accounts.models import Account, ChangeCredentialsTask, Award, ResetPasswordTask


class AccountChangeForm(forms.ModelForm):
    nick = forms.RegexField( label=_("Username"), max_length=30, regex=r"^[\w.@+-]+$",
                             help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
                             error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = Account


    def __init__(self, *args, **kwargs):
        super(AccountChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return Account.objects.normalize_email(email) if email else None


class AccountAdmin(DjangoUserAdmin):
    form = AccountChangeForm

    list_display = ('id', 'email', 'nick', 'is_staff', 'last_login', 'created_at')
    ordering = ('-created_at',)

    search_fields = ('nick', 'email')
    fieldsets = ( (None, {'fields': ('nick', 'password')}),
                  (_('Personal info'), {'fields': ('email',)}),
                  (_('Permissions'), {'fields': ('is_fast',
                                                 'is_active',
                                                 'is_staff',
                                                 'is_superuser',
                                                 'groups',
                                                 'user_permissions')}),
                 (_('Important dates'), {'fields': ('last_login', 'active_end_at', 'premium_end_at')}),  )


class ChangeCredentialsTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'account', )
    list_filter= ('state',)


class AwardAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'type', 'created_at')
    list_filter= ('type',)

class ResetPasswordTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'is_processed', 'uuid', 'created_at')


admin.site.register(Account, AccountAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(ChangeCredentialsTask, ChangeCredentialsTaskAdmin)
admin.site.register(ResetPasswordTask, ResetPasswordTaskAdmin)
