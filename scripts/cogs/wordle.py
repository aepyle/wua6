# -*- coding: utf8 -*-

from PIL import Image, ImageDraw, ImageFont
import random
import datetime
import discord
from discord.ext import commands
import os
import io

gray = (66, 69, 73)
light_gray = (132, 138, 146)
green = (100, 170, 100)
yellow = (200, 180, 88)

cwd = os.path.dirname(os.path.dirname(__file__))
font = ImageFont.truetype(cwd + '/Whitney/whitneymedium.otf', 100)
overlay = Image.open(cwd + "/Wordle/white overlay.png")
template = Image.open(cwd + "/Wordle/wordle template.png").convert('RGBA')

answer = ''
today = datetime.datetime.now() #datetime.date.today()
games = {}

with open(cwd + "/Wordle/words.txt") as f:
    words = f.read().split(', ')
    

def new_wordle():
    global today, answer, games
    if datetime.date.today() != today or answer == '':
        print("Wordle time!")
        today = datetime.date.today()
        with open(cwd + "/Wordle/common words.txt") as f:
            commonWords = f.read().split('\n')
        rand = random.randint(0, len(commonWords))
        answer = commonWords[rand]
        games.clear()



class Wordle(commands.Cog):

    guesses = {}
    ended = False
    keyboard = {}


    def __init__(self, bot):
        self.bot = bot


    @commands.guild_only()
    @commands.command()
    async def wordle(self, ctx):
        new_wordle()
        if ctx.author in games.keys():
            if games[ctx.author]["ended"] is True:
                return

        msg = ctx.message

        games[ctx.author] = {"guesses": {},
                             "keyboard": {},
                             "ended": False,
                             "msg": msg}

        await ctx.author.send("Begin with any 5-letter word")


    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot or ctx.author not in games.keys() or not isinstance(ctx.channel, discord.DMChannel):
            return
        if games[ctx.author]["ended"] is True:
            return

        score = [light_gray, light_gray, light_gray, light_gray, light_gray]
        guess = ctx.content.lower()
        game = games[ctx.author]

        if len(guess) != 5:
            await ctx.author.send("That word is not 5 letters")
            return
        elif guess not in words:
            await ctx.author.send("That is not a real word")
            return

        letters = [*answer]
        for i in range(len(guess)):
            if guess[i] == answer[i]:
                score[i] = green
                letters[i] = ''
                game["keyboard"][guess[i]] = green
            else:
                game["keyboard"][guess[i]] = gray

        for i in range(len(guess)):
            if score[i] != green:
                if guess[i] in letters:
                    score[i] = yellow
                    letters[letters.index(guess[i])] = ''
                    game["keyboard"][guess[i]] = yellow

        game["guesses"][guess] = score

        tempCopy = template.copy()
        draw = ImageDraw.Draw(tempCopy)
        
        self.draw_keyboard(game, draw)
        self.draw_guess(game, draw)
        tempCopy.paste(overlay, (0, 800), overlay)

        arr = io.BytesIO()
        tempCopy.save(arr, format='PNG')
        arr.seek(0)

        pic = discord.File(fp=arr, filename="Wordle.png")
        await ctx.author.send(file=pic)

        if guess == answer:
            game["ended"] = True
            await ctx.author.send("You won!")
            await self.on_finish(game)
        elif len(game["guesses"]) >= 6:
            game["ended"] = True
            await ctx.author.send(f"You lost, the word was **{answer}**")
            await self.on_finish(game)



    @staticmethod
    async def on_finish(game):
        output = "Wordle " + str(today.strftime("%m/%d/%y")) + " " + str(len(game["guesses"])) + "/6\n\n"

        for guess in game["guesses"].keys():
            for letter in game["guesses"][guess]:
                if letter == yellow:
                    output += "🟨"  # Yellow Square
                elif letter == green:
                    output += "🟩"  # Green Square
                else:
                    output += "⬛"  # Gray Square

            output += "\n"
        try:
            await game["msg"].reply(output)
        except discord.HTTPException:
            await game["msg"].channel.send(output)



    @staticmethod
    def draw_keyboard(game, draw):
        for i, letter in enumerate(['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']):
            start = (25 + (i*70), 800)
            end = (start[0] + 50, 850)
            draw.rectangle((start, end), fill=game["keyboard"][letter] if letter in game["keyboard"] else light_gray)

        for i, letter in enumerate(['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']):
            start = (65 + (i*70), 865)
            end = (start[0] + 50, 915)
            draw.rectangle((start, end), fill=game["keyboard"][letter] if letter in game["keyboard"] else light_gray)

        for i, letter in enumerate(['z', 'x', 'c', 'v', 'b', 'n', 'm']):
            start = (135 + (i*70), 930)
            end = (start[0] + 50, 980)
            draw.rectangle((start, end), fill=game["keyboard"][letter] if letter in game["keyboard"] else light_gray)



    @staticmethod
    def draw_guess(game, draw):
        for row, guess in enumerate(game["guesses"].keys()):
            for col in range(len(guess)):
                start = (68 + (col * 126), 22 + (row * 126))
                end = (start[0] + 110, start[1] + 110)
                draw.rectangle((start, end), fill=game["guesses"][guess][col])

                width = font.getmask(guess[col].upper()).getbbox()[2]
                start = (125 + (124 * col) - (width / 2), 20 + (125 * row))
                draw.text(start, guess[col].upper(), font=font, fill="black")







async def setup(bot):
    await bot.add_cog(Wordle(bot))