
import smart_imports

smart_imports.all()


class SupervisorTaskAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'created_at')


class SupervisorTaskMemberAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'task', 'account')


django_admin.site.register(models.SupervisorTask, SupervisorTaskAdmin)
django_admin.site.register(models.SupervisorTaskMember, SupervisorTaskMemberAdmin)
