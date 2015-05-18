# coding: utf-8

from django.core.management.base import BaseCommand

from dext.common.utils.logic import run_django_command


MIGRATIONS = [
	'contenttypes.0001_initial',
    # 'accounts.0001_initial',
	# 'forum.0001_initial',
	# 'clans.0001_initial',
	'auth.0001_initial',
	# 'accounts.0002_auto_20150504_0841',
	'accounts.0003_auto_20150506_1406',
	# 'collections.0001_initial',
	# 'achievements.0001_initial',
	'achievements.0002_auto_20150506_1406',
	# 'heroes.0001_initial',
	# 'actions.0001_initial',
	'actions.0002_metaactionmember_hero',
	'admin.0001_initial',
	'mobs.0001_initial',
	'artifacts.0001_initial',
	'contenttypes.0002_remove_content_type_name',
	# 'auth.0002_alter_permission_name_max_length',
	# 'auth.0003_alter_user_email_max_length',
	# 'auth.0004_alter_user_username_opts',
	# 'auth.0005_alter_user_last_login_null',
	# 'auth.0006_require_contenttypes_0002',
	'bank.0001_initial',
	# 'persons.0001_initial',
	# 'bills.0001_initial',
	# 'places.0001_initial',
	'bills.0002_actor_place',
	'blogs.0001_initial',
	# 'chronicle.0001_initial',
	'chronicle.0002_auto_20150504_0841',
	'clans.0002_auto_20150506_1406',
	'cms.0001_initial',
	'collections.0002_auto_20150506_1406',
	'companions.0001_initial',
	'forum.0002_auto_20150506_1406',
	'friends.0001_initial',
	'game.0001_initial',
	'roads.0001_initial',
	# 'heroes.0002_auto_20150504_0841',
	'heroes.0003_auto_20150506_1406',
	# 'linguistics.0001_initial',
	'linguistics.0002_auto_20150506_1406',
	# 'map.0001_initial',
	'map.0002_auto_20150506_1406',
	'market.0001_initial',
	'news.0001_initial',
	'personal_messages.0001_initial',
	# 'persons.0002_person_place',
	'persons.0003_auto_20150506_1406',
	'places.0002_auto_20150506_1406',
	'post_service.0001_initial',
	'postponed_tasks.0001_initial',
	# 'pvp.0001_initial',
	'pvp.0002_auto_20150506_1406',
	'ratings.0001_initial',
	'sessions.0001_initial',
	'settings.0001_initial',
	'statistics.0001_initial',
	# 'xsolla.0001_initial',
	'xsolla.0002_auto_20150506_1406' ]



class Command(BaseCommand):

    help = 'make fake initials migrations'

    def handle(self, *args, **options):
        for migration in MIGRATIONS:
            app_name, migration_name = migration.split('.')
            if migration_name.startswith('0001'):
                run_django_command(['migrate', '--fake-initial', app_name])
            else:
                run_django_command(['migrate', '--fake', app_name, migration_name])
