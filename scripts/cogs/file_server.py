import discord
from discord.ext import commands
import os
import random
import re
import requests



cwd = os.path.dirname(os.path.dirname(__file__))
dropbox = os.path.dirname(cwd) + "/"
bot_files = dropbox + "/wua6 files/"
headers = {'user-agent': 'test-app/0.0.1'}



class FileServer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if not user.bot and reaction.message.author == self.bot.user and reaction.message.content.startswith("__Page "):
            fileList = os.listdir(bot_files)
            pageNum = int(reaction.message.content.split()[1]) - 1
            maxPageNum = int(len(fileList) / 25) + 1

            if reaction.emoji == '⬅️' and pageNum > 0:
                pageNum -= 1
                await reaction.message.edit(
                    content="__Page " + str(pageNum + 1) + " of " + str(maxPageNum) + "__\n" + "\n".join(
                        fileList[pageNum * 25:pageNum * 25 + 25]))
            if reaction.emoji == '➡️' and pageNum < maxPageNum - 1:
                pageNum += 1
                await reaction.message.edit(
                    content="__Page " + str(pageNum + 1) + " of " + str(maxPageNum) + "__\n" + "\n".join(
                        fileList[pageNum * 25:pageNum * 25 + 25]))

            await reaction.message.remove_reaction(reaction, user)


    @commands.command()
    async def save(self, ctx):
        # If ctx has no attachments, quit
        if len(ctx.message.attachments) == 0:
            await ctx.send("Attachment required")
            return

        # Save title as newTitle
        newTitle = ctx.message.content[6:]
        filename = ctx.message.attachments[0].filename
        fileExtension = ctx.message.attachments[0].filename.split('.')[-1]

        # If title is less than 2 or over 32 chars, quit
        if len(newTitle) < 2 or len(newTitle) > 32:
            await ctx.send("File title must be between 2 and 32 characters")
            return

        # If title has invalid chars, quit
        if re.search("[/:*?<>|]", newTitle):
            await ctx.send("File title cannot contain characters \\,/,<,>,?,\",:,*, or |")
            return

        # If file of the same name exists, quit
        for file in os.listdir(bot_files):
            if os.path.splitext(file)[0] == newTitle:
                await ctx.send("Another file of the same name already exists")
                return

        # Remove whitespace
        newTitle = newTitle.strip()

        # Save attachment to homedir
        r = requests.get(ctx.message.attachments[0].url, headers=headers)

        with open(bot_files + newTitle + '.' + fileExtension, 'wb') as f:
            f.write(r.content)
            print("Saved", filename, "as", newTitle)
            await ctx.send("Successfully saved file")
            return


    @commands.command()
    async def send(self, ctx):
        if ctx.message.content.lower() == '>send':
            randFileInt = random.randint(0, len(os.listdir(bot_files))-1)
            await ctx.send(file=discord.File(bot_files + os.listdir(bot_files)[randFileInt]))
            return


        # Isolate requested file name from command
        requestedFile = ctx.message.content[6:]

        # Iterate through every file in homedir to find file
        for file in os.listdir(bot_files):
            if os.path.splitext(file)[0].lower() == requestedFile.lower():
                await ctx.send(file=discord.File(bot_files + file))
                return
        await ctx.send("No file of that name was found")


    @commands.command()
    async def list(self, ctx):
        # Iterate through every file in homedir and append to list
        fileList = os.listdir(bot_files)

        # If file(s) found, send them. Otherwise, quit
        if len(fileList) > 0:
            msg = await ctx.send(
                "__Page 1 of " + str(int(len(os.listdir(bot_files)) / 25) + 1) + "__\n" + "\n".join(fileList[0:25]))
            await msg.add_reaction("⬅️")
            await msg.add_reaction("➡️")
        else:
            await ctx.send("No files yet!")


    @commands.command()
    async def search(self, ctx):
        # Get search keyword
        fileList = ''
        keyword = ctx.message.content[8:].lower()

        # Iterate through every file in homedir and append to list
        for file in os.listdir(bot_files):
            if keyword in os.path.splitext(file)[0].lower():
                fileList = fileList + file + '\n'

        # If file(s) found, send them. Otherwise, quit
        if len(fileList) > 0:
            await ctx.message.channel.send(fileList)
        else:
            await ctx.message.channel.send("No files found with that keyword")
            return





async def setup(bot):
    await bot.add_cog(FileServer(bot))