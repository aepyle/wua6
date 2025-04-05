# -*- coding: utf8 -*-

import os
import random
import time as TIME
from datetime import datetime

import uno
import DiscordTTS

import discord
from discord.ext import commands
from gpiozero import CPUTemperature
from dotenv import load_dotenv

load_dotenv()

cwd = os.path.dirname(__file__)
dropbox = os.path.dirname(cwd) + "/"
bot_files = dropbox + "/files/"
headers = {'user-agent': 'test-app/0.0.1'}
mock = [False]

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='>', intents=intents)

NumList = ["",
           '1\N{COMBINING ENCLOSING KEYCAP}',
           '2\N{COMBINING ENCLOSING KEYCAP}',
           '3\N{COMBINING ENCLOSING KEYCAP}',
           '4\N{COMBINING ENCLOSING KEYCAP}',
           '5\N{COMBINING ENCLOSING KEYCAP}',
           '6\N{COMBINING ENCLOSING KEYCAP}',
           '7\N{COMBINING ENCLOSING KEYCAP}',
           '8\N{COMBINING ENCLOSING KEYCAP}']

Games = {"uno": {}}












# Start of Main Class

tempDate = str(datetime.now().date())


@bot.event
async def on_ready():

    print('Logged on as', bot.user)

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")




@bot.command(pass_context=True)
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()


@bot.command()
async def flip(ctx):
    coinFlip = random.randint(0, 1)
    if coinFlip == 0:
        await ctx.channel.send("Heads!")
    if coinFlip == 1:
        await ctx.channel.send("Tails!")


@bot.command()
async def dababy(ctx):
    await ctx.channel.send("👉🏾 👶🏾 👈🏾")


@bot.tree.command(name="mock")
async def slash_command(interaction):
    mock[0] = True
    interaction.response.send_message("so sneaky hehe", ephemeral=True)


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return


@bot.command()
async def temp(ctx):
    print(ctx.channel.id)
    if ctx.channel.id == 750765122821161073:
        try:
            await ctx.send(f"RPi is {CPUTemperature()} degrees")
        except Exception:
            await ctx.send("Exception occurred")





