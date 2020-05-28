
import smart_imports

smart_imports.all()


class AccountChangeForm(django_forms.ModelForm):
    nick = django_forms.RegexField(label="Username", max_length=30, regex=r"^[\w.@+-]+$",
                                   help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
                                   error_messages={'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
    password = django_auth_forms.ReadOnlyPasswordHashField(label="Password",
                                                           help_text="Raw passwords are not stored, so there is no way to see "
                                                           "this user's password, but you can change the password "
                                                           "using <a href=\"password/\">this form</a>.")

    class Meta:
        model = models.Account
        fields = '__all__'

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
        return models.Account.objects.normalize_email(email) if email else None


class AccountAdmin(django_auth_admin.UserAdmin):
    form = AccountChangeForm

    list_display = ('id', 'email', 'nick', 'action_id', 'referral_of', 'referer_domain', 'last_login', 'created_at')
    ordering = ('-created_at',)

    search_fields = ('nick', 'email')
    fieldsets = ((None, {'fields': ('nick', 'password')}),
                 ('Personal info', {'fields': ('email',
                                               'referer_domain',
                                               'referer',
                                               'action_id')}),
                 ('Permissions', {'fields': ('is_fast',
                                             'is_bot',
                                             'is_active',
                                             'is_staff',
                                             'is_superuser',
                                             'groups',
                                             'user_permissions')}),
                 ('Settings', {'fields': ('personal_messages_subscription', 'news_subscription')}),
                 ('Data', {'fields': ('permanent_purchases',)}),
                 ('Important dates', {'fields': ('last_login',
                                                 'active_end_at', 'premium_end_at',
                                                 'ban_game_end_at', 'ban_forum_end_at',
                                                 'removed_at')}),
                 ('Additional info', {'fields': ('might',
                                                 'actual_bills')}),)

    readonly_fields = list(django_auth_admin.UserAdmin.readonly_fields) + ['referer', 'referer_domain', 'referral_of', 'referrals_number']


class ChangeCredentialsTaskAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'state', 'account', 'old_email', 'new_email')
    list_filter = ('state',)


class AwardAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account', 'type', 'created_at')
    list_filter = ('type',)


class ResetPasswordTaskAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account', 'is_processed', 'uuid', 'created_at')


django_admin.site.register(models.Account, AccountAdmin)
django_admin.site.register(models.Award, AwardAdmin)
django_admin.site.register(models.ChangeCredentialsTask, ChangeCredentialsTaskAdmin)
django_admin.site.register(models.ResetPasswordTask, ResetPasswordTaskAdmin)
