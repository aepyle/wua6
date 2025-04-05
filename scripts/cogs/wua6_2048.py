import discord
from discord.ext import commands
import random
import numpy as np
import os
import re

cwd = os.path.dirname(os.path.dirname(__file__))    # /scripts/
homedir = os.path.dirname(cwd) + "/"                # ~/
games = {}

class game_2048(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.guild_only()
    @commands.command(name="2048")
    async def init_game(self, ctx):
        msg = await ctx.send("Setting up the board...")
        games[msg] = {"player": ctx.author,
                      "board": [["0", "0", "0", "0"],
                                ["0", "0", "0", "0"],
                                ["0", "0", "0", "0"],
                                ["0", "0", "0", "0"]]}

        await msg.add_reaction("⬅")
        await msg.add_reaction("➡")
        await msg.add_reaction("⬆")
        await msg.add_reaction("⬇")

        if len([x for x in await msg.guild.fetch_emojis() if x.name in ["sixteen", "thirtytwo"]]) != 2:
            with open(homedir + "/images/keycap16.png", 'rb') as img:
                img_byte = img.read()
                await msg.guild.create_custom_emoji(name="sixteen", image=img_byte)
            with open(homedir + "/images/keycap32.png", 'rb') as img:
                img_byte = img.read()
                await msg.guild.create_custom_emoji(name="thirtytwo", image=img_byte)

        self.new_tile(msg)
        self.new_tile(msg)

        await self.update_msg(msg)



    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message in games.keys():
            if user == games[reaction.message]["player"]:

                directions = {'⬅': 3, '➡': 1, '⬆': 0, '⬇': 2}

                try:
                    await self.handle_move(directions[reaction.emoji], reaction.message)
                except KeyError:
                    pass
            if not user.bot:
                await reaction.message.remove_reaction(reaction, user)



    async def update_msg(self, msg):
        sixteenEmote, thirtytwoEmote = [x for x in await msg.guild.fetch_emojis() if x.name in ["sixteen", "thirtytwo"]]
        numchars = {"0": "⬛",
                    "2": "2\N{COMBINING ENCLOSING KEYCAP}",
                    "4": "4\N{COMBINING ENCLOSING KEYCAP}",
                    "8": "8\N{COMBINING ENCLOSING KEYCAP}",
                    "16": str(sixteenEmote),
                    "32": str(thirtytwoEmote),
                    "64": "🟦",
                    "128": "🟨",
                    "256": "🟧",
                    "512": "🟥",
                    "1024": "🟫",
                    "2048": "🟩",
                    "4096": "🟪"}

        # array -> list of rows -> joined into one string (it's ugly but it works)
        board = "\n".join([' '.join(row) for row in games[msg]["board"]])
        score = sum([int(x) for x in board.split()])
        for num in numchars.keys():
            board = re.sub(r"\b{}\b".format(num), numchars[num], board)


        await msg.edit(content="🟦=64,     "
                               "🟨=128,     "
                               "🟧=256,     "
                               "🟥=512,\n"
                               "🟫=1024, "
                               "🟩=2048, "
                               "🟪=4096\n\n"
                               "Score: " + str(score) + "\n" +
                               board)



    def new_tile(self, msg):
        j = random.randint(0, 3)
        k = random.randint(0, 3)
        while games[msg]["board"][j][k] != "0":
            j = random.randint(0, 3)
            k = random.randint(0, 3)

        games[msg]["board"][j][k] = str(random.randint(1, 2) * 2)



    async def handle_move(self, direc, msg):
        games[msg]["board"] = np.rot90(games[msg]["board"], k=direc).tolist()
        self.smush(msg)
        games[msg]["board"] = np.rot90(games[msg]["board"], k=-direc).tolist()
        await self.update_msg(msg)



    def smush(self, msg):
        board = games[msg]["board"]
        hasChanged = False
        for i in range(0, 4):
            for row in range(0, 3):
                for column in range(0, 4):
                    if board[row + 1][column] != "0":
                        if i != 2:
                            if board[row][column] == "0":
                                board[row][column] = board[row + 1][column]
                                board[row + 1][column] = "0"
                                hasChanged = True
                        else:
                            if board[row + 1][column] == board[row][column]:
                                board[row][column] = str(int(board[row][column]) * 2)
                                board[row + 1][column] = "0"
                                hasChanged = True

        if hasChanged:
            self.new_tile(msg)




async def setup(bot):
    await bot.add_cog(game_2048(bot))