import smart_imports

smart_imports.all()


class DiscordClient(tt_api_discord.Client):
    pass


discord = DiscordClient(entry_point=conf.settings.TT_DISCORD_ENTRY_POINT)
