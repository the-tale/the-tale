
import smart_imports

smart_imports.all()


class Mixin:

    @contextlib.contextmanager
    def check_discord_synced(self, accounts_ids):
        with mock.patch('the_tale.portal.logic.sync_with_discord') as sync_with_discord:
            yield

        if not isinstance(accounts_ids, set):
            accounts_ids = {accounts_ids}

        self.assertEqual(sync_with_discord.call_count, len(accounts_ids))

        self.assertEqual(accounts_ids, {call[0][0].id for call in sync_with_discord.call_args_list})
