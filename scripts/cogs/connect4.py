import discord
from discord.ext import commands
import copy
import numpy as np


c4Board = [['x', 'x', 'x', 'x', 'x', 'x', 'x'],
           ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
           ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
           ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
           ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
           ['x', 'x', 'x', 'x', 'x', 'x', 'x']]

games = {}



class Connect4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.guild_only()
    @commands.command(name="connect4")
    async def init_c4(self, ctx):
        if len(ctx.message.mentions) != 1:
            await ctx.channel.send("Connect 4 requires one player to be invited.")
            return

        game = await ctx.channel.send("Setting up the board...")

        games[game] = {"player1": ctx.author,
                       "player2": ctx.message.mentions[0],
                       "playerTurn": ctx.message.mentions[0],
                       "board": copy.deepcopy(c4Board)}

        for i in range(1, 8):
            await game.add_reaction(str(i) + "\N{COMBINING ENCLOSING KEYCAP}")

        await self.update_msg(game)



    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if reaction.message in games.keys():
            game = games[reaction.message]
            if user == game["playerTurn"]:  # If it is the reactor's turn
                for position in range(0, 7):  # Iterate through number emojis
                    if reaction.emoji == str(position+1) + "\N{COMBINING ENCLOSING KEYCAP}":

                        for i in range(len(game["board"])):
                            if game["board"][5-i][position] == 'x':
                                if user == game["player1"]:
                                    game["board"][5-i][position] = '1'
                                elif user == game["player2"]:
                                    game["board"][5-i][position] = '2'
                                await self.update_msg(reaction.message)
                                break


            await reaction.message.remove_reaction(reaction, user)





    @staticmethod
    def check_win(board):
        for board in [board, np.rot90(board).tolist()]:
            for row in range(len(board)):
                for col in range(len(board[0])-3):
                    if board[row][col] != 'x' and board[row][col] == board[row][col+1] == board[row][col+2] == board[row][col+3]:
                        return True

            for row in range(len(board)-3):
                for col in range(len(board[0])-3):
                    if board[row][col] != 'x' and board[row][col] == board[row+1][col+1] == board[row+2][col+2] == board[row+3][col+3]:
                        return True

        return False



    @staticmethod
    def change_turn(game):
        if game["playerTurn"] == game["player1"]:
            game["playerTurn"] = game["player2"]

        elif game["playerTurn"] == game["player2"]:
            game["playerTurn"] = game["player1"]



    async def update_msg(self, msg):
        game = games[msg]

        key = {"1": '🟡', "2": '🔴', "x": '⬛'}
        boardStr = '\n'.join([f'[ {" ]   [ ".join(i)} ]' for i in game["board"]])
        for k in key.keys():
            boardStr = boardStr.replace(k, key[k])

        if self.check_win(game["board"]):
            await msg.edit(content=f"🔴= {game['player2'].name}, 🟡= {game['player1'].name}"
                                   f"\n{boardStr}\n {game['playerTurn'].name} wins!")
            await msg.clear_reactions()
            games.pop(msg)
        else:
            self.change_turn(game)
            await msg.edit(content=f"🔴= {game['player2'].name}, 🟡={game['player1'].name}"
                                    f"\nIt's {game['playerTurn'].name}'s turn\n" + boardStr)











async def setup(bot):
    await bot.add_cog(Connect4(bot))