@bot.event
async def on_message(ctx):

    if ctx.author.bot:
        return

    await bot.process_commands(ctx)

    # Wua6 mocking
    if random.randint(0, 400) == 1 or mock[0]:
        if ctx.content.startswith('>') or len(ctx.content) <= 8:
            return
        caps = False
        msg = ""
        for letter in ctx.content:
            if letter == ' ':
                caps = not caps
                msg += ' '
            elif caps:
                msg += letter.upper()
            else:
                msg += letter.lower()
            caps = not caps
        mock[0] = False
        await ctx.channel.send(msg)



    if ctx.content.lower() == "i pull up":
        await ctx.channel.send(file=discord.File(bot_files + "i pull up.png"))

    if ctx.content.lower().startswith("ratato"):
        await ctx.channel.send(file=discord.File(bot_files + "ratatouille.jpg"))




    if ctx.content.startswith(">recreate "):
        previousAuthor = None
        previousImage = None
        clips = []
        texts = []
        history = ctx.content.split()[1]

        if int(history) > 250:
            await ctx.channel.send("Cannot exceed 250 messages")
        messages = [msg async for msg in ctx.channel.history(limit=int(history) + 1)]

        start = TIME.time()
        await ctx.channel.typing()

        for msg in reversed(messages[1:]):
        #async for msg in ctx.channel.history(limit=int(history) + 1, oldest_first=True):
            if len(msg.clean_content) == 0:
                continue
            content = msg.clean_content
            username = msg.author.nick
            pfp = msg.author.avatar.url#(format="png", size=4096).read()
            name_color = msg.author.color.to_rgb()
            if name_color == (0, 0, 0):
                name_color = (255, 255, 255)
            time = msg.created_at

            if username is None:
                username = msg.author.display_name
            if not username.isalnum():
                username = msg.author.name
            #for char in username:
            #    if char not in list(string.printable):
            #        username = msg.author.name
            #        break

            if previousAuthor == msg.author:
                img = DiscordTTS.DrawMessage(content, username, pfp, name_color, time, previousImage).output
            else:
                img = DiscordTTS.DrawMessage(content, username, pfp, name_color, time).output

            previousAuthor = msg.author
            previousImage = img

            #texts.insert(0, content)
            #clips.insert(0, img)
            texts.append(content)
            clips.append(img)

        texts = [text.replace('>', '') for text in texts]
        if len(texts) == 0:
            return

        tts = DiscordTTS.MakeVideo(clips)
        output = tts.add_tts_sound(texts)

        output.write_videofile(cwd + "/images/output.mp4", fps=5, logger=None, preset="medium")
        finalVid = cwd + "/images/output.mp4"
        finalVidSize = os.stat(finalVid).st_size
        print("Successfully finished video of size", str(finalVidSize/1048576.0), "MB after", (TIME.time()-start), "seconds and", history, "messages")

        if finalVidSize > 8388608:
            await ctx.channel.send("Final video was too large ({:.2f} MB), try inputting fewer messages".format(finalVidSize / 1048576.0))
        else:
            await ctx.channel.send(file=discord.File(finalVid))






    if ctx.content.lower().startswith('>uno'):

        if "uno" in ctx.content.lower() and ctx.guild:
            players = ctx.mentions
            players.insert(0, ctx.author)

            for player in players:
                for game in Games["uno"]:
                    print("Game", game, "and player", player.name)
                    if player in Games["uno"][game]["players"]:
                        await ctx.channel.send(player.name + ' is already in an Uno game, they have to send "Leave" to wua6.')
                        return



            game = uno.Uno(players)
            Games["uno"].update({ctx.id:
                                          {"gameObject": game,
                                              "players": game.players,
                                            "messageID": ctx.id}})

            for i in range(0, len(players)):
                game.Display2(currentPlayer=i).save("unoBoard.png")
                pic = discord.File("unoBoard.png")

                await game.players[i].send("Type the color and then value of the card you want to send (e.g. 'green 5' or 'yellow +2')\n"
                                           "For +4 and wild cards, type the card and then the color (e.g. 'wild blue' or '+4 red')\n"
                                           "+2 cards and +4 cards can be stacked, but you cannot stack a +2 on a +4 and vice versa\n"
                                           "If you cannot play a card or are forced to draw, type 'draw'\n"
                                           "If you wish to leave a game, type 'leave'")
                await game.players[i].send(file=pic)




    if not ctx.guild:
        for key in Games["uno"]:
            if ctx.author in Games["uno"][key]["players"]:

                players = Games["uno"][key]["players"]
                game = Games["uno"][key]["gameObject"]

                if "leave" in ctx.content.lower():
                    players.remove(ctx.author)
                    await ctx.author.send("You left the game.")

                    if len(players) == 1:
                        await players[0].send("You've won! Everybody forfeited.")
                        del Games["uno"][key]
                        return

                    if game.playerTurn >= len(players):
                        game.playerTurn = 0

                        for i in range(0, len(players)):

                            game.Display2(currentPlayer=i).save("unoBoard.png")
                            pic = discord.File("unoBoard.png")
                            playerTurn = game.playerTurn

                            await game.players[i].send(file=pic)
                            await game.players[i].send(ctx.author.name + " has left the game.")
                            if i == playerTurn:
                                await game.players[i].send("Your turn!")

                        return



                players = Games["uno"][key]["players"]
                game = Games["uno"][key]["gameObject"]
                playerTurn = game.playerTurn

                if ctx.author != players[game.playerTurn]:
                    await ctx.author.send("Not your turn.")
                    return

                playCard = game.PlayCard(ctx.content)

                if playCard == "success":
                    if game.SumOfCards(playerTurn) == 0:
                        for i in range(0, len(players)):

                            game.Display2(currentPlayer=i).save("unoBoard.png")
                            pic = discord.File("unoBoard.png")

                            await game.players[i].send(file=pic)
                            await game.players[i].send(ctx.author.name + " won!")


                        del Games["uno"][key]
                        return


                elif playCard == "You got skipped":
                    await ctx.channel.send("You got skipped")

                else:
                    await ctx.channel.send(playCard)
                    game.Display2(currentPlayer=game.playerTurn).save("unoBoard.png")
                    pic = discord.File("unoBoard.png")

                    await game.players[game.playerTurn].send(file=pic)
                    await game.players[game.playerTurn].send("Your turn!")

                    return


                for i in range(0, len(players)):
                    game.Display2(currentPlayer=i).save("unoBoard.png")
                    pic = discord.File("unoBoard.png")
                    playerTurn = game.playerTurn

                    try:
                        await game.players[i].send(file=pic)
                        if i == playerTurn:
                            await game.players[i].send("Your turn!")
                    except discord.errors.HTTPException:
                        print("Error: Cannot send empty message")
                        print(pic.fp)
                    except AttributeError:
                        print("Cannot send message to {}, user cannot receive DMs".format(game.players[i].name))




    if ctx.content.lower().startswith('>what would ') and ' say' in ctx.content.lower():

        currentChannel = ctx.channel

        specifiedUser = ctx.content[12:-4].lower()
        quotesList = []

        f = open(dropbox + "/quotes.txt", "r", encoding="utf8")
        AllQuotesRaw = f.read()
        AllQuotes = AllQuotesRaw.split("<=>")

        for ctx in AllQuotes:
            if ("-" + specifiedUser) in ctx.lower() or (specifiedUser + ":") in ctx.lower() or (
                    "- " + specifiedUser) in ctx.lower():
                quotesList.append(ctx)

        quotesListLen = len(quotesList)

        if quotesListLen == 0:
            await currentChannel.send("Found no quotes attributed to that name")
            return

        randomQuote = random.randint(0, quotesListLen - 1)

        quote = quotesList[randomQuote]

        await currentChannel.send(quote)



bot.run(os.getenv("DISCORD_TOKEN"))
#client = commands.Bot(command_prefix='>', intents=intents)
