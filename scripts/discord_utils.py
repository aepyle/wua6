import discord
from discord.ext import commands



def member_name(user: discord.Member, order=["nick", "display_name", "name"]):
    for username in order:
        if username == "nick" and user.nick is not None:
            return user.nick
        elif username == "display_name" and user.display_name is not None:
            return user.display_name
        elif username == "name" and user.name is not None:
            return user.name
    return "Unknown"