import discord
from discord.ext import commands
from wordcloud import WordCloud
import re
import io


class Wordcloud(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def wordcloud(self, ctx):
        if len(ctx.message.content.split(" ")) >= 2:
            if ctx.message.content.split(" ")[1].isnumeric():
                message_limit = int(ctx.message.content.split(" ")[1])
            else:
                message_limit = 100
        else:
            message_limit = 100

        if message_limit > 10000:
            await ctx.channel.send("Cannot exceed 10,000 words.")
            return

        await ctx.channel.typing()

        text = ""

        async for message in ctx.channel.history(limit=message_limit+1):
            if not ctx.author.bot and message != ctx.message:
                text += message.content.lower() + ' '

        text = re.sub(r'(>.* )', '', text)
        text = re.sub(r'[^a-zA-Z0-9 \n]', '', text)

        try:
            async with ctx.channel.typing():
                arr = io.BytesIO()
                wordcloud = WordCloud().generate(text)
                image = wordcloud.to_image()
                image.save(arr, format='PNG')
                arr.seek(0)
                pic = discord.File(fp=arr, filename="wordcloud.png")
                await ctx.channel.send(file=pic)

        except ValueError:
            await ctx.channel.send("Failed to generate wordcloud")





async def setup(bot):
    await bot.add_cog(Wordcloud(bot))